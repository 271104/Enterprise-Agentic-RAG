"""FastAPI application for the Agentic RAG service."""

from contextlib import asynccontextmanager
import re
from uuid import uuid4

import logfire
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field

from app.config import settings
from app.agents.graph import rag_agent


def initialize_rails() -> None:
    from app.guardrails.rails import initialize_rails as initialize

    initialize()


def guard(message: str):
    from app.guardrails.rails import guard as check

    return check(message)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize service integrations once and close clients on shutdown."""
    settings.validate_runtime()
    logfire.configure(token=settings.logfire_token)
    initialize_rails()
    try:
        yield
    finally:
        from app.services.retrieval.qdrant_service import close_qdrant_client

        close_qdrant_client()


app = FastAPI(title="Enterprise Agentic RAG API", lifespan=lifespan)
MAX_REQUEST_BYTES = 64 * 1024


class RequestBoundaryMiddleware:
    """Bound buffered request bodies and attach a sanitized request ID."""

    def __init__(self, app, max_bytes: int):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = {key.lower(): value for key, value in scope.get("headers", [])}
        supplied_id = headers.get(b"x-request-id", b"").decode("latin-1")
        request_id = (
            supplied_id
            if re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", supplied_id)
            else str(uuid4())
        )
        scope.setdefault("state", {})["request_id"] = request_id

        async def send_with_request_id(message):
            if message["type"] == "http.response.start":
                response_headers = list(message.get("headers", []))
                response_headers.append((b"x-request-id", request_id.encode("ascii")))
                message["headers"] = response_headers
            await send(message)

        content_length = headers.get(b"content-length", b"")
        if content_length.isdigit() and int(content_length) > self.max_bytes:
            await self._too_large(send_with_request_id)
            return

        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            body.extend(message.get("body", b""))
            if len(body) > self.max_bytes:
                await self._too_large(send_with_request_id)
                return
            if not message.get("more_body", False):
                break

        replayed = False

        async def replay_body():
            nonlocal replayed
            if replayed:
                return {"type": "http.disconnect"}
            replayed = True
            return {"type": "http.request", "body": bytes(body), "more_body": False}

        await self.app(scope, replay_body, send_with_request_id)

    async def _too_large(self, send):
        payload = b'{"detail":"Request body exceeds the 64 KiB limit."}'
        await send(
            {
                "type": "http.response.start",
                "status": 413,
                "headers":[
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(payload)).encode("ascii")),
                ],
            }
        )
        await send({"type": "http.response.body", "body": payload})


app.add_middleware(RequestBoundaryMiddleware, max_bytes=MAX_REQUEST_BYTES)


class QueryRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    q: str = Field(min_length=1, max_length=8000)
    thread_id: str | None = Field(default=None, min_length=1, max_length=128)


class QueryResponse(BaseModel):
    question: str
    answer: str
    thought_process: list[str]
    status: str
    sources: list[str]
    request_id: str


@app.get("/", include_in_schema=False)
def home():
    return {"message": "Enterprise Agentic RAG API is live."}


@app.get("/health/live")
def liveness():
    return {"status": "ok"}


@app.get("/health/ready")
def readiness():
    try:
        settings.validate_runtime()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Service configuration incomplete") from exc
    return {"status": "ready"}


@app.get("/graph")
def get_graph_image():
    try:
        png_bytes = rag_agent.get_graph().draw_mermaid_png()
    except Exception as exc:
        logfire.error("Graph rendering failed", error_type=type(exc).__name__)
        raise HTTPException(status_code=503, detail="Graph image unavailable") from exc
    return Response(content=png_bytes, media_type="image/png")


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest, http_request: Request):
    """Run guardrails and the RAG graph for one isolated conversation session."""
    q = request.q
    thread_id = request.thread_id or str(uuid4())
    request_id = http_request.state.request_id

    try:
        rail_fired, rail_response = guard(q)
        if rail_fired:
            logfire.info("Request blocked by guardrails", request_id=request_id)
            return QueryResponse(
                question=q,
                answer=rail_response or "This request could not be processed.",
                thought_process=["Intent: Guardrails Fired", "Retrieval: Skipped"],
                status="Blocked by guardrails.",
                sources=[],
                request_id=request_id,
            )

        initial_state = {
            "messages": [{"role": "user", "content": q}],
            "current_query": q,
            "documents": [],
            "plan": ["Start"],
            "status": "Initializing graph...",
        }
        final_output = rag_agent.invoke(
            initial_state,
            config={"configurable": {"thread_id": thread_id}},
        )
        return QueryResponse(
            question=q,
            answer=final_output.get("final_answer") or "No response was generated.",
            thought_process=final_output.get("plan") or [],
            status=final_output.get("status") or "Response generated.",
            sources=final_output.get("documents") or [],
            request_id=request_id,
        )
    except Exception as exc:
        logfire.error(
            "Backend request failed",
            request_id=request_id,
            error_type=type(exc).__name__,
        )
        raise HTTPException(
            status_code=502,
            detail="The request could not be completed. Please try again later.",
        ) from exc

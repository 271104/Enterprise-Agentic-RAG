"""Text embeddings with an explicit, collection-compatible provider choice."""

import time

import logfire

from app.config import settings

BATCH_SIZE = 50
_DIMENSIONS = {"gemini": 3072, "local": 768}
_active_model = None


def _init():
    global _active_model
    if _active_model is not None:
        return _active_model
    provider = settings.embedding_provider
    if provider not in _DIMENSIONS:
        raise ValueError("EMBEDDING_PROVIDER must be 'gemini' or 'local'")

    if provider == "gemini":
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is required when EMBEDDING_PROVIDER=gemini")
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        _active_model = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-2-preview",
            google_api_key=settings.gemini_api_key,
        )
    else:
        from sentence_transformers import SentenceTransformer

        _active_model = SentenceTransformer("all-mpnet-base-v2")
    logfire.info("Embedding provider initialized", provider=provider)
    return _active_model


def get_embedding_dim() -> int:
    """Return the configured vector dimension without making a network call."""
    try:
        return _DIMENSIONS[settings.embedding_provider]
    except KeyError as exc:
        raise ValueError("EMBEDDING_PROVIDER must be 'gemini' or 'local'") from exc


def _embed_batch(batch: list[str]) -> list[list[float]]:
    model = _init()
    if settings.embedding_provider == "local":
        return model.encode(batch, show_progress_bar=False).tolist()

    for attempt in range(4):
        try:
            return model.embed_documents(batch)
        except Exception as exc:
            message = str(exc).lower()
            retryable = any(
                marker in message
                for marker in ("429", "rate", "quota", "resource_exhausted")
            )
            if not retryable or attempt == 3:
                raise
            delay = 2**attempt
            logfire.warning("Embedding rate limit; retrying", delay_seconds=delay)
            time.sleep(delay)
    raise RuntimeError("Embedding retry limit exceeded")


def embed_query(query: str) -> list[float]:
    model = _init()
    if settings.embedding_provider == "local":
        return model.encode([query])[0].tolist()
    return model.embed_query(query)


def embed_texts(texts: list[str]) -> list[list[float]]:
    _init()
    vectors: list[list[float]] = []
    for start in range(0, len(texts), BATCH_SIZE):
        with logfire.span(
            "Embed batch", provider=settings.embedding_provider, start=start
        ):
            vectors.extend(_embed_batch(texts[start : start + BATCH_SIZE]))
    return vectors

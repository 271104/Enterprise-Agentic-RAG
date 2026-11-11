# Deployment

## Container

```sh
docker build -t enterprise-agentic-rag .
docker run --rm -p 8080:8080 \
  -e QDRANT_CLUSTER_ENDPOINT="$QDRANT_CLUSTER_ENDPOINT" \
  -e QDRANT_API_KEY="$QDRANT_API_KEY" \
  -e PORTKEY_API_KEY="$PORTKEY_API_KEY" \
  -e GROQ_API_KEY="$GROQ_API_KEY" \
  -e GEMINI_API_KEY="$GEMINI_API_KEY" \
  enterprise-agentic-rag
```

The image includes the FastAPI service only, runs as a non-root account, and checks `/health/live`. The UI and ingestion/evaluation workflows are not included. Provide secret values through the platform’s secret manager, never image build args or source control.

## Operational requirements

Provision a Qdrant collection using the same embedding provider and dimension as the API. The container supports `EMBEDDING_PROVIDER=gemini` (3072 dimensions); local sentence-transformer embeddings require the full local dependency set and are not included in the runtime image. Configure a Qdrant endpoint, Portkey key, Groq key, and Gemini key before startup. Logfire and LangSmith are optional. Set `LANGSMITH_TRACING=false` unless tracing is intended and approved for the data involved.

The API currently uses process-local LangGraph memory. Run one worker for predictable session behavior; restarts clear memory. Multiple replicas do not share conversations. No production deployment topology or availability target has been validated by this repository.

Graceful process termination is delegated to Uvicorn and the container runtime. Provider availability is not checked by the readiness endpoint.

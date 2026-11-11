"""Qdrant vector search service."""

from functools import lru_cache

from qdrant_client import QdrantClient

from app.config import settings
from app.services.retrieval.embedding import embed_query


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    """Create a process-scoped Qdrant client with a finite request timeout."""
    if not settings.qdrant_url:
        raise RuntimeError("QDRANT_CLUSTER_ENDPOINT is required for retrieval")
    return QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        timeout=10,
    )


def close_qdrant_client() -> None:
    """Close the client at application shutdown when it was initialized."""
    if get_qdrant_client.cache_info().currsize:
        get_qdrant_client().close()
        get_qdrant_client.cache_clear()


def search_enterprise_knowledge(query: str, limit: int = 8) -> list[dict]:
    """Embed a query and return matching text and source metadata."""
    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")
    response = get_qdrant_client().query_points(
        collection_name=settings.qdrant_collection,
        query=embed_query(query),
        limit=limit,
        with_payload=True,
    )
    results = []
    for point in response.points:
        payload = point.payload or {}
        results.append(
            {
                "content": payload.get("text", ""),
                "source": payload.get("source", "Unknown"),
                "score": point.score,
            }
        )
    return results

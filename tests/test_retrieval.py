from app.services.retrieval import qdrant_service


def test_qdrant_search_shapes_payload(monkeypatch):
    class FakeClient:
        def query_points(self, **_kwargs):
            point = type("Point", (), {"payload": {"text": "doc", "source": "file"}, "score": 0.8})()
            return type("Result", (), {"points": [point]})()

    monkeypatch.setattr(qdrant_service, "get_qdrant_client", lambda: FakeClient())
    monkeypatch.setattr(qdrant_service, "embed_query", lambda _: [0.1, 0.2])
    assert qdrant_service.search_enterprise_knowledge("query") == [
        {"content": "doc", "source": "file", "score": 0.8}
    ]


def test_qdrant_search_rejects_bad_limit():
    import pytest

    with pytest.raises(ValueError):
        qdrant_service.search_enterprise_knowledge("query", limit=0)

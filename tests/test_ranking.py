from app.services.retrieval import ranking_service


def test_reranker_falls_back_to_original_order(monkeypatch):
    monkeypatch.setattr(
        ranking_service,
        "_get_ranker",
        lambda: (_ for _ in ()).throw(RuntimeError("model unavailable")),
    )
    assert ranking_service.rerank_documents("q", ["a", "b", "c"], top_n=2) == ["a", "b"]


def test_reranker_handles_empty_input():
    assert ranking_service.rerank_documents("q", [], top_n=2) == []

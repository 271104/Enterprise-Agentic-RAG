from app.agents.nodes import planner, responder, retriever


class FakeLLM:
    def __init__(self, content):
        self.content = content

    def invoke(self, _prompt):
        return type("Result", (), {"content": self.content})()


def test_planner_classifies_conversation(monkeypatch):
    monkeypatch.setattr(planner, "_llm", FakeLLM("CONVERSATIONAL"))
    result = planner.planner_node({"messages": [{"role": "user", "content": "hi"}]})
    assert result["current_query"] == "CONVERSATIONAL"


def test_planner_uses_search_query(monkeypatch):
    monkeypatch.setattr(planner, "_llm", FakeLLM("kubernetes autoscaling"))
    result = planner.planner_node({"messages": [{"role": "user", "content": "autoscale"}]})
    assert result["current_query"] == "kubernetes autoscaling"


def test_retriever_searches_and_reranks(monkeypatch):
    monkeypatch.setattr(
        retriever,
        "search_enterprise_knowledge",
        lambda _query, limit: [{"content": "chunk", "source": "doc", "score": 0.9}],
    )
    monkeypatch.setattr(retriever, "rerank_documents", lambda _q, docs, top_n: docs[:top_n])
    result = retriever.retrieve_node(
        {"current_query": "q", "plan": [], "documents": [], "messages": []}
    )
    assert result["documents"] == ["CONTENT: chunk"]


def test_responder_returns_answer(monkeypatch):
    class FakeCompletions:
        def create(self, **_kwargs):
            message = type("Message", (), {"content": "answer"})()
            choice = type("Choice", (), {"message": message})()
            return type("Response", (), {"choices": [choice]})()

    fake_client = type("Client", (), {"chat": type("Chat", (), {"completions": FakeCompletions()})()})()
    monkeypatch.setattr(responder, "portkey_client", fake_client)
    monkeypatch.setattr(responder, "extract_cache_status", lambda _: "MISS")
    result = responder.generate_node(
        {"current_query": "CONVERSATIONAL", "messages": [{"role": "user", "content": "hi"}], "documents": [], "plan": []}
    )
    assert result["final_answer"] == "answer"

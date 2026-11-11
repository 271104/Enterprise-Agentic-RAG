from fastapi.testclient import TestClient
import pytest

from app import main


@pytest.fixture(autouse=True)
def isolated_app_runtime(monkeypatch):
    monkeypatch.setattr(type(main.settings), "validate_runtime", lambda self: None)
    monkeypatch.setattr(main, "initialize_rails", lambda: None)
    monkeypatch.setattr(main, "guard", lambda _: (False, None))
    monkeypatch.setattr(main.logfire, "configure", lambda **_: None)


class FakeAgent:
    def __init__(self):
        self.thread_ids = []

    def invoke(self, state, config):
        self.thread_ids.append(config["configurable"]["thread_id"])
        return {
            "final_answer": "ok",
            "plan": ["test"],
            "status": "Response generated.",
            "documents": [],
        }


def test_query_allocates_distinct_sessions(monkeypatch):
    fake_agent = FakeAgent()
    monkeypatch.setattr(main, "rag_agent", fake_agent)

    with TestClient(main.app) as client:
        first = client.post("/query", json={"q": "one"})
        second = client.post("/query", json={"q": "two"})

    assert first.status_code == 200
    assert second.status_code == 200
    assert fake_agent.thread_ids[0] != fake_agent.thread_ids[1]
    assert first.json()["request_id"]


def test_query_rejects_oversized_input():
    with TestClient(main.app) as client:
        response = client.post("/query", json={"q": "x" * 8001})
    assert response.status_code == 422


def test_query_rejects_oversized_body():
    with TestClient(main.app) as client:
        response = client.post("/query", json={"q": "ok", "extra": "x" * (65 * 1024)})
    assert response.status_code == 413


def test_api_failure_does_not_return_internal_exception(monkeypatch):
    monkeypatch.setattr(main.logfire, "error", lambda *_args, **_kwargs: None)
    class BrokenAgent:
        def invoke(self, *_args, **_kwargs):
            raise RuntimeError("sensitive upstream detail")

    monkeypatch.setattr(main, "rag_agent", BrokenAgent())
    with TestClient(main.app) as client:
        response = client.post("/query", json={"q": "hello"})
    assert response.status_code == 502
    assert "sensitive upstream detail" not in response.text

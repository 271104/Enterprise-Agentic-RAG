from app.guardrails import rails


def test_guardrails_returns_canned_block(monkeypatch):
    class FakeRails:
        def generate(self, **_kwargs):
            return {"role": "assistant", "content": rails.RAIL_INDICATORS[0]}

    monkeypatch.setattr(rails, "_rails", FakeRails())
    fired, response = rails.guard("off topic")
    assert fired is True
    assert response == rails.RAIL_INDICATORS[0]


def test_guardrails_passes_regular_message(monkeypatch):
    class FakeRails:
        def generate(self, **_kwargs):
            return {"role": "assistant", "content": "normal response"}

    monkeypatch.setattr(rails, "_rails", FakeRails())
    assert rails.guard("technical question") == (False, None)

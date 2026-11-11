from app.gateway.client import GATEWAY_CONFIG


def test_gateway_config_has_primary_fallback_and_retries():
    assert GATEWAY_CONFIG["strategy"]["mode"] == "fallback"
    assert len(GATEWAY_CONFIG["targets"]) == 2
    assert GATEWAY_CONFIG["retry"]["attempts"] >= 1
    assert 429 in GATEWAY_CONFIG["retry"]["on_status_codes"]

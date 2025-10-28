from unittest.mock import patch
from agents.client.api import dmaas_latest

class _DummyResponse:
    def __init__(self, payload): self._p = payload
    def json(self): return self._p
    def raise_for_status(self): return None

@patch("httpx.Client.get")
def test_dmaas_latest_returns_json(mock_get):
    mock_get.return_value = _DummyResponse({"measurements": [{"name": "waist", "value": 30}]})
    data = dmaas_latest()
    assert "measurements" in data
    assert isinstance(data["measurements"], list)

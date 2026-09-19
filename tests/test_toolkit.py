import json

import httpx
import pytest

from langchain_twelvedata import TwelveDataAPIError, TwelveDataClient, TwelveDataToolkit


def test_tools_call_expected_endpoints(monkeypatch):
    monkeypatch.setenv("TWELVE_DATA_API_KEY", "test-key")
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(200, json={"endpoint": request.url.path})

    with httpx.Client(transport=httpx.MockTransport(respond)) as http_client:
        tools = {
            tool.name: tool
            for tool in TwelveDataToolkit(
                TwelveDataClient(http_client=http_client)
            ).get_tools()
        }
        examples = {
            "twelvedata_quote": {"symbol": "AAPL"},
            "twelvedata_time_series": {"symbol": "AAPL", "interval": "1day"},
            "twelvedata_symbol_search": {"query": "Apple"},
            "twelvedata_rsi": {"symbol": "AAPL"},
        }
        for name, args in examples.items():
            assert json.loads(tools[name].invoke(args))["endpoint"]

    assert [request.url.path for request in requests] == [
        "/quote",
        "/time_series",
        "/symbol_search",
        "/rsi",
    ]
    assert all(
        request.headers["Authorization"] == "apikey test-key" for request in requests
    )
    assert requests[1].url.params["outputsize"] == "5"
    assert requests[2].url.params["symbol"] == "Apple"
    assert requests[3].url.params["time_period"] == "14"
    assert "apikey" not in str(requests[0].url)


def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("TWELVE_DATA_API_KEY", raising=False)
    with pytest.raises(ValueError, match="TWELVE_DATA_API_KEY"):
        TwelveDataClient()


def test_api_error_is_not_returned_as_market_data():
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            400, json={"status": "error", "code": 400, "message": "Bad symbol"}
        )
    )
    with httpx.Client(transport=transport) as http_client:
        client = TwelveDataClient(api_key="test-key", http_client=http_client)
        with pytest.raises(TwelveDataAPIError, match="Bad symbol"):
            client.get("quote", symbol="BAD")


def test_outputsize_validation():
    toolkit = TwelveDataToolkit(TwelveDataClient(api_key="test-key"))
    history = next(
        tool for tool in toolkit.get_tools() if tool.name == "twelvedata_time_series"
    )
    with pytest.raises(ValueError):
        history.invoke({"symbol": "AAPL", "outputsize": 0})

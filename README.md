# langchain-twelvedata

LangChain tools for [Twelve Data](https://twelvedata.com/) market data. The
toolkit makes four read-only REST endpoints available to an agent: quote,
historical time series, symbol search, and Relative Strength Index (RSI).

## Install

```bash
pip install langchain-twelvedata
```

Before the PyPI release, install from a clone:

```bash
git clone https://github.com/MazeBraker/langchain-twelvedata.git
cd langchain-twelvedata
pip install .
```

## Quick start

Set a [Twelve Data API key](https://twelvedata.com/) in your environment:

```bash
export TWELVE_DATA_API_KEY="your-api-key"
```

Invoke a tool directly:

```python
import json

from langchain_twelvedata import TwelveDataToolkit

tools = TwelveDataToolkit().get_tools()
quote = next(tool for tool in tools if tool.name == "twelvedata_quote")
data = json.loads(quote.invoke({"symbol": "AAPL"}))
print(data["close"])
```

Pass the same `tools` list to a LangChain agent or a tool-calling model. Each
tool returns a JSON string containing the Twelve Data response. For example:

```python
history = next(tool for tool in tools if tool.name == "twelvedata_time_series")
print(history.invoke({"symbol": "AAPL", "interval": "1day", "outputsize": 5}))
```

The API key can also be passed explicitly with
`TwelveDataToolkit(TwelveDataClient(api_key="..."))` after importing
`TwelveDataClient` from `langchain_twelvedata`. Twelve Data API errors and HTTP
errors are raised to the caller.

## Development

```bash
pip install -e '.[test]'
pytest
```

## License

MIT

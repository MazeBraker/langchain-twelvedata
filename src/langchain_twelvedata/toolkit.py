"""LangChain tools for common Twelve Data endpoints."""

from __future__ import annotations

import json
from typing import Annotated

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import Field

from langchain_twelvedata.client import TwelveDataClient

OutputSize = Annotated[int, Field(ge=1, le=5000)]
TimePeriod = Annotated[int, Field(ge=1, le=800)]


class TwelveDataToolkit:
    """Expose quote, time series, symbol search, and RSI as LangChain tools."""

    def __init__(self, client: TwelveDataClient | None = None) -> None:
        self.client = client or TwelveDataClient()

    def get_quote(self, symbol: str) -> str:
        """Get the latest full market quote for a ticker such as AAPL."""
        return json.dumps(self.client.get("quote", symbol=symbol))

    def get_time_series(
        self, symbol: str, interval: str = "1day", outputsize: OutputSize = 5
    ) -> str:
        """Get historical OHLC market prices for a symbol and interval."""
        return json.dumps(
            self.client.get(
                "time_series", symbol=symbol, interval=interval, outputsize=outputsize
            )
        )

    def search_symbol(self, query: str, outputsize: OutputSize = 10) -> str:
        """Find ticker symbols by company name or partial ticker."""
        return json.dumps(
            self.client.get("symbol_search", symbol=query, outputsize=outputsize)
        )

    def get_rsi(
        self,
        symbol: str,
        interval: str = "1day",
        time_period: TimePeriod = 14,
        outputsize: OutputSize = 5,
    ) -> str:
        """Get Relative Strength Index (RSI) values for a market symbol."""
        return json.dumps(
            self.client.get(
                "rsi",
                symbol=symbol,
                interval=interval,
                time_period=time_period,
                outputsize=outputsize,
            )
        )

    def get_tools(self) -> list[BaseTool]:
        """Return four tools suitable for a LangChain agent."""
        return [
            StructuredTool.from_function(func=self.get_quote, name="twelvedata_quote"),
            StructuredTool.from_function(
                func=self.get_time_series, name="twelvedata_time_series"
            ),
            StructuredTool.from_function(
                func=self.search_symbol, name="twelvedata_symbol_search"
            ),
            StructuredTool.from_function(func=self.get_rsi, name="twelvedata_rsi"),
        ]

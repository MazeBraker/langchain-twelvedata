"""Small JSON client for the Twelve Data REST API."""

from __future__ import annotations

import os
from typing import Any

import httpx

API_BASE_URL = "https://api.twelvedata.com"


class _MissingAPIKeyError(ValueError):
    def __init__(self) -> None:
        super().__init__("Set TWELVE_DATA_API_KEY or pass api_key to TwelveDataClient")


class TwelveDataAPIError(Exception):
    """A request was rejected by the Twelve Data API."""

    @classmethod
    def unexpected_response(cls) -> TwelveDataAPIError:
        return cls("Unexpected Twelve Data response format")

    @classmethod
    def from_api_response(cls, code: Any, message: Any) -> TwelveDataAPIError:
        return cls(f"Twelve Data error {code}: {message}")


class TwelveDataClient:
    """Call Twelve Data JSON endpoints using an API key from the environment."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.api_key = (
            api_key if api_key is not None else os.getenv("TWELVE_DATA_API_KEY")
        )
        if not self.api_key:
            raise _MissingAPIKeyError
        self._http_client = http_client

    def get(self, endpoint: str, **params: Any) -> dict[str, Any]:
        """Return the decoded JSON response, raising on API or HTTP errors."""
        request = self._http_client.get if self._http_client else httpx.get
        response = request(
            f"{API_BASE_URL}/{endpoint}",
            headers={"Authorization": f"apikey {self.api_key}"},
            params={key: value for key, value in params.items() if value is not None},
            timeout=30.0,
        )
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise TwelveDataAPIError.unexpected_response() from None
        if not isinstance(data, dict):
            raise TwelveDataAPIError.unexpected_response()
        if data.get("status") == "error":
            code = data.get("code")
            message = data.get("message", "Unknown API error")
            raise TwelveDataAPIError.from_api_response(code, message)
        response.raise_for_status()
        return data

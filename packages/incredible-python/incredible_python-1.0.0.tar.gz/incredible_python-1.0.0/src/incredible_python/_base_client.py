from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, Mapping, Optional

import httpx

from ._exceptions import APIConnectionError, APIError, APITimeoutError

DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_TIMEOUT = 600.0
DEFAULT_MAX_RETRIES = 2
USER_AGENT = "incredible-python/0.1.0"


class BaseClient:
    """Shared HTTP client logic mirroring anthropic._base_client.Client."""

    DEFAULT_BASE_URL = DEFAULT_BASE_URL
    DEFAULT_TIMEOUT = DEFAULT_TIMEOUT
    DEFAULT_MAX_RETRIES = DEFAULT_MAX_RETRIES

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Optional[Mapping[str, str]] = None,
        default_query: Optional[Mapping[str, object]] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        if api_key is None:
            api_key = os.getenv("INCREDIBLE_API_KEY")

        self.api_key = api_key
        self.base_url = base_url or os.getenv("INCREDIBLE_BASE_URL", DEFAULT_BASE_URL)
        self.timeout = timeout
        self.max_retries = max_retries
        self.default_headers: Dict[str, str] = {
            **({"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}),
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        }
        if default_headers:
            self.default_headers.update(default_headers)

        self.default_query = dict(default_query or {})

        transport = httpx.HTTPTransport(retries=0)
        self._client = http_client or httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self.default_headers,
            transport=transport,
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> httpx.Response:
        merged_headers = dict(self.default_headers)
        if headers:
            merged_headers.update(headers)

        last_exc: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self._client.request(
                    method,
                    path,
                    json=json,
                    params=params or self.default_query,
                    headers=merged_headers,
                    timeout=timeout,
                )

                if response.status_code >= 400:
                    raise APIError(response.status_code, response.text)

                return response

            except httpx.TimeoutException as exc:
                last_exc = APITimeoutError(str(exc))
            except httpx.RequestError as exc:
                last_exc = APIConnectionError(str(exc))
            except APIError as exc:
                last_exc = exc
                break

            if attempt < self.max_retries:
                sleep_time = 0.5 * (2**attempt)
                time.sleep(sleep_time)

        if last_exc:
            raise last_exc
        raise APIConnectionError("Unknown request failure")

    def close(self) -> None:
        self._client.close()

    def with_options(
        self,
        *,
        timeout: Optional[float] = None,
        default_headers: Optional[Mapping[str, str]] = None,
        default_query: Optional[Mapping[str, object]] = None,
    ) -> "BaseClient":
        return self.__class__(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=timeout if timeout is not None else self.timeout,
            max_retries=self.max_retries,
            default_headers={**self.default_headers, **(default_headers or {})},
            default_query={**self.default_query, **(default_query or {})},
            http_client=self._client,
        )

    def __enter__(self) -> "BaseClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

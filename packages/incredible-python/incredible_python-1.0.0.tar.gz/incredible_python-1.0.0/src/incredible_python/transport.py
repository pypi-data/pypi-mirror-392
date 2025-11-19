from __future__ import annotations

import json
from typing import Any, Callable, Dict, Generator, Iterable, Optional

import httpx


class StreamBuilder:
    def __init__(self, response: httpx.Response) -> None:
        self._response = response

    def iter_lines(self) -> Generator[Dict[str, Any], None, None]:
        for raw_line in self._response.iter_lines():
            if not raw_line:
                continue
            line = raw_line.decode("utf-8")
            if not line.startswith("data:"):
                continue
            payload = line[len("data:") :].strip()
            if payload.upper() == "[DONE]":
                break
            try:
                yield json.loads(payload)
            except json.JSONDecodeError:
                continue

    def close(self) -> None:
        self._response.close()


class IncredibleHTTPClient(httpx.Client):
    def __init__(
        self,
        base_url: str,
        timeout: float,
        max_retries: int,
        headers: Dict[str, str],
    ) -> None:
        transport = httpx.HTTPTransport(retries=max_retries)
        super().__init__(
            base_url=base_url,
            timeout=timeout,
            headers=headers,
            transport=transport,
        )


class Response:
    def __init__(self, response: httpx.Response) -> None:
        self._response = response

    def json(self) -> Dict[str, Any]:
        self._response.raise_for_status()
        return self._response.json()

    def parse(self, model: Callable[[Dict[str, Any]], Any]) -> Any:
        payload = self.json()
        return model.from_dict(payload)


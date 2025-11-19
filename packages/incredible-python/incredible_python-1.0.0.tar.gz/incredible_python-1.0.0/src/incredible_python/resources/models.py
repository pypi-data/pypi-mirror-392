"""Models resource for listing available models."""

from __future__ import annotations

from typing import Optional


class Models:
    def __init__(self, client) -> None:
        self._client = client

    def list(self, *, timeout: Optional[float] = None):
        response = self._client.request("GET", "/v1/models", timeout=timeout)
        return response.json()

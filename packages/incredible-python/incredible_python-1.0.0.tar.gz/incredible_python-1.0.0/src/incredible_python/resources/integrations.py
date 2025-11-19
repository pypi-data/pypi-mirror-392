"""Integration resource helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class IntegrationConnectionResult:
    success: Optional[bool]
    message: Optional[str]
    redirect_url: Optional[str]
    instructions: Optional[str]
    integration_id: Optional[str]
    user_id: Optional[str]
    raw: Dict[str, Any]

    @property
    def requires_oauth(self) -> bool:
        return self.redirect_url is not None


class Integrations:
    def __init__(self, client) -> None:
        self._client = client

    def list(self, *, timeout: Optional[float] = None) -> List[Dict[str, Any]]:
        response = self._client.request(
            "GET",
            "/v1/integrations",
            timeout=timeout,
        )
        return response.json()

    def retrieve(self, integration_id: str, *, timeout: Optional[float] = None) -> Dict[str, Any]:
        response = self._client.request(
            "GET",
            f"/v1/integrations/{integration_id}",
            timeout=timeout,
        )
        return response.json()

    def connect(
        self,
        integration_id: str,
        *,
        user_id: Optional[str] = None,
        api_key: Optional[str] = None,
        callback_url: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> IntegrationConnectionResult:
        payload: Dict[str, Any] = {}
        if user_id is not None:
            payload["user_id"] = user_id
        if api_key is not None:
            payload["api_key"] = api_key
        if callback_url is not None:
            payload["callback_url"] = callback_url
        if extra:
            payload.update(extra)

        response = self._client.request(
            "POST",
            f"/v1/integrations/{integration_id}/connect",
            json=payload,
            timeout=timeout,
        )
        data = response.json()
        return IntegrationConnectionResult(
            success=data.get("success"),
            message=data.get("message"),
            redirect_url=data.get("redirect_url"),
            instructions=data.get("instructions"),
            integration_id=data.get("integration_id"),
            user_id=data.get("user_id"),
            raw=data,
        )

    def execute(
        self,
        integration_id: str,
        *,
        user_id: Optional[str] = None,
        feature_name: str,
        inputs: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "feature_name": feature_name,
            "inputs": inputs or {},
        }
        if user_id is not None:
            payload["user_id"] = user_id
        response = self._client.request(
            "POST",
            f"/v1/integrations/{integration_id}/execute",
            json=payload,
            timeout=timeout,
        )
        return response.json()

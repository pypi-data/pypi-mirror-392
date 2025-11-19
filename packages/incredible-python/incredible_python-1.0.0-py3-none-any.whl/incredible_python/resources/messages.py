"""Messages resource compatible with Anthropic's SDK surface."""

from __future__ import annotations

from typing import Iterable, Optional

from .._exceptions import APIResponseValidationError
from ..transport import Response, StreamBuilder
from ..types.messages import Message, MessageCreateParams


class Messages:
    def __init__(self, client) -> None:  # client: BaseClient
        self._client = client
    
    def __call__(
        self,
        *,
        max_tokens: int,
        messages: Iterable[dict],
        model: str,
        **kwargs
    ) -> Message | StreamBuilder:
        """
        Shorthand for create() - allows calling client.messages(...) directly.
        
        Example:
            ```python
            # Instead of client.messages.create(...)
            response = client.messages(
                model="small-1",
                max_tokens=100,
                messages=[{"role": "user", "content": "Hello"}]
            )
            ```
        """
        return self.create(
            max_tokens=max_tokens,
            messages=messages,
            model=model,
            **kwargs
        )

    def create(
        self,
        *,
        max_tokens: int,
        messages: Iterable[dict],
        model: str,
        metadata: Optional[dict] = None,
        service_tier: Optional[str] = None,
        stop_sequences: Optional[Iterable[str]] = None,
        stream: bool = False,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        thinking: Optional[dict] = None,
        tool_choice: Optional[dict] = None,
        tools: Optional[Iterable[dict]] = None,
        functions: Optional[Iterable[dict]] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        extra_headers: Optional[dict[str, str]] = None,
        extra_query: Optional[dict] = None,
        extra_body: Optional[dict] = None,
        timeout: Optional[float] = None,
    ) -> Message | StreamBuilder:
        params = MessageCreateParams(
            max_tokens=max_tokens,
            messages=list(messages),
            model=model,
            metadata=metadata,
            service_tier=service_tier,
            stop_sequences=list(stop_sequences or []),
            stream=stream,
            system=system,
            temperature=temperature,
            thinking=thinking,
            tool_choice=tool_choice,
            tools=list(tools or []),
            functions=list(functions or []),
            top_k=top_k,
            top_p=top_p,
            extra=dict(extra_body or {}),
        )

        headers = {"x-incredible-client": "python"}
        if extra_headers:
            headers.update(extra_headers)

        response = self._client.request(
            "POST",
            "/v1/chat-completion",
            json=params.to_dict(),
            params=extra_query,
            headers=headers,
            timeout=timeout,
        )

        if stream:
            return StreamBuilder(response)

        parsed = Response(response).json()
        try:
            message = Message.from_api_response(parsed)
        except (KeyError, TypeError, ValueError) as exc:
            raise APIResponseValidationError(str(exc)) from exc
        return message

    def stream(
        self,
        *,
        max_tokens: int,
        messages: Iterable[dict],
        model: str,
        **kwargs,
    ) -> StreamBuilder:
        return self.create(
            max_tokens=max_tokens,
            messages=messages,
            model=model,
            stream=True,
            **kwargs,
        )

    def count_tokens(
        self,
        *,
        messages: Iterable[dict],
        model: str,
        system: Optional[str] = None,
        tools: Optional[Iterable[dict]] = None,
        functions: Optional[Iterable[dict]] = None,
        extra_headers: Optional[dict[str, str]] = None,
        extra_query: Optional[dict] = None,
        timeout: Optional[float] = None,
    ) -> dict:
        headers = {"x-incredible-client": "python"}
        if extra_headers:
            headers.update(extra_headers)

        payload = {
            "messages": list(messages),
            "model": model,
        }
        if system is not None:
            payload["system"] = system
        if tools:
            payload["tools"] = list(tools)
        if functions:
            payload["functions"] = list(functions)

        response = self._client.request(
            "POST",
            "/v1/messages/count_tokens",
            json=payload,
            params=extra_query,
            headers=headers,
            timeout=timeout,
        )
        return response.json()

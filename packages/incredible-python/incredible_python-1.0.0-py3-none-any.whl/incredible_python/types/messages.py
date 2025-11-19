"""Message related data structures."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

ContentBlock = Dict[str, Any]


def _to_content_blocks(content: Any) -> List[ContentBlock]:
    if isinstance(content, list):
        return list(content)
    if isinstance(content, dict):
        return [content]
    if content is None:
        return []
    return [{"type": "text", "text": str(content)}]


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class ToolResult:
    id: str
    output: Any


@dataclass
class Message:
    id: str
    type: str
    role: str
    content: List[ContentBlock]
    model: Optional[str] = None
    stop_reason: Optional[str] = None
    stop_sequence: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    token_usage: Optional[Dict[str, Any]] = None
    tool_calls: List[ToolCall] = field(default_factory=list)
    tool_results: List[ToolResult] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, payload: Dict[str, Any]) -> "Message":
        result = payload.get("result") or {}
        responses = result.get("response") or []
        if not responses:
            raise ValueError("API response missing 'result.response' entries")

        assistant = None
        tool_calls: List[ToolCall] = []
        tool_results: List[ToolResult] = []

        for item in responses:
            item_type = item.get("type")
            if item.get("role") == "assistant" and assistant is None:
                assistant = item

            if item_type == "function_call":
                call_id = item.get("function_call_id") or f"toolu_{uuid.uuid4().hex}"
                for func in item.get("function_calls", []) or []:
                    tool_calls.append(
                        ToolCall(
                            id=call_id,
                            name=func.get("name", ""),
                            arguments=func.get("input", {}),
                        )
                    )
            elif item_type == "function_call_result":
                call_id = item.get("function_call_id") or f"toolu_{uuid.uuid4().hex}"
                tool_results.append(
                    ToolResult(
                        id=call_id,
                        output=item.get("function_call_results"),
                    )
                )

        if assistant is None:
            assistant = responses[0]

        content_blocks = _to_content_blocks(assistant.get("content"))

        for call in tool_calls:
            content_blocks.append(
                {
                    "type": "tool_use",
                    "id": call.id,
                    "name": call.name,
                    "input": call.arguments,
                }
            )
        for result_block in tool_results:
            content_blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": result_block.id,
                    "content": result_block.output,
                }
            )

        message_id = assistant.get("id") or f"msg_{uuid.uuid4().hex}"

        return cls(
            id=message_id,
            type=assistant.get("type", "message"),
            role=assistant.get("role", "assistant"),
            content=content_blocks,
            model=payload.get("model") or result.get("model"),
            stop_reason=result.get("stop_reason") or assistant.get("stop_reason"),
            stop_sequence=result.get("stop_sequence") or assistant.get("stop_sequence"),
            usage=result.get("usage"),
            token_usage=result.get("token_usage"),
            tool_calls=tool_calls,
            tool_results=tool_results,
            raw=payload,
        )


@dataclass
class MessageCreateParams:
    max_tokens: int
    messages: List[Dict[str, Any]]
    model: str
    metadata: Optional[Dict[str, Any]] = None
    service_tier: Optional[str] = None
    stop_sequences: Optional[Iterable[str]] = None
    stream: bool = False
    system: Optional[str] = None
    temperature: Optional[float] = None
    thinking: Optional[Dict[str, Any]] = None
    tool_choice: Optional[Dict[str, Any]] = None
    tools: Optional[Iterable[Dict[str, Any]]] = None
    functions: Optional[Iterable[Dict[str, Any]]] = None
    top_k: Optional[int] = None
    top_p: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "max_tokens": self.max_tokens,
            "messages": self.messages,
            "model": self.model,
            "stream": self.stream,
        }
        if self.metadata is not None:
            payload["metadata"] = self.metadata
        if self.service_tier is not None:
            payload["service_tier"] = self.service_tier
        if self.stop_sequences:
            payload["stop_sequences"] = list(self.stop_sequences)
        if self.system is not None:
            payload["system"] = self.system
        if self.temperature is not None:
            payload["temperature"] = self.temperature
        if self.thinking is not None:
            payload["thinking"] = self.thinking
        if self.tool_choice is not None:
            payload["tool_choice"] = self.tool_choice
        if self.tools:
            payload["tools"] = list(self.tools)
        if self.functions:
            payload["functions"] = list(self.functions)
        if self.top_k is not None:
            payload["top_k"] = self.top_k
        if self.top_p is not None:
            payload["top_p"] = self.top_p
        payload.update(self.extra)
        return payload

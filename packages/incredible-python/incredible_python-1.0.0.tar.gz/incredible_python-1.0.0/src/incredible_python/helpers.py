"""Utilities for working with Incredible function-calling messages."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional

from .types.messages import Message


def make_tool_call(
    name: str,
    arguments: Dict[str, Any],
    *,
    call_id: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a function_call message block compatible with the API."""
    call_identifier = call_id or f"toolu_{uuid.uuid4().hex}"
    call_payload: Dict[str, Any] = {
        "type": "function_call",
        "function_call_id": call_identifier,
        "function_calls": [
            {
                "name": name,
                "input": arguments,
            }
        ],
    }
    if description:
        call_payload["description"] = description
    return call_payload


def make_tool_calls(
    calls: Iterable[Dict[str, Any]],
    *,
    call_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a function_call message with multiple function invocations."""
    call_identifier = call_id or f"toolu_{uuid.uuid4().hex}"
    return {
        "type": "function_call",
        "function_call_id": call_identifier,
        "function_calls": list(calls),
    }


def make_tool_result(
    call_id: str,
    result: Any,
) -> Dict[str, Any]:
    """Create a function_call_result message block."""
    if isinstance(result, list):
        payload = result
    else:
        payload = [result]
    return {
        "type": "function_call_result",
        "function_call_id": call_id,
        "function_call_results": payload,
    }


@dataclass
class ToolExecution:
    """Represents a single tool call requested by the model."""

    name: str
    arguments: Dict[str, Any]
    description: Optional[str] = None


@dataclass
class ToolExecutionPlan:
    """Plan returned by :func:`build_tool_execution_plan`."""

    call_id: str
    tool_calls: List[ToolExecution] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not self.tool_calls

    def to_dict(self) -> Dict[str, Any]:
        return {
            "call_id": self.call_id,
            "tool_calls": [
                {
                    "name": call.name,
                    "arguments": call.arguments,
                    "description": call.description,
                }
                for call in self.tool_calls
            ],
        }


def build_tool_execution_plan(response_payload: Dict[str, Any]) -> Optional[ToolExecutionPlan]:
    """Extract the tool execution plan from an Incredible API response."""
    try:
        message = Message.from_api_response(response_payload)
    except Exception:
        return None

    if not message.tool_calls:
        return None

    call_id = message.tool_calls[0].id
    plan = ToolExecutionPlan(call_id=call_id)
    for call in message.tool_calls:
        plan.tool_calls.append(
            ToolExecution(
                name=call.name,
                arguments=call.arguments,
            )
        )
    return plan


def execute_plan(
    plan: ToolExecutionPlan,
    *,
    registry: Dict[str, Callable[..., Any]],
) -> List[Any]:
    """Execute a plan and return results in the order requested."""
    results: List[Any] = []
    for call in plan.tool_calls:
        func = registry.get(call.name)
        if func is None:
            results.append({"error": f"No registered tool named '{call.name}'"})
            continue
        try:
            results.append(func(**call.arguments))
        except Exception as exc:
            results.append({"error": str(exc)})
    return results


def build_follow_up_messages(
    original_messages: List[Dict[str, Any]],
    plan: ToolExecutionPlan,
    execution_results: List[Any],
) -> List[Dict[str, Any]]:
    call_block = make_tool_calls(
        [
            {
                "name": call.name,
                "input": call.arguments,
            }
            for call in plan.tool_calls
        ],
        call_id=plan.call_id,
    )
    result_block = make_tool_result(plan.call_id, execution_results)
    return original_messages + [call_block, result_block]


__all__ = [
    "make_tool_call",
    "make_tool_calls",
    "make_tool_result",
    "build_tool_execution_plan",
    "ToolExecution",
    "ToolExecutionPlan",
    "execute_plan",
    "build_follow_up_messages",
]

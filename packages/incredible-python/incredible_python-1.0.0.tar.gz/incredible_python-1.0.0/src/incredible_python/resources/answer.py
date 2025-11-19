"""
Answer resource for simple Q&A using Minimax M2.

This module provides a simple question-answering interface with optional
structured output support via JSON schemas.
"""

from __future__ import annotations

from typing import Any, Dict, Iterator, Literal, Optional, TypedDict, cast
from dataclasses import dataclass

from .._base_client import BaseClient


@dataclass
class AnswerResponse:
    """
    Response from the answer endpoint (simple mode).
    
    Attributes:
        success: Whether the request was successful
        answer: The generated answer text
    """
    success: bool
    answer: str


@dataclass
class StructuredAnswerResponse:
    """
    Response from the answer endpoint (structured mode).
    
    Attributes:
        success: Whether the request was successful
        data: Structured data matching the provided schema
    """
    success: bool
    data: Dict[str, Any]


class AnswerStreamEvent(TypedDict, total=False):
    """
    Streaming chunk emitted by the /v1/answer SSE endpoint.
    """
    thinking: str
    content: str
    tokens: int
    done: Literal[True]
    error: str


class Answer:
    """
    Answer resource for simple Q&A using Minimax M2.
    
    This endpoint provides a simple interface for question answering with
    optional structured output via JSON schemas.
    
    Example (simple answer):
        ```python
        client = Incredible(api_key="your-api-key")
        
        response = client.answer.create(
            query="What is the capital of France?"
        )
        print(response.answer)
        ```
    
    Example (structured output):
        ```python
        schema = {
            "type": "object",
            "properties": {
                "date": {"type": "string"},
                "event": {"type": "string"}
            },
            "required": ["date", "event"]
        }
        
        response = client.answer.create(
            query="When did World War II end?",
            response_format=schema
        )
        print(response.data)  # {"date": "1945-09-02", "event": "Japan surrendered"}
        ```
    """
    
    def __init__(self, client: BaseClient) -> None:
        """
        Initialize the Answer resource.
        
        Args:
            client: The base client instance for making API requests
        """
        self._client = client
    
    def __call__(
        self,
        query: str,
        response_format: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> AnswerResponse | StructuredAnswerResponse | Iterator[AnswerStreamEvent]:
        """
        Shorthand for create() - allows calling client.answer(...) directly.
        
        Args:
            query: The question or task to answer
            response_format: Optional JSON schema for structured output
            stream: Enable streaming response
            
        Returns:
            AnswerResponse, StructuredAnswerResponse, or streaming iterator
            
        Example:
            ```python
            # Instead of client.answer.create(query="...")
            response = client.answer(query="What is 2+2?")
            print(response.answer)
            ```
        """
        return self._create(
            query=query,
            response_format=response_format,
            stream=stream
        )
    
    def _create(
        self,
        query: str,
        response_format: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> AnswerResponse | StructuredAnswerResponse | Iterator[AnswerStreamEvent]:
        """
        Answer a query using Minimax M2.
        
        Supports both simple text answers and structured output via optional
        response_format parameter.
        
        Args:
            query: The question or task to answer
            response_format: Optional JSON schema for structured output.
                           If provided, the response will be parsed as JSON
                           matching the schema.
            stream: Enable streaming response (default: False)
                   Note: Streaming returns an iterator, not a response object
        
        Returns:
            AnswerResponse: Simple text answer (if no response_format)
            StructuredAnswerResponse: Structured data (if response_format provided)
            Iterator[AnswerStreamEvent]: Streaming iterator (if stream=True)
        
        Raises:
            AuthenticationError: If the API key is invalid
            ValidationError: If the request parameters are invalid
            APIError: If the API returns an error
            APIConnectionError: If the connection to the API fails
        
        Example (simple):
            ```python
            response = client.answer._create(
                query="What is 2+2?"
            )
            print(response.answer)  # "2+2 equals 4"
            ```
        
        Example (structured):
            ```python
            schema = {
                "type": "object",
                "properties": {
                    "result": {"type": "number"},
                    "explanation": {"type": "string"}
                },
                "required": ["result"]
            }
            
            response = client.answer._create(
                query="What is 15% of 2,500?",
                response_format=schema
            )
            print(response.data)  # {"result": 375, "explanation": "..."}
            ```
        
        Example (streaming):
            ```python
            stream = client.answer._create(
                query="Tell me about quantum computing",
                stream=True
            )
            
            for event in stream:
                if "content" in event:
                    print(event["content"], end="", flush=True)
                elif "thinking" in event:
                    print(f"[Thinking: {event['thinking']}]")
            ```
        """
        payload = {
            "query": query,
            "stream": stream
        }
        
        if response_format is not None:
            payload["response_format"] = response_format
        
        if stream:
            # Return streaming iterator for SSE
            response = self._client.request(
                "POST",
                "/v1/answer",
                json=payload
            )
            return self._parse_sse_stream(response)
        
        response = self._client.request(
            "POST",
            "/v1/answer",
            json=payload
        )
        data = response.json()
        
        # Parse response based on whether structured output was requested
        if response_format is not None:
            return StructuredAnswerResponse(
                success=data.get("success", False),
                data=data.get("data", {})
            )
        else:
            return AnswerResponse(
                success=data.get("success", False),
                answer=data.get("answer", "")
            )
    
    def _parse_sse_stream(self, response) -> Iterator[AnswerStreamEvent]:
        """
        Parse Server-Sent Events (SSE) stream.
        
        Yields:
            AnswerStreamEvent objects with keys like "thinking", "content",
            "tokens", "done", or "error"
        """
        for line in response.iter_lines():
            if line:
                # iter_lines() returns strings in newer httpx versions
                if isinstance(line, bytes):
                    line = line.decode('utf-8')
                if line.startswith('data: '):
                    import json
                    try:
                        event_data = json.loads(line[6:])  # Remove 'data: ' prefix
                        yield cast(AnswerStreamEvent, event_data)
                    except json.JSONDecodeError:
                        continue

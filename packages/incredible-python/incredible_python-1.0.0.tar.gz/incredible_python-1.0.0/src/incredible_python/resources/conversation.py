"""
Conversation resource for multi-turn conversations using DeepSeek v3.1.

This module provides a simple conversation interface without tool calling.
"""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Literal, Optional, TypedDict, cast
from dataclasses import dataclass

from .._base_client import BaseClient


class ConversationStreamEvent(TypedDict, total=False):
    """
    Streaming event from the conversation endpoint.
    
    Attributes:
        thinking: Reasoning/thinking content from the model
        content: Regular response content
        tokens: Token usage count
        done: Signal that streaming is complete
        error: Error message if something went wrong
    """
    thinking: str
    content: str
    tokens: int
    done: Literal[True]
    error: str


@dataclass
class ConversationResponse:
    """
    Response from the conversation endpoint.
    
    Attributes:
        success: Whether the request was successful
        response: The generated response text
    """
    success: bool
    response: str


class Conversation:
    """
    Conversation resource for multi-turn conversations using DeepSeek v3.1.
    
    This endpoint provides a simple conversation interface without tool calling.
    It uses DeepSeek v3.1 which is fast and cost-effective for conversational tasks.
    
    Example:
        ```python
        client = Incredible(api_key="your-api-key")
        
        response = client.conversation.create(
            messages=[
                {"role": "user", "content": "Hello!"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "How are you?"}
            ]
        )
        print(response.response)
        ```
    
    Example (with system prompt):
        ```python
        response = client.conversation.create(
            messages=[
                {"role": "user", "content": "What's 2+2?"}
            ],
            system_prompt="You are a helpful math tutor."
        )
        print(response.response)
        ```
    """
    
    def __init__(self, client: BaseClient) -> None:
        """
        Initialize the Conversation resource.
        
        Args:
            client: The base client instance for making API requests
        """
        self._client = client
    
    def __call__(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> ConversationResponse | Iterator[ConversationStreamEvent]:
        """
        Shorthand for create() - allows calling client.conversation(...) directly.
        
        Example:
            ```python
            # Instead of client.conversation.create(...)
            response = client.conversation(
                messages=[
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi!"},
                    {"role": "user", "content": "How are you?"}
                ]
            )
            ```
        """
        return self.create(messages=messages, **kwargs)
    
    def create(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> ConversationResponse | Iterator[ConversationStreamEvent]:
        """
        Create a multi-turn conversation using DeepSeek v3.1.
        
        Args:
            messages: List of conversation messages. Each message should have
                     "role" (either "user" or "assistant") and "content" fields.
            system_prompt: Optional system prompt to guide the conversation.
                          Defaults to "You are a helpful assistant."
            stream: Enable streaming response (default: False)
                   Note: Streaming returns an iterator, not a response object
        
        Returns:
            ConversationResponse: The assistant's response (if stream=False)
            Iterator[ConversationStreamEvent]: Streaming iterator (if stream=True)
        
        Raises:
            AuthenticationError: If the API key is invalid
            ValidationError: If the request parameters are invalid
            APIError: If the API returns an error
            APIConnectionError: If the connection to the API fails
        
        Example:
            ```python
            response = client.conversation.create(
                messages=[
                    {"role": "user", "content": "I'm learning Python"},
                    {"role": "assistant", "content": "That's great!"},
                    {"role": "user", "content": "Can you explain lists?"}
                ],
                system_prompt="You are a patient programming tutor."
            )
            print(response.response)
            ```
        
        Example (streaming):
            ```python
            stream = client.conversation.create(
                messages=[
                    {"role": "user", "content": "Tell me a story"}
                ],
                stream=True
            )
            
            for event in stream:
                if "content" in event:
                    print(event["content"], end="", flush=True)
                elif "thinking" in event:
                    print(f"[Thinking: {event['thinking']}]")
                elif "done" in event:
                    print("\n[Done]")
            ```
        """
        payload = {
            "messages": messages,
            "stream": stream
        }
        
        if system_prompt is not None:
            payload["system_prompt"] = system_prompt
        
        if stream:
            # Return streaming iterator for SSE
            response = self._client.request(
                "POST",
                "/v1/conversation",
                json=payload
            )
            return self._parse_sse_stream(response)
        
        response = self._client.request(
            "POST",
            "/v1/conversation",
            json=payload
        )
        data = response.json()
        
        return ConversationResponse(
            success=data.get("success", False),
            response=data.get("response", "")
        )
    
    def _parse_sse_stream(self, response) -> Iterator[ConversationStreamEvent]:
        """
        Parse Server-Sent Events (SSE) stream.
        
        Yields:
            ConversationStreamEvent objects with keys like "thinking", "content",
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
                        yield cast(ConversationStreamEvent, event_data)
                    except json.JSONDecodeError:
                        continue


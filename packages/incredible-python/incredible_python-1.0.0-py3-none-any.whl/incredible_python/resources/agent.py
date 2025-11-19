"""
Agent resource for Incredible SDK.
Provides agentic conversation with tool calling using Kimi K2 Thinking.
"""

from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Literal, Optional, TypedDict, cast


class AgentStreamEvent(TypedDict, total=False):
    """
    Streaming event from the agent endpoint.
    
    Attributes:
        thinking: Reasoning/thinking content from the model
        content: Regular response content
        tool_call: Tool call information (id, name, inputs)
        tokens: Token usage count
        done: Signal that streaming is complete
        error: Error message if something went wrong
    """
    thinking: str
    content: str
    tool_call: Dict[str, Any]
    tokens: int
    done: Literal[True]
    error: str


@dataclass
class ToolCall:
    """Tool call made by the agent."""
    
    id: str
    name: str
    inputs: Dict[str, Any]


@dataclass
class AgentResponse:
    """Response from agent endpoint."""
    
    success: bool
    response: str
    tool_calls: Optional[List[ToolCall]] = None
    raw_response: Optional[Dict[str, Any]] = None


class Agent:
    """
    Agent resource for agentic conversation with tool calling.
    
    Uses Kimi K2 Thinking model which excels at reasoning and tool use.
    Note: This endpoint returns tool calls but does not execute them - 
    the caller is responsible for executing tools and providing results back.
    
    Example:
        ```python
        from incredible_python import Incredible
        
        client = Incredible(api_key="your-api-key")
        
        # Define tools
        tools = [{
            "name": "get_weather",
            "description": "Get weather for a location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }]
        
        # Agent conversation
        response = client.agent.chat(
            messages=[
                {"role": "user", "content": "What's the weather in SF?"}
            ],
            tools=tools
        )
        
        if response.tool_calls:
            for call in response.tool_calls:
                print(f"Tool: {call.name}, Inputs: {call.inputs}")
        ```
    """
    
    def __init__(self, client) -> None:
        self._client = client
    
    def __call__(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        **kwargs
    ) -> AgentResponse | Iterator[AgentStreamEvent]:
        """
        Shorthand for chat() - allows calling client.agent(...) directly.
        
        Example:
            ```python
            # Instead of client.agent.chat(...)
            response = client.agent(
                messages=[{"role": "user", "content": "Calculate 5+5"}],
                tools=[{
                    "name": "calculator",
                    "description": "Perform calculations",
                    "input_schema": {...}
                }]
            )
            ```
        """
        return self.chat(messages=messages, tools=tools, **kwargs)
    
    def chat(
        self,
        *,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        stream: bool = False,
        timeout: Optional[float] = None,
    ) -> AgentResponse | Iterator[AgentStreamEvent]:
        """
        Agentic conversation with tool calling using Kimi K2 Thinking.
        
        This endpoint provides an agentic interface with function calling capabilities.
        The agent can decide to call tools based on the conversation context.
        
        Note: This endpoint returns tool calls but does not execute them. The caller
        is responsible for executing tools and providing results back in follow-up messages.
        
        Args:
            messages: List of conversation messages with "role" and "content" (required)
                     Role can be "user" or "assistant"
            tools: List of tool definitions (required). Each tool must have:
                  - name: Tool name
                  - description: What the tool does
                  - input_schema: JSON schema for tool inputs
            system_prompt: System prompt to guide the agent (optional)
            stream: Enable streaming response (default: False)
            timeout: Request timeout in seconds (optional)
        
        Returns:
            AgentResponse: Response object (if stream=False) with:
                - success: Whether the request was successful
                - response: The agent's text response
                - tool_calls: List of tool calls made (if any), each with:
                    - id: Tool call ID
                    - name: Tool name
                    - inputs: Tool input arguments
            Iterator[AgentStreamEvent]: Streaming iterator (if stream=True)
        
        Raises:
            ValidationError: If request parameters are invalid
            APIError: If the API request fails
        
        Example:
            ```python
            # Define tools
            tools = [
                {
                    "name": "get_weather",
                    "description": "Get current weather for a location",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City name"
                            },
                            "units": {
                                "type": "string",
                                "enum": ["celsius", "fahrenheit"],
                                "description": "Temperature units"
                            }
                        },
                        "required": ["location"]
                    }
                },
                {
                    "name": "search_web",
                    "description": "Search the web for information",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            }
                        },
                        "required": ["query"]
                    }
                }
            ]
            
            # Single-turn conversation
            response = client.agent.chat(
                messages=[
                    {"role": "user", "content": "What's the weather in Tokyo?"}
                ],
                tools=tools
            )
            
            print(f"Agent: {response.response}")
            
            if response.tool_calls:
                for call in response.tool_calls:
                    print(f"Calling {call.name} with {call.inputs}")
                    # Execute the tool and get results
                    # Then send back in next message...
            
            # Multi-turn conversation with tool results
            response = client.agent.chat(
                messages=[
                    {"role": "user", "content": "What's the weather in Tokyo?"},
                    {"role": "assistant", "content": "I'll check the weather for you."},
                    {"role": "user", "content": "The weather is 15°C and sunny."},
                    {"role": "user", "content": "Now what about Paris?"}
                ],
                tools=tools,
                system_prompt="You are a helpful weather assistant."
            )
            ```
        
        Note:
            - The agent uses Kimi K2 Thinking model which excels at reasoning
            - Tool calls are returned but not executed automatically
            - You must execute tools yourself and provide results in follow-up messages
            - Streaming is supported (stream=True) for real-time responses
        """
        if not messages or len(messages) == 0:
            from .._exceptions import ValidationError
            raise ValidationError("messages cannot be empty")
        
        if not tools or len(tools) == 0:
            from .._exceptions import ValidationError
            raise ValidationError("tools cannot be empty")
        
        # Validate message format
        for msg in messages:
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                from .._exceptions import ValidationError
                raise ValidationError("Each message must have 'role' and 'content' fields")
            
            if msg["role"] not in ["user", "assistant"]:
                from .._exceptions import ValidationError
                raise ValidationError("Message role must be 'user' or 'assistant'")
        
        # Validate tool format
        for tool in tools:
            if not isinstance(tool, dict):
                from .._exceptions import ValidationError
                raise ValidationError("Each tool must be a dictionary")
            
            required_fields = ["name", "description", "input_schema"]
            for field in required_fields:
                if field not in tool:
                    from .._exceptions import ValidationError
                    raise ValidationError(f"Tool must have '{field}' field")
        
        # Build request payload
        payload: Dict[str, Any] = {
            "messages": messages,
            "tools": tools,
            "stream": stream,
        }
        
        if system_prompt:
            payload["system_prompt"] = system_prompt
        
        # Handle streaming
        if stream:
            response = self._client.request(
                "POST",
                "/v1/agent",
                json=payload,
                timeout=timeout
            )
            return self._parse_sse_stream(response)
        
        # Make request
        response = self._client.request(
            "POST",
            "/v1/agent",
            json=payload,
            timeout=timeout
        )
        
        data = response.json()
        
        # Parse tool calls if present
        tool_calls = None
        if data.get("tool_calls"):
            tool_calls = [
                ToolCall(
                    id=call.get("id", ""),
                    name=call.get("name", ""),
                    inputs=call.get("inputs", {})
                )
                for call in data["tool_calls"]
            ]
        
        return AgentResponse(
            success=data.get("success", False),
            response=data.get("response", ""),
            tool_calls=tool_calls,
            raw_response=data
        )
    
    def stream_chat(
        self,
        *,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Iterator[AgentStreamEvent]:
        """
        Stream agentic conversation with tool calling.
        
        This is a convenience method that sets stream=True and returns
        the streaming response for Server-Sent Events (SSE).
        
        Args:
            messages: List of conversation messages
            tools: List of tool definitions
            system_prompt: Optional system prompt
            timeout: Request timeout
        
        Yields:
            Server-Sent Events with:
                - {"thinking": "..."} - Reasoning/thinking content
                - {"content": "..."} - Regular response text
                - {"tool_call": {...}} - Tool call information
                - {"tokens": N} - Token usage
                - {"done": true} - Stream complete
                - {"error": "..."} - Error occurred
        
        Example:
            ```python
            tools = [{
                "name": "calculator",
                "description": "Perform calculations",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string"}
                    },
                    "required": ["expression"]
                }
            }]
            
            for event in client.agent.stream_chat(
                messages=[
                    {"role": "user", "content": "What is 25 * 4?"}
                ],
                tools=tools
            ):
                if "thinking" in event:
                    print(f"Thinking: {event['thinking']}")
                elif "content" in event:
                    print(f"Response: {event['content']}")
                elif "tool_call" in event:
                    print(f"Tool call: {event['tool_call']}")
            ```
        """
        # Validate inputs (same as chat method)
        if not messages or len(messages) == 0:
            from .._exceptions import ValidationError
            raise ValidationError("messages cannot be empty")
        
        if not tools or len(tools) == 0:
            from .._exceptions import ValidationError
            raise ValidationError("tools cannot be empty")
        
        # Build request payload with stream=True
        payload: Dict[str, Any] = {
            "messages": messages,
            "tools": tools,
            "stream": True,
        }
        
        if system_prompt:
            payload["system_prompt"] = system_prompt
        
        # Make streaming request
        response = self._client.request(
            "POST",
            "/v1/agent",
            json=payload,
            timeout=timeout
        )
        
        # Parse and yield SSE events
        yield from self._parse_sse_stream(response)
    
    def _parse_sse_stream(self, response) -> Iterator[AgentStreamEvent]:
        """
        Parse Server-Sent Events (SSE) stream.
        
        Yields:
            AgentStreamEvent objects with keys like "thinking", "content",
            "tool_call", "tokens", "done", or "error"
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
                        yield cast(AgentStreamEvent, event_data)
                    except json.JSONDecodeError:
                        continue


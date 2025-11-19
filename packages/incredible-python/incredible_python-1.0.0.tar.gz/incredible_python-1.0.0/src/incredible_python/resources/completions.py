"""Completions resource for OpenAI-style text completion.

This provides the /v1/completions endpoint which is different from
chat completions. It's for direct text completion without conversation format.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CompletionChoice:
    """A single completion choice.
    
    Attributes:
        text: The generated text
        index: Index of this choice
        finish_reason: Why generation stopped
        logprobs: Log probabilities if requested
    """
    text: str
    index: int
    finish_reason: Optional[str] = None
    logprobs: Optional[Dict[str, Any]] = None


@dataclass
class CompletionResponse:
    """Response from completions endpoint.
    
    Attributes:
        id: Unique completion ID
        choices: List of completion choices
        created: Unix timestamp
        model: Model used
        object: Object type (always "text_completion")
        usage: Token usage information
    """
    id: str
    choices: List[CompletionChoice]
    created: int
    model: str
    object: str = "text_completion"
    usage: Optional[Dict[str, Any]] = None


class Completions:
    """OpenAI-style text completions resource.
    
    This endpoint is different from chat completions. It's for direct
    text completion without the conversational message format.
    
    Example:
        >>> client = Incredible()
        >>> 
        >>> # Simple completion
        >>> response = client.completions.create(
        ...     model="small-1",
        ...     prompt="Once upon a time",
        ...     max_tokens=50
        ... )
        >>> print(response.choices[0].text)
        >>> 
        >>> # Multiple completions
        >>> response = client.completions.create(
        ...     model="small-1",
        ...     prompt="Write a haiku about",
        ...     max_tokens=50,
        ...     n=3  # Generate 3 variations
        ... )
        >>> for choice in response.choices:
        ...     print(f"Choice {choice.index}: {choice.text}")
    """
    
    def __init__(self, client) -> None:
        self._client = client
    
    def __call__(
        self,
        prompt: str,
        **kwargs
    ):
        """
        Shorthand for create() - allows calling client.completions(...) directly.
        
        Example:
            ```python
            # Instead of client.completions.create(...)
            response = client.completions(
                prompt="Once upon a time",
                model="small-1",
                max_tokens=50
            )
            ```
        """
        return self.create(prompt=prompt, **kwargs)
    
    def create(
        self,
        *,
        model: str,
        prompt: str | List[str],
        max_tokens: int = 16,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        n: Optional[int] = None,
        stream: bool = False,
        logprobs: Optional[int] = None,
        echo: bool = False,
        stop: Optional[str | List[str]] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        best_of: Optional[int] = None,
        logit_bias: Optional[Dict[str, float]] = None,
        user: Optional[str] = None,
        suffix: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> CompletionResponse:
        """Create a text completion.
        
        Generate text completion(s) from a prompt. This is the OpenAI-style
        completions endpoint, different from chat completions.
        
        Args:
            model: Model ID ("small-1" or "small-2")
            prompt: Text prompt(s) to complete. Can be string or list of strings.
            max_tokens: Maximum tokens to generate. Default: 16
            temperature: Sampling temperature (0.0-2.0). Default: 1.0
                Lower = more focused, Higher = more creative
            top_p: Nucleus sampling parameter (0.0-1.0). Optional
            n: Number of completions to generate. Default: 1
            stream: Whether to stream the response. Default: False
            logprobs: Include log probabilities. Optional
            echo: Echo back the prompt in addition to completion. Default: False
            stop: Stop sequences. Can be string or list of strings. Optional
            presence_penalty: Penalty for new tokens (-2.0 to 2.0). Optional
            frequency_penalty: Penalty for frequent tokens (-2.0 to 2.0). Optional
            best_of: Generate N and return best. Optional
            logit_bias: Modify likelihood of specific tokens. Optional
            user: User identifier for tracking. Optional
            suffix: Text to append after completion. Optional
            timeout: Request timeout in seconds. Optional
        
        Returns:
            CompletionResponse with generated text choices
        
        Raises:
            APIError: If request fails
            AuthenticationError: If API key invalid
            RateLimitError: If rate limit exceeded
        
        Example:
            >>> # Basic completion
            >>> response = client.completions.create(
            ...     model="small-1",
            ...     prompt="The capital of France is",
            ...     max_tokens=10
            ... )
            >>> print(response.choices[0].text)
            >>> 
            >>> # With temperature
            >>> response = client.completions.create(
            ...     model="small-1",
            ...     prompt="Write a creative story:",
            ...     max_tokens=100,
            ...     temperature=1.5
            ... )
            >>> 
            >>> # Multiple completions
            >>> response = client.completions.create(
            ...     model="small-1",
            ...     prompt="AI is",
            ...     max_tokens=30,
            ...     n=3
            ... )
            >>> for i, choice in enumerate(response.choices):
            ...     print(f"Completion {i+1}: {choice.text}")
            >>> 
            >>> # With stop sequences
            >>> response = client.completions.create(
            ...     model="small-1",
            ...     prompt="List 3 colors:\n1.",
            ...     max_tokens=50,
            ...     stop=["\n4.", "\n\n"]
            ... )
        """
        # Build request payload
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
        }
        
        # Add optional parameters
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if n is not None:
            payload["n"] = n
        if stream:
            payload["stream"] = stream
        if logprobs is not None:
            payload["logprobs"] = logprobs
        if echo:
            payload["echo"] = echo
        if stop is not None:
            payload["stop"] = stop
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if best_of is not None:
            payload["best_of"] = best_of
        if logit_bias is not None:
            payload["logit_bias"] = logit_bias
        if user is not None:
            payload["user"] = user
        if suffix is not None:
            payload["suffix"] = suffix
        
        # Make request
        response = self._client.request(
            "POST",
            "/v1/completions",
            json=payload,
            timeout=timeout,
        )
        
        # Parse response
        data = response.json()
        
        # Build CompletionResponse
        choices = [
            CompletionChoice(
                text=choice.get("text", ""),
                index=choice.get("index", i),
                finish_reason=choice.get("finish_reason"),
                logprobs=choice.get("logprobs"),
            )
            for i, choice in enumerate(data.get("choices", []))
        ]
        
        return CompletionResponse(
            id=data.get("id", ""),
            choices=choices,
            created=data.get("created", 0),
            model=data.get("model", model),
            object=data.get("object", "text_completion"),
            usage=data.get("usage"),
        )


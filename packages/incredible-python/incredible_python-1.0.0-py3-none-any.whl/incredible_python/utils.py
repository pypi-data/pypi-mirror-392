"""Utility functions for the Incredible Python SDK.

Provides helpers for common tasks like message formatting,
context management, retry logic, and token estimation.
"""

from __future__ import annotations

import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union

from ._exceptions import RateLimitError, APIConnectionError, APITimeoutError

T = TypeVar('T')


def format_messages(
    conversation: List[Union[str, Tuple[str, str], Dict[str, str]]]
) -> List[Dict[str, str]]:
    """Format conversation into proper message format.
    
    Converts various input formats into the standard message format
    expected by the API.
    
    Args:
        conversation: List of messages in various formats:
            - str: Converted to system message if first, else user message
            - (role, content): Tuple of role and content
            - {"role": ..., "content": ...}: Already formatted
    
    Returns:
        List of properly formatted message dicts
    
    Example:
        >>> messages = format_messages([
        ...     "You are a helpful assistant",  # System message
        ...     ("user", "What is Python?"),
        ...     ("assistant", "Python is a programming language"),
        ...     "Tell me more"  # User message
        ... ])
        >>> # Returns:
        >>> # [
        >>> #     {"role": "system", "content": "You are a helpful assistant"},
        >>> #     {"role": "user", "content": "What is Python?"},
        >>> #     {"role": "assistant", "content": "Python is a programming language"},
        >>> #     {"role": "user", "content": "Tell me more"}
        >>> # ]
    """
    formatted = []
    
    for i, msg in enumerate(conversation):
        if isinstance(msg, dict):
            # Already formatted
            formatted.append(msg)
        elif isinstance(msg, tuple):
            # (role, content) tuple
            role, content = msg
            formatted.append({"role": role, "content": content})
        elif isinstance(msg, str):
            # String - first message is system, rest are user
            role = "system" if i == 0 and not formatted else "user"
            formatted.append({"role": role, "content": msg})
        else:
            raise ValueError(f"Invalid message format: {type(msg)}")
    
    return formatted


def retry_on_error(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[type, ...] = (RateLimitError, APIConnectionError, APITimeoutError),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to automatically retry failed API calls.
    
    Retries with exponential backoff when specific exceptions occur.
    
    Args:
        max_attempts: Maximum number of attempts (including first try)
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay on each retry (exponential backoff)
        exceptions: Tuple of exception types to retry on
    
    Returns:
        Decorated function that will retry on failure
    
    Example:
        >>> @retry_on_error(max_attempts=3, delay=1.0)
        ... def call_api():
        ...     return client.messages.create(...)
        >>> 
        >>> # Will retry up to 3 times with exponential backoff
        >>> response = call_api()
        
        >>> # Custom retry configuration
        >>> @retry_on_error(
        ...     max_attempts=5,
        ...     delay=2.0,
        ...     backoff=3.0,
        ...     exceptions=(RateLimitError,)
        ... )
        ... def rate_limited_call():
        ...     return client.messages.create(...)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        # Last attempt, raise the exception
                        raise
                    
                    # Special handling for rate limit errors
                    if isinstance(e, RateLimitError) and e.retry_after:
                        wait_time = e.retry_after
                    else:
                        wait_time = current_delay
                    
                    print(f"Attempt {attempt + 1}/{max_attempts} failed: {e}")
                    print(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    
                    # Exponential backoff
                    current_delay *= backoff
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator


class ContextManager:
    """Manage conversation context within token limits.
    
    Automatically truncates older messages to stay within token limits
    while preserving system messages and recent context.
    
    Attributes:
        max_tokens: Maximum tokens to allow in context
        token_count: Current estimated token count
        messages: List of messages in context
    
    Example:
        >>> context = ContextManager(max_tokens=4000)
        >>> 
        >>> # Add messages
        >>> context.add_message("system", "You are a helpful assistant")
        >>> context.add_message("user", "Hello")
        >>> context.add_message("assistant", "Hi there!")
        >>> 
        >>> # Get messages that fit in context
        >>> messages = context.get_messages()
        >>> print(f"Using {context.token_count} tokens")
        >>> 
        >>> # Clear context
        >>> context.clear()
    """
    
    def __init__(self, max_tokens: int = 8000) -> None:
        """Initialize context manager.
        
        Args:
            max_tokens: Maximum tokens to allow in context (default: 8000)
        """
        self.max_tokens = max_tokens
        self.messages: List[Dict[str, str]] = []
        self._system_messages: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the context.
        
        Args:
            role: Message role ("system", "user", "assistant")
            content: Message content
        
        Example:
            >>> context.add_message("user", "What is AI?")
            >>> context.add_message("assistant", "AI is artificial intelligence...")
        """
        message = {"role": role, "content": content}
        
        if role == "system":
            self._system_messages.append(message)
        else:
            self.messages.append(message)
    
    def get_messages(self, preserve_recent: int = 10) -> List[Dict[str, str]]:
        """Get messages that fit within token limit.
        
        Preserves system messages and most recent messages,
        truncating older messages if needed.
        
        Args:
            preserve_recent: Minimum number of recent messages to keep
        
        Returns:
            List of messages that fit in context
        
        Example:
            >>> messages = context.get_messages(preserve_recent=5)
            >>> response = client.messages.create(
            ...     model="small-1",
            ...     max_tokens=200,
            ...     messages=messages
            ... )
        """
        all_messages = self._system_messages + self.messages
        
        # Rough token estimation (4 chars = 1 token)
        def estimate_tokens(msg: Dict[str, str]) -> int:
            return len(msg.get("content", "")) // 4 + 10  # +10 for overhead
        
        # Calculate current total
        total_tokens = sum(estimate_tokens(msg) for msg in all_messages)
        
        if total_tokens <= self.max_tokens:
            return all_messages
        
        # Need to truncate - keep system messages and recent messages
        result = self._system_messages.copy()
        recent_messages = self.messages[-preserve_recent:]
        
        # Add recent messages that fit
        current_total = sum(estimate_tokens(msg) for msg in result)
        
        for msg in recent_messages:
            msg_tokens = estimate_tokens(msg)
            if current_total + msg_tokens <= self.max_tokens:
                result.append(msg)
                current_total += msg_tokens
            else:
                break
        
        return result
    
    @property
    def token_count(self) -> int:
        """Estimate current token count.
        
        Returns:
            Estimated number of tokens in current context
        
        Example:
            >>> print(f"Context uses {context.token_count} tokens")
        """
        all_messages = self._system_messages + self.messages
        return sum(len(msg.get("content", "")) // 4 + 10 for msg in all_messages)
    
    def clear(self) -> None:
        """Clear all messages from context.
        
        Example:
            >>> context.clear()
            >>> print(context.token_count)  # 0
        """
        self.messages.clear()
        self._system_messages.clear()
    
    def __len__(self) -> int:
        """Get total number of messages.
        
        Returns:
            Total message count
        """
        return len(self._system_messages) + len(self.messages)


def estimate_tokens(text: str, method: str = "chars") -> int:
    """Estimate token count for text.
    
    Provides a rough estimate of tokens without making an API call.
    For accurate counts, use client.messages.count_tokens().
    
    Args:
        text: Text to estimate tokens for
        method: Estimation method:
            - "chars": 4 characters = 1 token (default, fast)
            - "words": 0.75 words = 1 token (more accurate for English)
    
    Returns:
        Estimated token count
    
    Example:
        >>> text = "Hello, how are you today?"
        >>> tokens = estimate_tokens(text)
        >>> print(f"Estimated {tokens} tokens")
        >>> 
        >>> # Word-based estimation
        >>> tokens = estimate_tokens(text, method="words")
    """
    if method == "chars":
        return len(text) // 4
    elif method == "words":
        words = len(text.split())
        return int(words * 1.33)  # ~0.75 words per token
    else:
        raise ValueError(f"Unknown method: {method}")


def estimate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """Estimate cost for API request.
    
    Note: Prices are estimates and may change. Check official pricing
    at https://incredible.one/pricing for current rates.
    
    Args:
        model: Model identifier ("small-1", "medium-1", "large-1")
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
    
    Returns:
        Estimated cost in USD
    
    Example:
        >>> cost = estimate_cost(
        ...     model="small-1",
        ...     input_tokens=1000,
        ...     output_tokens=500
        ... )
        >>> print(f"Estimated cost: ${cost:.4f}")
    """
    # Pricing per 1M tokens (example rates - update with actual pricing)
    pricing = {
        "small-1": {"input": 0.50, "output": 1.50},    # $0.50/$1.50 per 1M tokens
        "medium-1": {"input": 2.00, "output": 6.00},   # $2/$6 per 1M tokens
        "large-1": {"input": 5.00, "output": 15.00},   # $5/$15 per 1M tokens
    }
    
    if model not in pricing:
        raise ValueError(f"Unknown model: {model}")
    
    rates = pricing[model]
    input_cost = (input_tokens / 1_000_000) * rates["input"]
    output_cost = (output_tokens / 1_000_000) * rates["output"]
    
    return input_cost + output_cost


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 100,
) -> List[str]:
    """Split text into overlapping chunks.
    
    Useful for processing long documents that exceed context limits.
    
    Args:
        text: Text to split into chunks
        chunk_size: Target size for each chunk (in characters)
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of text chunks
    
    Example:
        >>> long_text = "..." * 10000  # Very long text
        >>> chunks = chunk_text(long_text, chunk_size=2000, overlap=200)
        >>> 
        >>> # Process each chunk
        >>> for i, chunk in enumerate(chunks):
        ...     response = client.messages.create(
        ...         model="small-1",
        ...         max_tokens=500,
        ...         messages=[{"role": "user", "content": f"Summarize: {chunk}"}]
        ...     )
        ...     print(f"Chunk {i+1}: {response.content[0]['text']}")
    """
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")
    
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    
    return chunks


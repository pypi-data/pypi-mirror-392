"""Incredible Python SDK - Anthropics compatible client.

Provides an Anthropic-compatible interface to the Incredible API with
enhanced error handling, utilities, and developer experience improvements.

Example:
    >>> from incredible_python import Incredible
    >>> 
    >>> client = Incredible()
    >>> response = client.messages.create(
    ...     model="small-1",
    ...     max_tokens=200,
    ...     messages=[{"role": "user", "content": "Hello!"}]
    ... )
    >>> print(response.content[0]["text"])

Error Handling:
    >>> from incredible_python._exceptions import RateLimitError, NotFoundError
    >>> 
    >>> try:
    ...     response = client.messages.create(...)
    ... except RateLimitError as e:
    ...     print(f"Rate limited. Retry after {e.retry_after}s")
    ... except NotFoundError as e:
    ...     print(f"Resource not found: {e.message}")

Utilities:
    >>> from incredible_python import utils
    >>> 
    >>> # Format messages
    >>> messages = utils.format_messages([
    ...     "You are helpful",
    ...     ("user", "Hello"),
    ... ])
    >>> 
    >>> # Manage context
    >>> context = utils.ContextManager(max_tokens=4000)
    >>> context.add_message("user", "Hello")
    >>> messages = context.get_messages()
"""

# Load environment variables from .env file automatically
from dotenv import load_dotenv
load_dotenv()

from .client import Incredible
from . import helpers
from . import utils
from ._exceptions import (
    IncredibleError,
    APIError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    InternalServerError,
    APIConnectionError,
    APITimeoutError,
    APIResponseValidationError,
)

__all__ = [
    "Incredible",
    "helpers",
    "utils",
    # Exceptions
    "IncredibleError",
    "APIError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
    "InternalServerError",
    "APIConnectionError",
    "APITimeoutError",
    "APIResponseValidationError",
]
__version__ = "1.0.0"

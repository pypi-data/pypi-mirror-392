"""Exception hierarchy for the Incredible Python SDK.

All exceptions inherit from IncredibleError for easy catching:
    try:
        response = client.messages.create(...)
    except IncredibleError as e:
        print(f"SDK error: {e}")
"""

from __future__ import annotations
from typing import Any, Dict, Optional


class IncredibleError(Exception):
    """Base exception for the Incredible SDK.
    
    All SDK exceptions inherit from this, allowing you to catch
    any SDK-related error with a single except block.
    
    Attributes:
        message: Human-readable error message
        request_id: Unique identifier for the request (if available)
    
    Example:
        >>> try:
        ...     response = client.messages.create(...)
        ... except IncredibleError as e:
        ...     print(f"Error: {e}")
        ...     if hasattr(e, 'request_id'):
        ...         print(f"Request ID: {e.request_id}")
    """
    
    def __init__(self, message: str, request_id: Optional[str] = None) -> None:
        self.message = message
        self.request_id = request_id
        super().__init__(message)


class APIError(IncredibleError):
    """Raised when the API returns a non-success status code.
    
    Attributes:
        status_code: HTTP status code (e.g., 400, 500)
        message: Error message from the API
        request_id: Unique request identifier
        error_type: Error type/code from API (if provided)
        error_details: Additional error details (if provided)
    
    Example:
        >>> try:
        ...     response = client.messages.create(...)
        ... except APIError as e:
        ...     print(f"API error {e.status_code}: {e.message}")
        ...     print(f"Request ID: {e.request_id}")
        ...     if e.error_details:
        ...         print(f"Details: {e.error_details}")
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        request_id: Optional[str] = None,
        error_type: Optional[str] = None,
        error_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.status_code = status_code
        self.error_type = error_type
        self.error_details = error_details or {}
        super().__init__(message, request_id)


class AuthenticationError(APIError):
    """Raised when API key is invalid or missing (401).
    
    Example:
        >>> try:
        ...     client = Incredible(api_key="invalid_key")
        ...     response = client.messages.create(...)
        ... except AuthenticationError as e:
        ...     print("Invalid API key. Please check your credentials.")
        ...     print(f"Request ID: {e.request_id}")
    """
    
    def __init__(
        self,
        message: str = "Invalid or missing API key",
        request_id: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(
            status_code=401,
            message=message,
            request_id=request_id,
            error_type="authentication_error",
            **kwargs
        )


class PermissionDeniedError(APIError):
    """Raised when the API key lacks required permissions (403).
    
    Example:
        >>> try:
        ...     response = client.messages.create(...)
        ... except PermissionDeniedError as e:
        ...     print("Your API key doesn't have access to this resource")
        ...     print(f"Required permission: {e.error_details.get('required_permission')}")
    """
    
    def __init__(
        self,
        message: str = "Permission denied",
        request_id: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(
            status_code=403,
            message=message,
            request_id=request_id,
            error_type="permission_denied",
            **kwargs
        )


class NotFoundError(APIError):
    """Raised when the requested resource is not found (404).
    
    Example:
        >>> try:
        ...     integration = client.integrations.retrieve("nonexistent_id")
        ... except NotFoundError as e:
        ...     print(f"Integration not found: {e.message}")
        ...     print(f"Request ID: {e.request_id}")
    """
    
    def __init__(
        self,
        message: str = "Resource not found",
        request_id: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(
            status_code=404,
            message=message,
            request_id=request_id,
            error_type="not_found",
            **kwargs
        )


class RateLimitError(APIError):
    """Raised when rate limit is exceeded (429).
    
    Attributes:
        retry_after: Seconds to wait before retrying (if provided by API)
        limit: Rate limit (requests per period)
        remaining: Remaining requests in current period
        reset_at: Unix timestamp when limit resets
    
    Example:
        >>> try:
        ...     response = client.messages.create(...)
        ... except RateLimitError as e:
        ...     print(f"Rate limited. Retry after {e.retry_after}s")
        ...     time.sleep(e.retry_after)
        ...     # Retry the request
    """
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        request_id: Optional[str] = None,
        retry_after: Optional[int] = None,
        limit: Optional[int] = None,
        remaining: Optional[int] = None,
        reset_at: Optional[int] = None,
        **kwargs
    ) -> None:
        self.retry_after = retry_after or 60  # Default to 60s
        self.limit = limit
        self.remaining = remaining
        self.reset_at = reset_at
        
        super().__init__(
            status_code=429,
            message=message,
            request_id=request_id,
            error_type="rate_limit_exceeded",
            **kwargs
        )


class ValidationError(APIError):
    """Raised when request parameters are invalid (422).
    
    Attributes:
        validation_errors: List of validation error details
    
    Example:
        >>> try:
        ...     response = client.messages.create(
        ...         model="small-1",
        ...         max_tokens=-100,  # Invalid
        ...         messages=[]
        ...     )
        ... except ValidationError as e:
        ...     print("Validation errors:")
        ...     for error in e.validation_errors:
        ...         print(f"  - {error['field']}: {error['message']}")
    """
    
    def __init__(
        self,
        message: str = "Validation error",
        request_id: Optional[str] = None,
        validation_errors: Optional[list] = None,
        **kwargs
    ) -> None:
        self.validation_errors = validation_errors or []
        super().__init__(
            status_code=422,
            message=message,
            request_id=request_id,
            error_type="validation_error",
            error_details={"validation_errors": validation_errors},
            **kwargs
        )


class InternalServerError(APIError):
    """Raised when the API encounters an internal error (500).
    
    Example:
        >>> try:
        ...     response = client.messages.create(...)
        ... except InternalServerError as e:
        ...     print(f"Server error: {e.message}")
        ...     print(f"Request ID: {e.request_id}")
        ...     print("Please try again later or contact support")
    """
    
    def __init__(
        self,
        message: str = "Internal server error",
        request_id: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(
            status_code=500,
            message=message,
            request_id=request_id,
            error_type="internal_server_error",
            **kwargs
        )


class APIConnectionError(IncredibleError):
    """Raised when the SDK cannot reach the Incredible API.
    
    This typically indicates network issues or that the API is unreachable.
    
    Example:
        >>> try:
        ...     response = client.messages.create(...)
        ... except APIConnectionError as e:
        ...     print("Cannot connect to API. Check your internet connection.")
        ...     print(f"Error: {e}")
    """
    pass


class APITimeoutError(APIConnectionError):
    """Raised when a request to the API times out.
    
    Attributes:
        timeout: The timeout value that was exceeded (in seconds)
    
    Example:
        >>> try:
        ...     response = client.messages.create(...)
        ... except APITimeoutError as e:
        ...     print(f"Request timed out after {e.timeout}s")
        ...     print("Try increasing the timeout or check API status")
    """
    
    def __init__(
        self,
        message: str = "Request timed out",
        timeout: Optional[float] = None,
        request_id: Optional[str] = None,
    ) -> None:
        self.timeout = timeout
        super().__init__(message, request_id)


class APIResponseValidationError(IncredibleError):
    """Raised when the SDK cannot parse the API response.
    
    This usually indicates a mismatch between expected and actual response format.
    
    Attributes:
        raw_response: The raw response that couldn't be parsed (if available)
    
    Example:
        >>> try:
        ...     response = client.messages.create(...)
        ... except APIResponseValidationError as e:
        ...     print(f"Cannot parse API response: {e}")
        ...     if hasattr(e, 'raw_response'):
        ...         print(f"Raw response: {e.raw_response}")
    """
    
    def __init__(
        self,
        message: str,
        request_id: Optional[str] = None,
        raw_response: Optional[Any] = None,
    ) -> None:
        self.raw_response = raw_response
        super().__init__(message, request_id)

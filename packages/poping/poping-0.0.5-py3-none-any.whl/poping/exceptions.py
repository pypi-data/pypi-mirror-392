"""
Poping SDK Exceptions
"""


class PopingError(Exception):
    """Base exception for all Poping errors"""
    pass


class AuthenticationError(PopingError):
    """Authentication failed - invalid API key or credentials"""
    pass


class ToolExecutionError(PopingError):
    """Tool execution failed"""

    def __init__(self, tool_name: str, message: str, details: dict = None):
        self.tool_name = tool_name
        self.details = details or {}
        super().__init__(f"Tool '{tool_name}' failed: {message}")


class RateLimitError(PopingError):
    """Rate limit exceeded"""

    def __init__(self, retry_after: int = None):
        self.retry_after = retry_after
        message = "Rate limit exceeded"
        if retry_after:
            message += f", retry after {retry_after}s"
        super().__init__(message)


class ValidationError(PopingError):
    """Input validation failed"""
    pass


class ResourceNotFoundError(PopingError):
    """Requested resource not found"""
    pass


class APIError(PopingError):
    """Backend API error"""

    def __init__(self, status_code: int, message: str, details: dict = None):
        self.status_code = status_code
        self.details = details or {}
        super().__init__(f"API error {status_code}: {message}")

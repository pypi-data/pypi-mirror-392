"""Custom exceptions for PromptGuard."""
from typing import Optional, Any


class PromptGuardError(Exception):
    """Base exception for PromptGuard."""
    pass


class PromptExecutionError(PromptGuardError):
    """Error during prompt execution."""
    
    def __init__(self, message: str, attempts: list[dict], last_error: Exception):
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(message)


class ValidationError(PromptGuardError):
    """Response validation failed."""
    
    def __init__(self, message: str, validation_results: dict):
        self.validation_results = validation_results
        super().__init__(message)


class ModelNotFoundError(PromptGuardError):
    """Requested model not available."""
    pass


class RateLimitError(PromptGuardError):
    """Rate limit exceeded."""
    
    def __init__(self, retry_after: Optional[float] = None):
        self.retry_after = retry_after
        message = f"Rate limit exceeded. Retry after {retry_after}s" if retry_after else "Rate limit exceeded"
        super().__init__(message)


class TimeoutError(PromptGuardError):
    """Request timed out."""
    pass


class ProviderError(PromptGuardError):
    """Provider-specific error."""
    
    def __init__(self, provider: str, message: str, original_error: Optional[Exception] = None):
        self.provider = provider
        self.original_error = original_error
        super().__init__(f"Error from {provider}: {message}")


class InvalidConfigurationError(PromptGuardError):
    """Invalid configuration provided."""
    pass


class CacheError(PromptGuardError):
    """Error during cache operation."""
    pass

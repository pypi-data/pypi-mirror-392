"""Retry strategies for PromptGuard."""
from abc import ABC, abstractmethod
from typing import Callable, Optional
import asyncio


class RetryStrategy(ABC):
    """Base class for retry strategies."""
    
    @abstractmethod
    def get_delay(self, attempt: int, error: Exception) -> float:
        """Calculate delay before next retry.
        
        Args:
            attempt: Attempt number (0-indexed)
            error: Exception that occurred
            
        Returns:
            Delay in seconds
        """
        pass
    
    @abstractmethod
    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Determine if should retry.
        
        Args:
            attempt: Attempt number
            error: Exception that occurred
            
        Returns:
            True if should retry
        """
        pass


class ExponentialBackoff(RetryStrategy):
    """Exponential backoff: 1s, 2s, 4s, 8s..."""
    
    def __init__(self, base: float = 1.0, max_delay: float = 60.0, max_retries: int = 3):
        self.base = base
        self.max_delay = max_delay
        self.max_retries = max_retries
    
    def get_delay(self, attempt: int, error: Exception) -> float:
        """Calculate exponential backoff delay."""
        delay = self.base * (2 ** attempt)
        return min(delay, self.max_delay)
    
    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Retry up to max_retries."""
        return attempt < self.max_retries


class FibonacciBackoff(RetryStrategy):
    """Fibonacci backoff: 1s, 1s, 2s, 3s, 5s, 8s..."""
    
    def __init__(self, base: float = 1.0, max_delay: float = 60.0, max_retries: int = 3):
        self.base = base
        self.max_delay = max_delay
        self.max_retries = max_retries
        self._fib_sequence = self._generate_fibonacci()
    
    @staticmethod
    def _generate_fibonacci():
        """Generate Fibonacci sequence."""
        a, b = 1, 1
        while True:
            yield a
            a, b = b, a + b
    
    def get_delay(self, attempt: int, error: Exception) -> float:
        """Calculate Fibonacci backoff delay."""
        # Get the nth Fibonacci number
        fib_num = next(iter(list(self._fib_sequence)[:attempt + 1]))
        delay = self.base * fib_num
        return min(delay, self.max_delay)
    
    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Retry up to max_retries."""
        return attempt < self.max_retries


class ConstantDelay(RetryStrategy):
    """Fixed delay between retries."""
    
    def __init__(self, delay: float = 1.0, max_retries: int = 3):
        self.delay = delay
        self.max_retries = max_retries
    
    def get_delay(self, attempt: int, error: Exception) -> float:
        """Return constant delay."""
        return self.delay
    
    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Retry up to max_retries."""
        return attempt < self.max_retries


class CustomRetryStrategy(RetryStrategy):
    """User-defined retry logic."""
    
    def __init__(
        self,
        delay_func: Callable[[int, Exception], float],
        should_retry_func: Optional[Callable[[int, Exception], bool]] = None
    ):
        """Initialize custom retry strategy.
        
        Args:
            delay_func: Function that returns delay in seconds
            should_retry_func: Function that determines if should retry
        """
        self.delay_func = delay_func
        self.should_retry_func = should_retry_func or (lambda attempt, error: True)
    
    def get_delay(self, attempt: int, error: Exception) -> float:
        """Get delay from custom function."""
        return self.delay_func(attempt, error)
    
    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Get retry decision from custom function."""
        return self.should_retry_func(attempt, error)


class LinearBackoff(RetryStrategy):
    """Linear backoff: 1s, 2s, 3s, 4s..."""
    
    def __init__(self, base: float = 1.0, max_delay: float = 60.0, max_retries: int = 3):
        self.base = base
        self.max_delay = max_delay
        self.max_retries = max_retries
    
    def get_delay(self, attempt: int, error: Exception) -> float:
        """Calculate linear backoff delay."""
        delay = self.base * (attempt + 1)
        return min(delay, self.max_delay)
    
    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Retry up to max_retries."""
        return attempt < self.max_retries

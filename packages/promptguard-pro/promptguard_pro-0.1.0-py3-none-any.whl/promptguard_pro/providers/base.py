"""Base provider interface for LLM providers."""
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Optional, Dict, List
import asyncio


class BaseProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize provider.
        
        Args:
            api_key: API key for the provider
            **kwargs: Provider-specific configuration
        """
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    async def execute(
        self,
        messages: List[dict],
        model: str,
        temperature: float = 0.01,
        max_tokens: int = 4096,
        **kwargs
    ) -> dict:
        """Execute prompt and return standardized response.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum output tokens
            **kwargs: Provider-specific arguments
            
        Returns:
            Dict with keys:
                - content: str (response text)
                - model: str (model used)
                - usage: dict (tokens used)
                - raw: Any (provider-specific response)
        """
        pass
    
    @abstractmethod
    async def stream(
        self,
        messages: List[dict],
        model: str,
        temperature: float = 0.01,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream response chunks.
        
        Args:
            messages: List of message dicts
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum output tokens
            **kwargs: Provider-specific arguments
            
        Yields:
            Response chunks as strings
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens for given text and model.
        
        Args:
            text: Text to count tokens for
            model: Model identifier
            
        Returns:
            Number of tokens
        """
        pass
    
    @abstractmethod
    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str
    ) -> float:
        """Estimate cost based on token usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model identifier
            
        Returns:
            Estimated cost in USD
        """
        pass
    
    @abstractmethod
    def parse_response(self, raw_response: Any) -> dict:
        """Parse provider-specific response to standard format.
        
        Args:
            raw_response: Provider-specific response object
            
        Returns:
            Standardized response dict
        """
        pass
    
    @property
    @abstractmethod
    def supported_models(self) -> List[str]:
        """List of supported model identifiers.
        
        Returns:
            List of model identifiers
        """
        pass
    
    async def validate_connection(self) -> bool:
        """Validate that provider is accessible.
        
        Returns:
            True if connection is valid
            
        Raises:
            Exception if connection fails
        """
        try:
            # Try a simple operation - subclasses can override
            return True
        except Exception:
            return False

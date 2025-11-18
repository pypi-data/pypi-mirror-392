"""Anthropic Claude provider for PromptGuard."""
import os
from typing import Any, AsyncIterator, List, Optional, Dict

from promptguard.providers.base import BaseProvider
from promptguard.exceptions import ProviderError, RateLimitError
from promptguard.core.models import get_model_info, MODEL_REGISTRY


class AnthropicProvider(BaseProvider):
    """Provider for Anthropic Claude models."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            **kwargs: Additional configuration
        """
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        super().__init__(api_key=api_key, **kwargs)
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.async_client = anthropic.AsyncAnthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic package is required. Install with: pip install anthropic")
    
    async def execute(
        self,
        messages: List[dict],
        model: str,
        temperature: float = 0.01,
        max_tokens: int = 4096,
        **kwargs
    ) -> dict:
        """Execute prompt using Anthropic API.
        
        Args:
            messages: List of message dicts
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum output tokens
            **kwargs: Additional arguments
            
        Returns:
            Standardized response dict
        """
        try:
            model_info = get_model_info(f"anthropic/{model.split('/')[-1]}")
            model_id = model_info.id
        except ValueError:
            # If not found by full identifier, try with the model name directly
            model_id = model.split("/")[-1]
        
        try:
            response = await self.async_client.messages.create(
                model=model_id,
                max_tokens=max_tokens,
                messages=messages,
                temperature=temperature,
                **kwargs
            )
            
            return {
                "content": response.content[0].text,
                "model": model_id,
                "usage": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens,
                    "total": response.usage.input_tokens + response.usage.output_tokens,
                },
                "raw": response,
            }
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError(retry_after=60)
            raise ProviderError("anthropic", str(e), e)
    
    async def stream(
        self,
        messages: List[dict],
        model: str,
        temperature: float = 0.01,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream response from Anthropic API.
        
        Args:
            messages: List of message dicts
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum output tokens
            **kwargs: Additional arguments
            
        Yields:
            Response chunks as strings
        """
        try:
            model_info = get_model_info(f"anthropic/{model.split('/')[-1]}")
            model_id = model_info.id
        except ValueError:
            model_id = model.split("/")[-1]
        
        try:
            with self.async_client.messages.stream(
                model=model_id,
                max_tokens=max_tokens,
                messages=messages,
                temperature=temperature,
                **kwargs
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError(retry_after=60)
            raise ProviderError("anthropic", str(e), e)
    
    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens using Anthropic's counter.
        
        Args:
            text: Text to count
            model: Model identifier
            
        Returns:
            Number of tokens
        """
        try:
            return self.client.beta.messages.count_tokens(
                model=model.split("/")[-1],
                messages=[{"role": "user", "content": text}],
            ).input_tokens
        except Exception as e:
            raise ProviderError("anthropic", f"Token counting failed: {str(e)}", e)
    
    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str
    ) -> float:
        """Estimate cost for Anthropic API usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model identifier
            
        Returns:
            Estimated cost in USD
        """
        try:
            model_info = get_model_info(f"anthropic/{model.split('/')[-1]}")
            input_cost = (input_tokens / 1000) * model_info.input_cost_per_1k
            output_cost = (output_tokens / 1000) * model_info.output_cost_per_1k
            return input_cost + output_cost
        except ValueError:
            return 0.0
    
    def parse_response(self, raw_response: Any) -> dict:
        """Parse Anthropic response.
        
        Args:
            raw_response: Anthropic response object
            
        Returns:
            Parsed response dict
        """
        return {
            "content": raw_response.content[0].text,
            "model": raw_response.model,
            "usage": {
                "input": raw_response.usage.input_tokens,
                "output": raw_response.usage.output_tokens,
            }
        }
    
    @property
    def supported_models(self) -> List[str]:
        """Get supported Anthropic models.
        
        Returns:
            List of model identifiers
        """
        return [
            "anthropic/claude-3-5-sonnet",
            "anthropic/claude-3-opus",
            "anthropic/claude-3-sonnet",
            "anthropic/claude-3-haiku",
        ]
    
    async def validate_connection(self) -> bool:
        """Validate Anthropic connection."""
        try:
            await self.async_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}],
            )
            return True
        except Exception:
            return False

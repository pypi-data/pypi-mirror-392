"""OpenAI provider for PromptGuard."""
import os
from typing import Any, AsyncIterator, List, Optional, Dict

from promptguard.providers.base import BaseProvider
from promptguard.exceptions import ProviderError, RateLimitError
from promptguard.core.models import get_model_info


class OpenAIProvider(BaseProvider):
    """Provider for OpenAI GPT models."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            **kwargs: Additional configuration
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        super().__init__(api_key=api_key, **kwargs)
        
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")
    
    async def execute(
        self,
        messages: List[dict],
        model: str,
        temperature: float = 0.01,
        max_tokens: int = 4096,
        **kwargs
    ) -> dict:
        """Execute prompt using OpenAI API."""
        try:
            model_id = model.split("/")[-1]
            
            response = await self.client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return {
                "content": response.choices[0].message.content,
                "model": model_id,
                "usage": {
                    "input": response.usage.prompt_tokens,
                    "output": response.usage.completion_tokens,
                    "total": response.usage.total_tokens,
                },
                "raw": response,
            }
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError(retry_after=60)
            raise ProviderError("openai", str(e), e)
    
    async def stream(
        self,
        messages: List[dict],
        model: str,
        temperature: float = 0.01,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream response from OpenAI API."""
        try:
            model_id = model.split("/")[-1]
            
            stream = await self.client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError(retry_after=60)
            raise ProviderError("openai", str(e), e)
    
    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens for OpenAI models."""
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(model.split("/")[-1])
            return len(encoding.encode(text))
        except Exception as e:
            raise ProviderError("openai", f"Token counting failed: {str(e)}", e)
    
    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str
    ) -> float:
        """Estimate cost for OpenAI API usage."""
        try:
            model_info = get_model_info(model)
            input_cost = (input_tokens / 1000) * model_info.input_cost_per_1k
            output_cost = (output_tokens / 1000) * model_info.output_cost_per_1k
            return input_cost + output_cost
        except ValueError:
            return 0.0
    
    def parse_response(self, raw_response: Any) -> dict:
        """Parse OpenAI response."""
        return {
            "content": raw_response.choices[0].message.content,
            "model": raw_response.model,
            "usage": {
                "input": raw_response.usage.prompt_tokens,
                "output": raw_response.usage.completion_tokens,
            }
        }
    
    @property
    def supported_models(self) -> List[str]:
        """Get supported OpenAI models."""
        return [
            "openai/gpt-4o",
            "openai/gpt-4-turbo",
            "openai/gpt-4",
            "openai/gpt-3.5-turbo",
        ]
    
    async def validate_connection(self) -> bool:
        """Validate OpenAI connection."""
        try:
            await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10,
            )
            return True
        except Exception:
            return False

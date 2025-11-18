"""Groq provider for PromptGuard."""
import os
from typing import Any, AsyncIterator, List, Optional

from promptguard_pro.providers.base import BaseProvider
from promptguard_pro.exceptions import ProviderError, RateLimitError


class GroqProvider(BaseProvider):
    """Provider for Groq LLaMA and Mixtral models."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize Groq provider.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            **kwargs: Additional configuration
        """
        api_key = api_key or os.getenv("GROQ_API_KEY")
        super().__init__(api_key=api_key, **kwargs)
        
        try:
            from groq import AsyncGroq
            self.client = AsyncGroq(api_key=self.api_key)
        except ImportError:
            raise ImportError("groq package is required. Install with: pip install groq")
    
    async def execute(
        self,
        messages: List[dict],
        model: str,
        temperature: float = 0.01,
        max_tokens: int = 4096,
        **kwargs
    ) -> dict:
        """Execute prompt using Groq API."""
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
            raise ProviderError("groq", str(e), e)
    
    async def stream(
        self,
        messages: List[dict],
        model: str,
        temperature: float = 0.01,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream response from Groq API."""
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
            raise ProviderError("groq", str(e), e)
    
    def count_tokens(self, text: str, model: str) -> int:
        """Estimate tokens for Groq models."""
        # Groq models are largely compatible with LLaMA tokenizer
        try:
            import tiktoken
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except Exception:
            # Fallback: rough estimate of 1 token per 4 characters
            return len(text) // 4
    
    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str
    ) -> float:
        """Groq models are currently free tier."""
        return 0.0
    
    def parse_response(self, raw_response: Any) -> dict:
        """Parse Groq response."""
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
        """Get supported Groq models."""
        return [
            "groq/llama-3-70b",
            "groq/llama-2-70b",
            "groq/mixtral-8x7b",
        ]
    
    async def validate_connection(self) -> bool:
        """Validate Groq connection."""
        try:
            await self.client.chat.completions.create(
                model="llama-3-70b-8192",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10,
            )
            return True
        except Exception:
            return False

"""Cohere provider for PromptGuard."""
import os
from typing import Any, AsyncIterator, List, Optional

from promptguard_pro.providers.base import BaseProvider
from promptguard_pro.exceptions import ProviderError, RateLimitError


class CohereProvider(BaseProvider):
    """Provider for Cohere Command models."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize Cohere provider.
        
        Args:
            api_key: Cohere API key (defaults to COHERE_API_KEY env var)
            **kwargs: Additional configuration
        """
        api_key = api_key or os.getenv("COHERE_API_KEY")
        super().__init__(api_key=api_key, **kwargs)
        
        try:
            import cohere
            self.client = cohere.AsyncClient(api_key=self.api_key)
        except ImportError:
            raise ImportError("cohere package is required. Install with: pip install cohere")
    
    async def execute(
        self,
        messages: List[dict],
        model: str,
        temperature: float = 0.01,
        max_tokens: int = 4096,
        **kwargs
    ) -> dict:
        """Execute prompt using Cohere API."""
        try:
            model_id = model.split("/")[-1]
            
            # Convert messages to Cohere format
            chat_history = self._convert_messages_to_history(messages[:-1])
            user_message = messages[-1]["content"]
            
            response = await self.client.chat(
                model=model_id,
                message=user_message,
                chat_history=chat_history,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return {
                "content": response.text,
                "model": model_id,
                "usage": {
                    "input": 0,  # Cohere doesn't provide token count in response
                    "output": 0,
                    "total": 0,
                },
                "raw": response,
            }
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError(retry_after=60)
            raise ProviderError("cohere", str(e), e)
    
    async def stream(
        self,
        messages: List[dict],
        model: str,
        temperature: float = 0.01,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream response from Cohere API."""
        try:
            model_id = model.split("/")[-1]
            
            chat_history = self._convert_messages_to_history(messages[:-1])
            user_message = messages[-1]["content"]
            
            stream = await self.client.chat_stream(
                model=model_id,
                message=user_message,
                chat_history=chat_history,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            async for event in stream:
                if hasattr(event, 'text'):
                    yield event.text
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError(retry_after=60)
            raise ProviderError("cohere", str(e), e)
    
    def count_tokens(self, text: str, model: str) -> int:
        """Estimate tokens for Cohere models."""
        # Rough estimate: 1 token per 4 characters
        return len(text) // 4
    
    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str
    ) -> float:
        """Estimate cost for Cohere API."""
        try:
            from promptguard_pro.core.models import get_model_info
            model_info = get_model_info(model)
            input_cost = (input_tokens / 1000) * model_info.input_cost_per_1k
            output_cost = (output_tokens / 1000) * model_info.output_cost_per_1k
            return input_cost + output_cost
        except ValueError:
            return 0.0
    
    def parse_response(self, raw_response: Any) -> dict:
        """Parse Cohere response."""
        return {
            "content": raw_response.text,
            "model": raw_response.model,
        }
    
    @property
    def supported_models(self) -> List[str]:
        """Get supported Cohere models."""
        return [
            "cohere/command-r-plus",
            "cohere/command-r",
        ]
    
    def _convert_messages_to_history(self, messages: List[dict]) -> List[Any]:
        """Convert OpenAI-style messages to Cohere chat history format."""
        try:
            import cohere
            history = []
            for msg in messages:
                history.append(
                    cohere.ChatMessage(
                        role=msg["role"],
                        message=msg["content"]
                    )
                )
            return history
        except Exception:
            return []
    
    async def validate_connection(self) -> bool:
        """Validate Cohere connection."""
        try:
            response = await self.client.chat(
                model="command-r",
                message="test",
            )
            return bool(response.text)
        except Exception:
            return False

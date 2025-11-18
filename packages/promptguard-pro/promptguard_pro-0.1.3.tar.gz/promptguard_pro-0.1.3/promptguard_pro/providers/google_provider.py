"""Google Gemini provider for PromptGuard."""
import os
from typing import Any, AsyncIterator, List, Optional

from promptguard_pro.providers.base import BaseProvider
from promptguard_pro.exceptions import ProviderError, RateLimitError


class GoogleProvider(BaseProvider):
    """Provider for Google Gemini models."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize Google provider.
        
        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            **kwargs: Additional configuration
        """
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        super().__init__(api_key=api_key, **kwargs)
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.genai = genai
        except ImportError:
            raise ImportError("google-generativeai package is required. Install with: pip install google-generativeai")
    
    async def execute(
        self,
        messages: List[dict],
        model: str,
        temperature: float = 0.01,
        max_tokens: int = 4096,
        **kwargs
    ) -> dict:
        """Execute prompt using Google Gemini API."""
        try:
            model_id = model.split("/")[-1]
            model_obj = self.genai.GenerativeModel(model_id)
            
            # Convert messages to Gemini format
            contents = self._convert_messages(messages)
            
            response = await model_obj.generate_content_async(
                contents,
                generation_config=self.genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
                **kwargs
            )
            
            return {
                "content": response.text,
                "model": model_id,
                "usage": {
                    "input": response.usage_metadata.prompt_token_count,
                    "output": response.usage_metadata.candidates_token_count,
                    "total": response.usage_metadata.total_token_count,
                },
                "raw": response,
            }
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError(retry_after=60)
            raise ProviderError("google", str(e), e)
    
    async def stream(
        self,
        messages: List[dict],
        model: str,
        temperature: float = 0.01,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream response from Google Gemini API."""
        try:
            model_id = model.split("/")[-1]
            model_obj = self.genai.GenerativeModel(model_id)
            
            contents = self._convert_messages(messages)
            
            stream = await model_obj.generate_content_async(
                contents,
                stream=True,
                generation_config=self.genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError(retry_after=60)
            raise ProviderError("google", str(e), e)
    
    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens for Google models."""
        try:
            model_id = model.split("/")[-1]
            model_obj = self.genai.GenerativeModel(model_id)
            response = model_obj.count_tokens(text)
            return response.total_tokens
        except Exception:
            # Fallback: rough estimate
            return len(text) // 4
    
    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str
    ) -> float:
        """Estimate cost for Google Gemini API."""
        try:
            from promptguard_pro.core.models import get_model_info
            model_info = get_model_info(model)
            input_cost = (input_tokens / 1000) * model_info.input_cost_per_1k
            output_cost = (output_tokens / 1000) * model_info.output_cost_per_1k
            return input_cost + output_cost
        except ValueError:
            return 0.0
    
    def parse_response(self, raw_response: Any) -> dict:
        """Parse Google response."""
        return {
            "content": raw_response.text,
            "model": raw_response.model_version,
            "usage": {
                "input": raw_response.usage_metadata.prompt_token_count,
                "output": raw_response.usage_metadata.candidates_token_count,
            }
        }
    
    @property
    def supported_models(self) -> List[str]:
        """Get supported Google models."""
        return [
            "google/gemini-1.5-pro",
            "google/gemini-1.5-flash",
        ]
    
    def _convert_messages(self, messages: List[dict]) -> List[Any]:
        """Convert OpenAI-style messages to Google format."""
        contents = []
        for msg in messages:
            role = "model" if msg["role"] == "assistant" else "user"
            contents.append(self.genai.types.Content(role=role, parts=[self.genai.types.Part(text=msg["content"])]))
        return contents
    
    async def validate_connection(self) -> bool:
        """Validate Google connection."""
        try:
            model_obj = self.genai.GenerativeModel("gemini-1.5-flash")
            response = await model_obj.generate_content_async("test", stream=False)
            return bool(response.text)
        except Exception:
            return False

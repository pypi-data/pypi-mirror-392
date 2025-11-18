"""Provider factory for PromptGuard."""
from typing import Optional, Type, Dict

from promptguard_pro.providers.base import BaseProvider
from promptguard_pro.providers.anthropic_provider import AnthropicProvider
from promptguard_pro.providers.openai_provider import OpenAIProvider
from promptguard_pro.providers.groq_provider import GroqProvider
from promptguard_pro.providers.cohere_provider import CohereProvider
from promptguard_pro.providers.google_provider import GoogleProvider
from promptguard_pro.exceptions import ModelNotFoundError


PROVIDER_MAP: Dict[str, Type[BaseProvider]] = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "groq": GroqProvider,
    "cohere": CohereProvider,
    "google": GoogleProvider,
}


def get_provider(model: str, **kwargs) -> BaseProvider:
    """Get provider instance for a model.
    
    Args:
        model: Model identifier (e.g., "anthropic/claude-3-5-sonnet")
        **kwargs: Provider configuration
        
    Returns:
        Provider instance
        
    Raises:
        ModelNotFoundError: If model not supported
    """
    if "/" not in model:
        raise ValueError(f"Invalid model format: {model}. Use 'provider/model'")
    
    provider_name = model.split("/")[0].lower()
    
    if provider_name not in PROVIDER_MAP:
        raise ModelNotFoundError(f"Provider '{provider_name}' not found. Available: {list(PROVIDER_MAP.keys())}")
    
    provider_class = PROVIDER_MAP[provider_name]
    return provider_class(**kwargs)


def register_provider(name: str, provider_class: Type[BaseProvider]) -> None:
    """Register a custom provider.
    
    Args:
        name: Provider name
        provider_class: Provider class
    """
    PROVIDER_MAP[name.lower()] = provider_class

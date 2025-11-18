"""Model registry and configuration."""
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ModelInfo:
    """Information about a model."""
    id: str
    provider: str
    name: str
    description: Optional[str] = None
    input_cost_per_1k: float = 0.0
    output_cost_per_1k: float = 0.0
    max_tokens: int = 4096
    supports_streaming: bool = True


# Model registry - Maps model identifiers to their info
MODEL_REGISTRY: Dict[str, ModelInfo] = {
    # Anthropic Claude
    "anthropic/claude-3-5-sonnet": ModelInfo(
        id="claude-3-5-sonnet-20241022",
        provider="anthropic",
        name="Claude 3.5 Sonnet",
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.015,
        max_tokens=8192,
    ),
    "anthropic/claude-3-5-sonnet-20241022": ModelInfo(
        id="claude-3-5-sonnet-20241022",
        provider="anthropic",
        name="Claude 3.5 Sonnet",
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.015,
        max_tokens=8192,
    ),
    "anthropic/claude-3-opus": ModelInfo(
        id="claude-3-opus-20240229",
        provider="anthropic",
        name="Claude 3 Opus",
        input_cost_per_1k=0.015,
        output_cost_per_1k=0.075,
        max_tokens=200000,
    ),
    "anthropic/claude-3-sonnet": ModelInfo(
        id="claude-3-sonnet-20240229",
        provider="anthropic",
        name="Claude 3 Sonnet",
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.015,
        max_tokens=200000,
    ),
    "anthropic/claude-3-haiku": ModelInfo(
        id="claude-3-haiku-20240307",
        provider="anthropic",
        name="Claude 3 Haiku",
        input_cost_per_1k=0.00025,
        output_cost_per_1k=0.00125,
        max_tokens=200000,
    ),
    
    # OpenAI
    "openai/gpt-4o": ModelInfo(
        id="gpt-4o",
        provider="openai",
        name="GPT-4o",
        input_cost_per_1k=0.005,
        output_cost_per_1k=0.015,
        max_tokens=128000,
    ),
    "openai/gpt-4-turbo": ModelInfo(
        id="gpt-4-turbo-preview",
        provider="openai",
        name="GPT-4 Turbo",
        input_cost_per_1k=0.01,
        output_cost_per_1k=0.03,
        max_tokens=128000,
    ),
    "openai/gpt-4": ModelInfo(
        id="gpt-4",
        provider="openai",
        name="GPT-4",
        input_cost_per_1k=0.03,
        output_cost_per_1k=0.06,
        max_tokens=8192,
    ),
    "openai/gpt-3.5-turbo": ModelInfo(
        id="gpt-3.5-turbo",
        provider="openai",
        name="GPT-3.5 Turbo",
        input_cost_per_1k=0.0005,
        output_cost_per_1k=0.0015,
        max_tokens=4096,
    ),
    
    # Groq
    "groq/llama-3-70b": ModelInfo(
        id="llama-3-70b-8192",
        provider="groq",
        name="Llama 3 70B",
        input_cost_per_1k=0.0,
        output_cost_per_1k=0.0,  # Groq is free tier
        max_tokens=8192,
    ),
    "groq/llama-2-70b": ModelInfo(
        id="llama2-70b-4096",
        provider="groq",
        name="Llama 2 70B",
        input_cost_per_1k=0.0,
        output_cost_per_1k=0.0,
        max_tokens=4096,
    ),
    "groq/mixtral-8x7b": ModelInfo(
        id="mixtral-8x7b-32768",
        provider="groq",
        name="Mixtral 8x7B",
        input_cost_per_1k=0.0,
        output_cost_per_1k=0.0,
        max_tokens=32768,
    ),
    
    # Google Gemini
    "google/gemini-1.5-pro": ModelInfo(
        id="gemini-1.5-pro",
        provider="google",
        name="Gemini 1.5 Pro",
        input_cost_per_1k=0.00075,
        output_cost_per_1k=0.003,
        max_tokens=2000000,
    ),
    "google/gemini-1.5-flash": ModelInfo(
        id="gemini-1.5-flash",
        provider="google",
        name="Gemini 1.5 Flash",
        input_cost_per_1k=0.000075,
        output_cost_per_1k=0.0003,
        max_tokens=1000000,
    ),
    
    # Cohere
    "cohere/command-r-plus": ModelInfo(
        id="command-r-plus",
        provider="cohere",
        name="Command R+",
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.015,
        max_tokens=4096,
    ),
    "cohere/command-r": ModelInfo(
        id="command-r",
        provider="cohere",
        name="Command R",
        input_cost_per_1k=0.0005,
        output_cost_per_1k=0.0015,
        max_tokens=4096,
    ),
}


def get_model_info(model_identifier: str) -> ModelInfo:
    """Get model info by identifier.
    
    Args:
        model_identifier: Model identifier (e.g., "anthropic/claude-3-5-sonnet")
        
    Returns:
        ModelInfo object
        
    Raises:
        ValueError: If model not found
    """
    if model_identifier not in MODEL_REGISTRY:
        raise ValueError(f"Model '{model_identifier}' not found in registry")
    return MODEL_REGISTRY[model_identifier]


def list_models_by_provider(provider: str) -> list[ModelInfo]:
    """List all models for a provider.
    
    Args:
        provider: Provider name (e.g., "anthropic", "openai")
        
    Returns:
        List of ModelInfo objects
    """
    return [info for info in MODEL_REGISTRY.values() if info.provider == provider]

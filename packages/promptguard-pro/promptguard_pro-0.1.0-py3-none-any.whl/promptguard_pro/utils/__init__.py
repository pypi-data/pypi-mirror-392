"""Utility functions for PromptGuard."""
from typing import Dict, List, Optional
import json
import re


def count_tokens_approximate(text: str, model: str = "") -> int:
    """Approximate token count using character ratio.
    
    Args:
        text: Text to count
        model: Model identifier (for future optimization)
        
    Returns:
        Approximate token count
    """
    # Rough estimate: 1 token per 4 characters
    # This is a fallback when provider-specific tokenizers aren't available
    return len(text) // 4


def extract_json_from_response(response: str) -> Optional[Dict]:
    """Extract JSON object from response text.
    
    Args:
        response: Response text
        
    Returns:
        Extracted JSON dict or None
    """
    # Try multiple extraction strategies
    strategies = [
        lambda r: json.loads(r),  # Raw JSON
        lambda r: json.loads(re.search(r'```(?:json)?\s*(.*?)\s*```', r, re.DOTALL).group(1)),
        lambda r: json.loads(re.search(r'\{.*\}', r, re.DOTALL).group(0)),
    ]
    
    for strategy in strategies:
        try:
            return strategy(response)
        except Exception:
            continue
    
    return None


def format_cost(cost: float) -> str:
    """Format cost as currency string.
    
    Args:
        cost: Cost in USD
        
    Returns:
        Formatted string
    """
    if cost < 0.001:
        return f"${cost:.6f}"
    elif cost < 0.01:
        return f"${cost:.4f}"
    else:
        return f"${cost:.2f}"


def format_duration(ms: float) -> str:
    """Format duration as human-readable string.
    
    Args:
        ms: Duration in milliseconds
        
    Returns:
        Formatted string
    """
    if ms < 1000:
        return f"{ms:.0f}ms"
    elif ms < 60000:
        return f"{ms / 1000:.1f}s"
    else:
        return f"{ms / 60000:.1f}m"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to append if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_model_id(model: str) -> str:
    """Sanitize model identifier for use as filename/key.
    
    Args:
        model: Model identifier
        
    Returns:
        Sanitized identifier
    """
    return re.sub(r'[^a-zA-Z0-9_-]', '_', model)


def merge_dicts(*dicts) -> Dict:
    """Merge multiple dictionaries, with later ones taking precedence.
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result

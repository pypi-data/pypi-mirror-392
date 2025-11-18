"""Cache backend for PromptGuard."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import hashlib
import json


class CacheBackend(ABC):
    """Base class for cache backends."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[dict]:
        """Retrieve cached result.
        
        Args:
            key: Cache key
            
        Returns:
            Cached dict or None if not found
        """
        pass
    
    @abstractmethod
    async def set(self, key: str, value: dict, ttl: int) -> None:
        """Store result in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove from cache.
        
        Args:
            key: Cache key
        """
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all cache entries."""
        pass
    
    @staticmethod
    def memory() -> "MemoryCacheBackend":
        """Create in-memory cache."""
        from promptguard.caching.memory import MemoryCacheBackend
        return MemoryCacheBackend()
    
    @staticmethod
    def redis(url: str = "redis://localhost:6379") -> "RedisCacheBackend":
        """Create Redis cache backend."""
        from promptguard.caching.redis import RedisCacheBackend
        return RedisCacheBackend(url)
    
    @staticmethod
    def disk(path: str = ".promptguard_cache") -> "DiskCacheBackend":
        """Create disk-based cache."""
        from promptguard.caching.disk import DiskCacheBackend
        return DiskCacheBackend(path)


def generate_cache_key(prompt: str, model: str, prefix: Optional[str] = None) -> str:
    """Generate cache key from prompt and model.
    
    Args:
        prompt: Prompt text
        model: Model identifier
        prefix: Optional key prefix
        
    Returns:
        Cache key
    """
    key_data = f"{model}:{prompt}"
    hash_obj = hashlib.sha256(key_data.encode())
    hash_str = hash_obj.hexdigest()
    
    if prefix:
        return f"{prefix}:{hash_str}"
    return hash_str

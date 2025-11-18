"""In-memory cache backend."""
import time
from typing import Optional, Dict, Any
from promptguard_pro.caching.base import CacheBackend


class MemoryCacheBackend(CacheBackend):
    """Simple in-memory cache implementation."""
    
    def __init__(self):
        """Initialize memory cache."""
        self._cache: Dict[str, tuple[Any, float]] = {}  # key -> (value, expiry_time)
    
    async def get(self, key: str) -> Optional[dict]:
        """Retrieve cached result."""
        if key not in self._cache:
            return None
        
        value, expiry = self._cache[key]
        
        if time.time() > expiry:
            del self._cache[key]
            return None
        
        return value
    
    async def set(self, key: str, value: dict, ttl: int) -> None:
        """Store result in cache."""
        expiry_time = time.time() + ttl
        self._cache[key] = (value, expiry_time)
    
    async def delete(self, key: str) -> None:
        """Remove from cache."""
        if key in self._cache:
            del self._cache[key]
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
    
    def __len__(self) -> int:
        """Get number of cached items."""
        return len(self._cache)

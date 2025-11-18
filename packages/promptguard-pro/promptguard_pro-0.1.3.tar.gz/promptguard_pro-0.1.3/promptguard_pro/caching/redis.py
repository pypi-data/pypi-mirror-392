"""Redis cache backend."""
from typing import Optional
import json
from promptguard_pro.caching.base import CacheBackend
from promptguard_pro.exceptions import CacheError


class RedisCacheBackend(CacheBackend):
    """Redis-based cache implementation."""
    
    def __init__(self, url: str = "redis://localhost:6379"):
        """Initialize Redis cache.
        
        Args:
            url: Redis URL
        """
        self.url = url
        
        try:
            import redis.asyncio
            self.redis = redis.asyncio.from_url(url)
        except ImportError:
            raise ImportError("redis package is required. Install with: pip install redis")
        except Exception as e:
            raise CacheError(f"Failed to connect to Redis at {url}: {str(e)}")
    
    async def get(self, key: str) -> Optional[dict]:
        """Retrieve cached result."""
        try:
            value = await self.redis.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            raise CacheError(f"Redis get failed: {str(e)}")
    
    async def set(self, key: str, value: dict, ttl: int) -> None:
        """Store result in cache."""
        try:
            await self.redis.setex(key, ttl, json.dumps(value))
        except Exception as e:
            raise CacheError(f"Redis set failed: {str(e)}")
    
    async def delete(self, key: str) -> None:
        """Remove from cache."""
        try:
            await self.redis.delete(key)
        except Exception as e:
            raise CacheError(f"Redis delete failed: {str(e)}")
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        try:
            await self.redis.flushdb()
        except Exception as e:
            raise CacheError(f"Redis clear failed: {str(e)}")
    
    async def close(self) -> None:
        """Close Redis connection."""
        await self.redis.close()

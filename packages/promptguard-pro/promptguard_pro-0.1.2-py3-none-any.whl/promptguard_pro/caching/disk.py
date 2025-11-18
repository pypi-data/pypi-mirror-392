"""Disk-based cache backend."""
import os
import json
import time
from typing import Optional
from pathlib import Path
from promptguard_pro.caching.base import CacheBackend
from promptguard_pro.exceptions import CacheError


class DiskCacheBackend(CacheBackend):
    """Disk-based cache implementation."""
    
    def __init__(self, path: str = ".promptguard_cache"):
        """Initialize disk cache.
        
        Args:
            path: Cache directory path
        """
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, key: str) -> Path:
        """Get file path for cache key."""
        return self.path / f"{key}.json"
    
    async def get(self, key: str) -> Optional[dict]:
        """Retrieve cached result."""
        try:
            file_path = self._get_file_path(key)
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Check if expired
            if time.time() > data.get('_expiry', 0):
                file_path.unlink()
                return None
            
            # Remove expiry marker before returning
            del data['_expiry']
            return data
        except Exception as e:
            raise CacheError(f"Disk cache get failed: {str(e)}")
    
    async def set(self, key: str, value: dict, ttl: int) -> None:
        """Store result in cache."""
        try:
            file_path = self._get_file_path(key)
            
            # Add expiry time
            data = value.copy()
            data['_expiry'] = time.time() + ttl
            
            with open(file_path, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            raise CacheError(f"Disk cache set failed: {str(e)}")
    
    async def delete(self, key: str) -> None:
        """Remove from cache."""
        try:
            file_path = self._get_file_path(key)
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            raise CacheError(f"Disk cache delete failed: {str(e)}")
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        try:
            for file_path in self.path.glob("*.json"):
                file_path.unlink()
        except Exception as e:
            raise CacheError(f"Disk cache clear failed: {str(e)}")

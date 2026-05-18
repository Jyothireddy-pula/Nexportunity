import time
from typing import Any, Callable, Optional
from functools import wraps


class CacheService:
    """Simple in-memory caching service with TTL support"""
    
    _cache = {}
    _timestamps = {}
    
    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        """Get value from cache if exists and not expired"""
        if key in cls._cache:
            # Check if expired
            if key in cls._timestamps:
                if time.time() - cls._timestamps[key] > 300:  # 5 minutes default TTL
                    cls.delete(key)
                    return None
            return cls._cache[key]
        return None
    
    @classmethod
    def set(cls, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache with TTL (seconds)"""
        cls._cache[key] = value
        cls._timestamps[key] = time.time()
    
    @classmethod
    def delete(cls, key: str) -> None:
        """Delete key from cache"""
        cls._cache.pop(key, None)
        cls._timestamps.pop(key, None)
    
    @classmethod
    def clear(cls) -> None:
        """Clear all cache"""
        cls._cache.clear()
        cls._timestamps.clear()
    
    @classmethod
    def cached(cls, ttl: int = 300, key_prefix: str = ""):
        """Decorator for caching function results"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{key_prefix}{func.__name__}_{str(args)}_{str(kwargs)}"
                
                # Try to get from cache
                cached_value = cls.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                cls.set(cache_key, result, ttl)
                return result
            return wrapper
        return decorator

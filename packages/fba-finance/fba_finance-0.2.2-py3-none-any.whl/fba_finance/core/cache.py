"""
Cache manager with multiple backend support
"""
import json
import hashlib
import time
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import os

try:
    import diskcache as dc
except ImportError:
    dc = None

try:
    import redis
except ImportError:
    redis = None


class CacheManager:
    """Manages caching with multiple backend options"""
    
    def __init__(self, backend: str = "memory", cache_dir: str = ".cache"):
        self.backend = backend
        self.cache_dir = cache_dir
        self._memory_cache = {}
        self._memory_cache_expiry = {}
        
        if backend == "disk":
            if dc is None:
                raise ImportError("diskcache not installed. Run: pip install diskcache")
            os.makedirs(cache_dir, exist_ok=True)
            self._disk_cache = dc.Cache(cache_dir)
        elif backend == "redis":
            if redis is None:
                raise ImportError("redis not installed. Run: pip install redis")
            self._redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DB", 0)),
                decode_responses=True
            )
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_parts = [prefix] + [str(arg) for arg in args]
        if kwargs:
            key_parts.append(json.dumps(kwargs, sort_keys=True))
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.backend == "memory":
                if key in self._memory_cache:
                    if key in self._memory_cache_expiry:
                        if time.time() > self._memory_cache_expiry[key]:
                            del self._memory_cache[key]
                            del self._memory_cache_expiry[key]
                            return None
                    return self._memory_cache[key]
                return None
            
            elif self.backend == "disk":
                return self._disk_cache.get(key)
            
            elif self.backend == "redis":
                value = self._redis_client.get(key)
                if value:
                    return json.loads(value)
                return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with optional TTL (seconds)"""
        try:
            if self.backend == "memory":
                self._memory_cache[key] = value
                if ttl:
                    self._memory_cache_expiry[key] = time.time() + ttl
            
            elif self.backend == "disk":
                if ttl:
                    self._disk_cache.set(key, value, expire=ttl)
                else:
                    self._disk_cache.set(key, value)
            
            elif self.backend == "redis":
                serialized = json.dumps(value, default=str)
                if ttl:
                    self._redis_client.setex(key, ttl, serialized)
                else:
                    self._redis_client.set(key, serialized)
        except Exception as e:
            print(f"Cache set error: {e}")
    
    def delete(self, key: str):
        """Delete key from cache"""
        try:
            if self.backend == "memory":
                self._memory_cache.pop(key, None)
                self._memory_cache_expiry.pop(key, None)
            elif self.backend == "disk":
                self._disk_cache.delete(key)
            elif self.backend == "redis":
                self._redis_client.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")
    
    def clear(self):
        """Clear all cache"""
        try:
            if self.backend == "memory":
                self._memory_cache.clear()
                self._memory_cache_expiry.clear()
            elif self.backend == "disk":
                self._disk_cache.clear()
            elif self.backend == "redis":
                self._redis_client.flushdb()
        except Exception as e:
            print(f"Cache clear error: {e}")
    
    def cache_quote(self, symbol: str, data: Any, ttl: int = 60):
        """Cache quote data"""
        key = self._make_key("quote", symbol)
        self.set(key, data, ttl)
    
    def get_cached_quote(self, symbol: str) -> Optional[Any]:
        """Get cached quote data"""
        key = self._make_key("quote", symbol)
        return self.get(key)
    
    def cache_historical(self, symbol: str, interval: str, start: str, end: str, 
                        data: Any, ttl: int = 3600):
        """Cache historical data"""
        key = self._make_key("historical", symbol, interval, start, end)
        self.set(key, data, ttl)
    
    def get_cached_historical(self, symbol: str, interval: str, 
                             start: str, end: str) -> Optional[Any]:
        """Get cached historical data"""
        key = self._make_key("historical", symbol, interval, start, end)
        return self.get(key)

    def is_stale(self, key: str, ttl_seconds: int) -> bool:
        """
        Check if cached entry is stale (older than TTL).
        
        Args:
            key: Cache key
            ttl_seconds: Time-to-live in seconds
            
        Returns:
            True if cache is stale or missing, False if still fresh
        """
        try:
            if self.backend == "memory":
                if key not in self._memory_cache:
                    return True  # Not in cache = stale
                if key in self._memory_cache_expiry:
                    return time.time() > self._memory_cache_expiry[key]
                return False  # No expiry = always fresh
            
            elif self.backend == "disk":
                value = self._disk_cache.get(key)
                return value is None
            
            elif self.backend == "redis":
                ttl_remaining = self._redis_client.ttl(key)
                if ttl_remaining == -2:  # Key doesn't exist
                    return True
                if ttl_remaining == -1:  # No expiry
                    return False
                return ttl_remaining <= 0
        except Exception as e:
            print(f"Cache is_stale error: {e}")
            return True  # On error, consider stale
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for monitoring.
        
        Returns:
            Dictionary with cache stats
        """
        try:
            if self.backend == "memory":
                return {
                    "backend": "memory",
                    "size": len(self._memory_cache),
                    "keys_with_ttl": len(self._memory_cache_expiry)
                }
            elif self.backend == "disk":
                return {
                    "backend": "disk",
                    "size": len(self._disk_cache),
                    "volume_path": self._disk_cache.directory
                }
            elif self.backend == "redis":
                info = self._redis_client.info("keyspace")
                db_key = f"db{os.getenv('REDIS_DB', 0)}"
                db_info = info.get(db_key, {})
                return {
                    "backend": "redis",
                    "keys": db_info.get("keys", 0) if isinstance(db_info, dict) else 0
                }
        except Exception as e:
            return {"error": str(e)}

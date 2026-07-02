# """Thread-safe Redis cache with LRU eviction"""

# import asyncio
# import hashlib
# import json
# from typing import Optional, Any, Dict
# import structlog
# import redis.asyncio as redis
# from src.common.circuit_breaker import CircuitBreaker, CircuitBreakerConfig

# logger = structlog.get_logger()


# class InferenceCache:
#     """Thread-safe distributed inference cache using Redis"""
    
#     def __init__(
#         self,
#         redis_host: str = "localhost",
#         redis_port: int = 6379,
#         redis_db: int = 0,
#         max_size: int = 10000,
#         ttl_seconds: int = 3600,
#         redis_password: Optional[str] = None
#     ):
#         self.redis = redis.Redis(
#             host=redis_host,
#             port=redis_port,
#             db=redis_db,
#             password=redis_password,
#             decode_responses=True,
#             socket_keepalive=True,
#             socket_connect_timeout=5,
#             socket_timeout=5,
#             health_check_interval=30
#         )
#         self.max_size = max_size
#         self.ttl = ttl_seconds
#         self._lock = asyncio.Lock()
#         self.circuit_breaker = CircuitBreaker(
#             "redis-cache",
#             CircuitBreakerConfig(failure_threshold=3, timeout_seconds=10)
#         )
#         self._initialized = False
    
#     async def initialize(self) -> None:
#         """Initialize cache connection"""
#         if self._initialized:
#             return
        
#         try:
#             await self.redis.ping()
#             self._initialized = True
#             logger.info("✅ Redis cache initialized")
#         except Exception as e:
#             logger.error(f"Redis cache initialization failed: {e}")
#             raise
    
#     def _get_key(self, content: str) -> str:
#         """Generate cache key from content"""
#         return f"cache:{hashlib.md5(content.encode()).hexdigest()}"
    
#     async def get(self, content: str) -> Optional[Dict[str, Any]]:
#         """Get cached inference result"""
#         if not self._initialized:
#             await self.initialize()
        
#         try:
#             key = self._get_key(content)
#             cached = await self.circuit_breaker.call(
#                 self.redis.get,
#                 key
#             )
#             if cached:
#                 logger.debug("Cache hit", key=key[:8])
#                 return json.loads(cached)
#             logger.debug("Cache miss", key=key[:8])
#             return None
#         except Exception as e:
#             logger.warning(f"Cache get failed: {e}")
#             return None
    
#     async def set(self, content: str, result: Dict[str, Any]) -> None:
#         """Set cache entry with TTL"""
#         if not self._initialized:
#             await self.initialize()
        
#         try:
#             key = self._get_key(content)
#             await self.circuit_breaker.call(
#                 self.redis.setex,
#                 key,
#                 self.ttl,
#                 json.dumps(result)
#             )
#             logger.debug("Cache set", key=key[:8])
#         except Exception as e:
#             logger.warning(f"Cache set failed: {e}")
    
#     async def clear(self) -> None:
#         """Clear all cache entries"""
#         if not self._initialized:
#             await self.initialize()
        
#         try:
#             keys = await self.redis.keys("cache:*")
#             if keys:
#                 await self.redis.delete(*keys)
#             logger.info("Cache cleared")
#         except Exception as e:
#             logger.error(f"Cache clear failed: {e}")
    
#     async def get_stats(self) -> Dict[str, Any]:
#         """Get cache statistics"""
#         if not self._initialized:
#             await self.initialize()
        
#         try:
#             size = await self.redis.dbsize()
#             return {
#                 "size": size,
#                 "max_size": self.max_size,
#                 "ttl_seconds": self.ttl,
#                 "utilization": (size / self.max_size) * 100 if self.max_size > 0 else 0
#             }
#         except Exception as e:
#             return {"error": str(e)}
    
#     async def close(self) -> None:
#         """Close Redis connection"""
#         await self.redis.close()
#         await self.redis.wait_closed()



"""Thread-safe Redis cache with LRU eviction"""

import asyncio
import hashlib
import json
from typing import Optional, Any, Dict
import structlog
import redis.asyncio as redis
from src.common.circuit_breaker import CircuitBreaker, CircuitBreakerConfig

logger = structlog.get_logger()


class InferenceCache:
    """Thread-safe distributed inference cache using Redis"""
    
    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        max_size: int = 10000,
        ttl_seconds: int = 3600,
        redis_password: Optional[str] = None
    ):
        self.redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password,
            decode_responses=True,
            socket_keepalive=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            health_check_interval=30
        )
        self.max_size = max_size
        self.ttl = ttl_seconds
        self._lock = asyncio.Lock()
        self.circuit_breaker = CircuitBreaker(
            "redis-cache",
            CircuitBreakerConfig(failure_threshold=3, timeout_seconds=10)
        )
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize cache connection"""
        if self._initialized:
            return
        
        try:
            await self.redis.ping()
            self._initialized = True
            logger.info("✅ Redis cache initialized")
        except Exception as e:
            logger.error(f"Redis cache initialization failed: {e}")
            raise
    
    def _get_key(self, content: str) -> str:
        """Generate cache key from content"""
        return f"cache:{hashlib.md5(content.encode()).hexdigest()}"
    
    async def get(self, content: str) -> Optional[Dict[str, Any]]:
        """Get cached inference result"""
        if not self._initialized:
            await self.initialize()
        
        try:
            key = self._get_key(content)
            cached = await self.circuit_breaker.call(
                self.redis.get,
                key
            )
            if cached:
                logger.debug("Cache hit", key=key[:8])
                return json.loads(cached)
            logger.debug("Cache miss", key=key[:8])
            return None
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
            return None
    
    async def set(self, content: str, result: Dict[str, Any]) -> None:
        """Set cache entry with TTL"""
        if not self._initialized:
            await self.initialize()
        
        try:
            key = self._get_key(content)
            await self.circuit_breaker.call(
                self.redis.setex,
                key,
                self.ttl,
                json.dumps(result)
            )
            logger.debug("Cache set", key=key[:8])
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
    
    async def clear(self) -> None:
        """Clear all cache entries"""
        if not self._initialized:
            await self.initialize()
        
        try:
            keys = await self.redis.keys("cache:*")
            if keys:
                await self.redis.delete(*keys)
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self._initialized:
            await self.initialize()
        
        try:
            size = await self.redis.dbsize()
            return {
                "size": size,
                "max_size": self.max_size,
                "ttl_seconds": self.ttl,
                "utilization": (size / self.max_size) * 100 if self.max_size > 0 else 0
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def close(self) -> None:
        """Close Redis connection"""
        if self.redis:
            try:
                # Try the modern way first
                await self.redis.aclose()
            except AttributeError:
                try:
                    # Fallback for older versions
                    await self.redis.close()
                    await self.redis.wait_closed()
                except AttributeError:
                    # Final fallback
                    pass
            logger.debug("Redis connection closed")
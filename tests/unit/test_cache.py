# """Unit tests for Redis cache"""

# import pytest
# import asyncio
# import json
# from src.serving.cache import InferenceCache


# @pytest.fixture
# async def cache():
#     """Create cache instance for testing"""
#     cache = InferenceCache(redis_host='localhost', redis_port=6379)
#     await cache.initialize()
#     yield cache
#     await cache.close()


# @pytest.mark.asyncio
# async def test_initialize():
#     """Test cache initialization"""
#     cache = InferenceCache(redis_host='localhost', redis_port=6379)
#     assert cache._initialized is False
    
#     await cache.initialize()
#     assert cache._initialized is True
    
#     await cache.close()


# @pytest.mark.asyncio
# async def test_set_and_get(cache):
#     """Test set and get operations"""
#     test_data = {"prediction": 42, "confidence": 0.95}
    
#     await cache.set("test_key", test_data)
#     result = await cache.get("test_key")
    
#     assert result == test_data


# @pytest.mark.asyncio
# async def test_cache_miss(cache):
#     """Test cache miss returns None"""
#     result = await cache.get("nonexistent_key")
#     assert result is None


# @pytest.mark.asyncio
# async def test_cache_clear(cache):
#     """Test clearing cache"""
#     test_data = {"prediction": 42}
    
#     await cache.set("test_key", test_data)
#     result = await cache.get("test_key")
#     assert result == test_data
    
#     await cache.clear()
#     result = await cache.get("test_key")
#     assert result is None


# @pytest.mark.asyncio
# async def test_cache_stats(cache):
#     """Test cache statistics"""
#     stats = await cache.get_stats()
    
#     assert "size" in stats
#     assert "max_size" in stats
#     assert "ttl_seconds" in stats
#     assert "utilization" in stats


# @pytest.mark.asyncio
# async def test_cache_ttl(cache):
#     """Test TTL works"""
#     test_data = {"prediction": 42}
    
#     await cache.set("ttl_key", test_data)
    
#     # Should exist initially
#     result = await cache.get("ttl_key")
#     assert result == test_data




"""Unit tests for Redis cache"""

import pytest
import pytest_asyncio
import asyncio
import json
from src.serving.cache import InferenceCache


@pytest_asyncio.fixture
async def cache():
    """Create cache instance for testing"""
    cache = InferenceCache(redis_host='localhost', redis_port=6379)
    await cache.initialize()
    yield cache
    await cache.close()


@pytest.mark.asyncio
async def test_initialize():
    """Test cache initialization"""
    cache = InferenceCache(redis_host='localhost', redis_port=6379)
    assert cache._initialized is False
    
    await cache.initialize()
    assert cache._initialized is True
    
    await cache.close()


@pytest.mark.asyncio
async def test_set_and_get(cache):
    """Test set and get operations"""
    test_data = {"prediction": 42, "confidence": 0.95}
    
    await cache.set("test_key", test_data)
    result = await cache.get("test_key")
    
    assert result == test_data


@pytest.mark.asyncio
async def test_cache_miss(cache):
    """Test cache miss returns None"""
    result = await cache.get("nonexistent_key")
    assert result is None


@pytest.mark.asyncio
async def test_cache_clear(cache):
    """Test clearing cache"""
    test_data = {"prediction": 42}
    
    await cache.set("test_key", test_data)
    result = await cache.get("test_key")
    assert result == test_data
    
    await cache.clear()
    result = await cache.get("test_key")
    assert result is None


@pytest.mark.asyncio
async def test_cache_stats(cache):
    """Test cache statistics"""
    stats = await cache.get_stats()
    
    assert "size" in stats
    assert "max_size" in stats
    assert "ttl_seconds" in stats
    assert "utilization" in stats


@pytest.mark.asyncio
async def test_cache_ttl(cache):
    """Test TTL works"""
    test_data = {"prediction": 42}
    
    await cache.set("ttl_key", test_data)
    
    # Should exist initially
    result = await cache.get("ttl_key")
    assert result == test_data
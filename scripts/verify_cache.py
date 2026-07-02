#!/usr/bin/env python
"""Complete cache verification"""

import asyncio
import sys
import json
from src.serving.cache import InferenceCache

async def test_cache():
    print("=" * 60)
    print("🔍 VERIFYING REDIS CACHE")
    print("=" * 60)
    
    cache = InferenceCache(redis_host='localhost', redis_port=6379)
    
    try:
        # 1. Initialize
        print("\n📋 Testing initialization...")
        await cache.initialize()
        print("✅ Cache initialized")
        
        # 2. Set
        print("\n📋 Testing set operation...")
        test_data = {"prediction": 42, "confidence": 0.95, "label": "test"}
        await cache.set("test_key", test_data)
        print("✅ Set successful")
        
        # 3. Get
        print("\n📋 Testing get operation...")
        result = await cache.get("test_key")
        assert result == test_data
        print(f"✅ Get successful: {result}")
        
        # 4. Cache miss
        print("\n📋 Testing cache miss...")
        missing = await cache.get("nonexistent_key")
        assert missing is None
        print("✅ Cache miss returns None")
        
        # 5. Stats
        print("\n📋 Testing stats...")
        stats = await cache.get_stats()
        assert stats["size"] > 0
        print(f"✅ Stats: {stats}")
        
        # 6. Clear
        print("\n📋 Testing clear...")
        await cache.clear()
        cleared = await cache.get("test_key")
        assert cleared is None
        print("✅ Cache cleared")
        
        # 7. Close - FIXED
        print("\n📋 Testing close...")
        await cache.close()
        print("✅ Connection closed")
        
        print("\n" + "=" * 60)
        print("✅ ALL CACHE TESTS PASSED!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_cache())
    sys.exit(0 if success else 1)
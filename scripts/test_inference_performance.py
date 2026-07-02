# #!/usr/bin/env python
# """Performance test for model inference"""

# import asyncio
# import time
# from src.serving.inference import ModelInference, InferenceRequest
# from src.serving.config import ServingConfig

# async def test_performance():
#     config = ServingConfig()
#     inference = ModelInference(config)
    
#     # Note: This requires a real model to be loaded
#     # For demonstration, we'll just test the batching logic
    
#     # Create test requests
#     requests = [
#         InferenceRequest(content=f"Test document {i}")
#         for i in range(10)
#     ]
    
#     print(f"📊 Created {len(requests)} test requests")
    
#     # Test batch processing logic (without actual model)
#     start = time.time()
    
#     # Simulate batch processing
#     batch_size = config.batch_size or 32
#     for i in range(0, len(requests), batch_size):
#         batch = requests[i:i + batch_size]
#         print(f"   Processing batch {i//batch_size + 1}: {len(batch)} requests")
#         await asyncio.sleep(0.01)  # Simulate processing
    
#     elapsed = time.time() - start
#     print(f"✅ Batch processing completed in {elapsed:.3f}s")
#     print(f"   Throughput: {len(requests)/elapsed:.1f} requests/s")

# asyncio.run(test_performance())


# #!/usr/bin/env python
# """Performance test for inference module"""

# import sys
# import os
# import time
# import asyncio
# import random

# # Add project root to path
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from src.serving.inference import ModelInference, InferenceRequest
# from src.serving.config import ServingConfig


# async def test_performance():
#     """Test inference performance"""
#     print("=" * 60)
#     print("🚀 INFERENCE PERFORMANCE TEST")
#     print("=" * 60)
    
#     # Load config and model
#     config = ServingConfig()
#     inference = ModelInference(config)
#     await inference.load()
    
#     print(f"\n📋 Model loaded (mock mode: {inference._mock_mode})")
#     print(f"   Device: {inference.device}")
#     print(f"   Labels: {inference.labels}")
    
#     # Test documents
#     documents = [
#         "This is a business document about quarterly earnings",
#         "Legal contract between two parties for software licensing",
#         "Technical specification for API integration",
#         "Academic research paper on machine learning",
#         "General document about company policies",
#         "Invoice for professional services rendered",
#         "Employment agreement with confidentiality clause",
#         "Product requirements document for new feature",
#         "Quality assurance test report for release 2.0",
#         "Marketing presentation for product launch"
#     ]
    
#     print("\n📊 Running performance tests...")
    
#     # Single prediction test
#     print("\n📋 Single prediction test:")
#     start = time.time()
#     for i, doc in enumerate(documents[:5]):
#         result = await inference.predict(doc)
#         print(f"  {i+1}. {result.label} ({result.confidence:.3f}) - {result.latency_ms:.2f}ms")
#     single_time = (time.time() - start) * 1000 / 5
#     print(f"\n  Average latency: {single_time:.2f}ms")
    
#     # Batch prediction test
#     print("\n📋 Batch prediction test:")
#     requests = [InferenceRequest(content=doc) for doc in documents]
#     start = time.time()
#     results = await inference.predict_batch(requests)
#     batch_time = (time.time() - start) * 1000
    
#     # Show stats
#     latencies = [r.latency_ms for r in results]
#     avg_latency = sum(latencies) / len(latencies)
#     max_latency = max(latencies)
#     min_latency = min(latencies)
    
#     print(f"  Total documents: {len(results)}")
#     print(f"  Total time: {batch_time:.2f}ms")
#     print(f"  Average latency: {avg_latency:.2f}ms")
#     print(f"  Min latency: {min_latency:.2f}ms")
#     print(f"  Max latency: {max_latency:.2f}ms")
#     print(f"  Throughput: {len(results) / (batch_time / 1000):.2f} req/s")
    
#     # Cache test
#     print("\n📋 Cache performance test:")
#     # First request (cache miss)
#     start = time.time()
#     result1 = await inference.predict("This is a test for cache")
#     miss_time = (time.time() - start) * 1000
    
#     # Second request (cache hit)
#     start = time.time()
#     result2 = await inference.predict("This is a test for cache")
#     hit_time = (time.time() - start) * 1000
    
#     print(f"  Cache miss: {miss_time:.2f}ms")
#     print(f"  Cache hit: {hit_time:.2f}ms")
#     print(f"  Speedup: {miss_time / hit_time:.2f}x")
    
#     # Cleanup
#     await inference.clear_cache()
#     await inference.cache.close()
    
#     print("\n" + "=" * 60)
#     print("✅ Performance test complete!")
#     print("=" * 60)

# if __name__ == "__main__":
#     asyncio.run(test_performance())






















#!/usr/bin/env python
"""Comprehensive performance test for inference module"""

import sys
import os
import time
import asyncio
import random
import statistics

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.serving.inference import ModelInference, InferenceRequest
from src.serving.config import ServingConfig


async def test_performance():
    """Test inference performance"""
    print("=" * 70)
    print("🚀 INFERENCE PERFORMANCE TEST - v2.0")
    print("=" * 70)
    
    # Load config and model
    config = ServingConfig()
    inference = ModelInference(config)
    await inference.load()
    
    print(f"\n📋 System Info:")
    print(f"   Mock mode: {inference._mock_mode}")
    print(f"   Device: {inference.device}")
    print(f"   Labels: {len(inference.labels)} classes")
    
    # More diverse test documents
    documents = [
        "This is a business document about quarterly earnings",
        "Legal contract between two parties for software licensing",
        "Technical specification for API integration",
        "Academic research paper on machine learning",
        "General document about company policies",
        "Invoice for professional services rendered",
        "Employment agreement with confidentiality clause",
        "Product requirements document for new feature",
        "Quality assurance test report for release 2.0",
        "Marketing presentation for product launch",
        "Financial audit report for fiscal year",
        "Data privacy policy and GDPR compliance",
        "Software architecture design for microservices",
        "Customer support ticket analysis report",
        "Supply chain logistics and inventory management"
    ] * 2  # 30 documents
    
    print(f"\n📊 Test Documents: {len(documents)}")
    
    # ============================================================
    # 1. SINGLE PREDICTION TEST
    # ============================================================
    print("\n" + "=" * 70)
    print("📋 1. SINGLE PREDICTION TEST")
    print("=" * 70)
    
    single_latencies = []
    print("\n  Individual predictions:")
    for i in range(10):
        doc = random.choice(documents)
        start = time.perf_counter()
        result = await inference.predict(doc)
        latency = (time.perf_counter() - start) * 1000
        single_latencies.append(latency)
        print(f"  {i+1:2d}. {result.label:12s} ({result.confidence:.3f}) - {latency:6.2f}ms")
    
    print(f"\n  📊 Statistics:")
    print(f"     Min:  {min(single_latencies):.2f}ms")
    print(f"     Max:  {max(single_latencies):.2f}ms")
    print(f"     Avg:  {statistics.mean(single_latencies):.2f}ms")
    print(f"     P95:  {statistics.quantiles(single_latencies, n=20)[-1]:.2f}ms")
    print(f"     Std:  {statistics.stdev(single_latencies):.2f}ms")
    
    # ============================================================
    # 2. BATCH PREDICTION TEST
    # ============================================================
    print("\n" + "=" * 70)
    print("📋 2. BATCH PREDICTION TEST")
    print("=" * 70)
    
    # Test different batch sizes
    batch_sizes = [1, 5, 10, 20, 30]
    
    for batch_size in batch_sizes:
        batch_docs = documents[:batch_size]
        requests = [InferenceRequest(content=doc) for doc in batch_docs]
        
        start = time.perf_counter()
        results = await inference.predict_batch(requests)
        batch_time = (time.perf_counter() - start) * 1000
        
        batch_latencies = [r.latency_ms for r in results]
        
        print(f"\n  Batch Size: {batch_size}")
        print(f"     Total Time:  {batch_time:.2f}ms")
        print(f"     Avg Latency: {statistics.mean(batch_latencies):.2f}ms")
        print(f"     Throughput:  {batch_size / (batch_time / 1000):.2f} req/s")
    
    # ============================================================
    # 3. CACHE PERFORMANCE TEST
    # ============================================================
    print("\n" + "=" * 70)
    print("📋 3. CACHE PERFORMANCE TEST")
    print("=" * 70)
    
    test_content = "This is a test document for cache performance testing"
    
    # Measure cache miss
    miss_latencies = []
    for i in range(5):
        # Use slightly different content to avoid cache hits
        content = f"{test_content} - {i}" if i > 0 else test_content
        start = time.perf_counter()
        await inference.predict(content)
        latency = (time.perf_counter() - start) * 1000
        miss_latencies.append(latency)
    
    # Measure cache hits
    hit_latencies = []
    for i in range(5):
        start = time.perf_counter()
        await inference.predict(test_content)
        latency = (time.perf_counter() - start) * 1000
        hit_latencies.append(latency)
    
    print(f"\n  Cache Miss (first request):")
    print(f"     Min:  {min(miss_latencies):.2f}ms")
    print(f"     Avg:  {statistics.mean(miss_latencies):.2f}ms")
    print(f"     Max:  {max(miss_latencies):.2f}ms")
    
    print(f"\n  Cache Hit (cached requests):")
    print(f"     Min:  {min(hit_latencies):.2f}ms")
    print(f"     Avg:  {statistics.mean(hit_latencies):.2f}ms")
    print(f"     Max:  {max(hit_latencies):.2f}ms")
    
    speedup = statistics.mean(miss_latencies) / statistics.mean(hit_latencies)
    print(f"\n  ⚡ Speedup: {speedup:.2f}x")
    
    # ============================================================
    # 4. CONCURRENT REQUESTS TEST
    # ============================================================
    print("\n" + "=" * 70)
    print("📋 4. CONCURRENT REQUESTS TEST")
    print("=" * 70)
    
    concurrency_levels = [1, 5, 10, 25, 50]
    
    for concurrency in concurrency_levels:
        print(f"\n  Concurrency: {concurrency}")
        
        async def worker(idx):
            doc = random.choice(documents)
            return await inference.predict(doc)
        
        start = time.perf_counter()
        tasks = [worker(i) for i in range(concurrency)]
        results = await asyncio.gather(*tasks)
        total_time = (time.perf_counter() - start) * 1000
        
        avg_latency = sum(r.latency_ms for r in results) / len(results)
        
        print(f"     Total Time:  {total_time:.2f}ms")
        print(f"     Avg Latency: {avg_latency:.2f}ms")
        print(f"     Throughput:  {concurrency / (total_time / 1000):.2f} req/s")
    
    # ============================================================
    # 5. SUMMARY
    # ============================================================
    print("\n" + "=" * 70)
    print("📊 5. PERFORMANCE SUMMARY")
    print("=" * 70)
    
    print(f"\n  Single Prediction (avg): {statistics.mean(single_latencies):.2f}ms")
    print(f"  Batch Prediction (30 docs): Throughput: {30 / ((batch_time) / 1000):.2f} req/s")
    print(f"  Cache Speedup: {speedup:.2f}x")
    print(f"  Concurrent (50 req): {50 / ((total_time) / 1000):.2f} req/s")
    
    # ============================================================
    # 6. CLEANUP
    # ============================================================
    await inference.clear_cache()
    await inference.cache.close()
    
    print("\n" + "=" * 70)
    print("✅ PERFORMANCE TEST COMPLETE!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_performance())
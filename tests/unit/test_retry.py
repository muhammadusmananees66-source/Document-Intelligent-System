"""Unit tests for retry module"""

import pytest
import asyncio
import time
from src.common.retry import retry, RetryConfig


class TestRetryConfig:
    """Test RetryConfig"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.backoff_multiplier == 2.0
        assert config.jitter is True
        assert config.retry_on == (Exception,)
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = RetryConfig(
            max_retries=5,
            base_delay=0.5,
            max_delay=10.0,
            backoff_multiplier=1.5,
            jitter=False,
            retry_on=(ValueError, TypeError)
        )
        assert config.max_retries == 5
        assert config.base_delay == 0.5
        assert config.max_delay == 10.0
        assert config.backoff_multiplier == 1.5
        assert config.jitter is False
        assert config.retry_on == (ValueError, TypeError)


class TestRetry:
    """Test retry decorator"""
    
    def test_retry_sync_success_first_attempt(self):
        """Test sync function succeeds on first attempt"""
        counter = 0
        
        @retry(RetryConfig(max_retries=3))
        def test_func():
            nonlocal counter
            counter += 1
            return "success"
        
        result = test_func()
        assert result == "success"
        assert counter == 1
    
    def test_retry_sync_success_after_retries(self):
        """Test sync function succeeds after retries"""
        counter = 0
        
        @retry(RetryConfig(max_retries=3))
        def test_func():
            nonlocal counter
            counter += 1
            if counter < 2:
                raise ValueError("Temporary failure")
            return "success"
        
        result = test_func()
        assert result == "success"
        assert counter == 2
    
    def test_retry_sync_exhausted(self):
        """Test sync function exhausts retries"""
        counter = 0
        
        @retry(RetryConfig(max_retries=2))
        def test_func():
            nonlocal counter
            counter += 1
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            test_func()
        assert counter == 3  # max_retries + 1
    
    def test_retry_sync_only_on_specific_exception(self):
        """Test sync retry only on specific exception"""
        counter = 0
        
        @retry(RetryConfig(max_retries=2, retry_on=(ValueError,)))
        def test_func():
            nonlocal counter
            counter += 1
            raise TypeError("Not retryable")
        
        with pytest.raises(TypeError):
            test_func()
        assert counter == 1  # Should not retry
    
    def test_retry_sync_jitter_disabled(self):
        """Test sync retry with jitter disabled"""
        counter = 0
        
        @retry(RetryConfig(
            max_retries=2,
            base_delay=0.1,
            backoff_multiplier=2.0,
            jitter=False
        ))
        def test_func():
            nonlocal counter
            counter += 1
            raise ValueError("Fail")
        
        start = time.time()
        with pytest.raises(ValueError):
            test_func()
        elapsed = time.time() - start
        
        # With jitter disabled, delays should be deterministic
        # 0.1 + 0.2 = 0.3 seconds
        assert elapsed >= 0.25
        assert elapsed < 0.5
        assert counter == 3
    
    def test_retry_sync_max_delay(self):
        """Test sync retry respects max_delay"""
        counter = 0
        
        @retry(RetryConfig(
            max_retries=2,
            base_delay=10.0,  # Large base delay
            max_delay=1.0,    # Capped at 1 second
            backoff_multiplier=2.0,
            jitter=False
        ))
        def test_func():
            nonlocal counter
            counter += 1
            raise ValueError("Fail")
        
        start = time.time()
        with pytest.raises(ValueError):
            test_func()
        elapsed = time.time() - start
        
        # Delays should be capped at max_delay (1.0)
        # 1.0 + 1.0 = 2.0 seconds
        assert elapsed >= 1.8
        assert elapsed < 2.5
        assert counter == 3
    
    @pytest.mark.asyncio
    async def test_retry_async_success_first_attempt(self):
        """Test async function succeeds on first attempt"""
        counter = 0
        
        @retry(RetryConfig(max_retries=3))
        async def test_func():
            nonlocal counter
            counter += 1
            return "success"
        
        result = await test_func()
        assert result == "success"
        assert counter == 1
    
    @pytest.mark.asyncio
    async def test_retry_async_success_after_retries(self):
        """Test async function succeeds after retries"""
        counter = 0
        
        @retry(RetryConfig(max_retries=3))
        async def test_func():
            nonlocal counter
            counter += 1
            if counter < 2:
                raise ValueError("Temporary failure")
            return "success"
        
        result = await test_func()
        assert result == "success"
        assert counter == 2
    
    @pytest.mark.asyncio
    async def test_retry_async_exhausted(self):
        """Test async function exhausts retries"""
        counter = 0
        
        @retry(RetryConfig(max_retries=2))
        async def test_func():
            nonlocal counter
            counter += 1
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            await test_func()
        assert counter == 3
    
    @pytest.mark.asyncio
    async def test_retry_async_only_on_specific_exception(self):
        """Test async retry only on specific exception"""
        counter = 0
        
        @retry(RetryConfig(max_retries=2, retry_on=(ValueError,)))
        async def test_func():
            nonlocal counter
            counter += 1
            raise TypeError("Not retryable")
        
        with pytest.raises(TypeError):
            await test_func()
        assert counter == 1
    
    @pytest.mark.asyncio
    async def test_retry_async_with_delay(self):
        """Test async retry with actual delays"""
        counter = 0
        
        @retry(RetryConfig(
            max_retries=2,
            base_delay=0.1,
            backoff_multiplier=2.0,
            jitter=False
        ))
        async def test_func():
            nonlocal counter
            counter += 1
            raise ValueError("Fail")
        
        start = time.time()
        with pytest.raises(ValueError):
            await test_func()
        elapsed = time.time() - start
        
        assert elapsed >= 0.25
        assert counter == 3


class TestRetryIntegration:
    """Integration-style tests"""
    
    def test_retry_with_circuit_breaker_pattern(self):
        """Test retry works with circuit breaker pattern"""
        counter = 0
        
        @retry(RetryConfig(max_retries=3, retry_on=(ValueError,)))
        def flaky_service():
            nonlocal counter
            counter += 1
            if counter < 2:
                raise ValueError("Service temporarily unavailable")
            return "Service healthy"
        
        result = flaky_service()
        assert result == "Service healthy"
        assert counter == 2
    
    def test_retry_with_different_exception_types(self):
        """Test retry handles different exception types"""
        counter = 0
        
        @retry(RetryConfig(
            max_retries=3,
            retry_on=(ValueError, ConnectionError, TimeoutError)
        ))
        def test_func():
            nonlocal counter
            counter += 1
            if counter == 1:
                raise ConnectionError("Network error")
            if counter == 2:
                raise TimeoutError("Timeout")
            return "Success"
        
        result = test_func()
        assert result == "Success"
        assert counter == 3
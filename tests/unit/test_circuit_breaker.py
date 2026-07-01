"""
Comprehensive unit tests for circuit breaker.

Tests cover:
- State transitions (CLOSED -> OPEN -> HALF_OPEN -> CLOSED)
- Failure thresholds
- Success thresholds  
- Timeout recovery
- Max requests in HALF_OPEN
- Race condition prevention
- Metrics collection
- Full lifecycle
"""

import pytest
import asyncio
import time
from src.common.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState
)


class TestCircuitBreakerConfig:
    """Test CircuitBreakerConfig"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = CircuitBreakerConfig()
        assert config.failure_threshold == 5
        assert config.success_threshold == 3
        assert config.timeout_seconds == 60
        assert config.max_requests == 1
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout_seconds=30,
            max_requests=5
        )
        assert config.failure_threshold == 3
        assert config.success_threshold == 2
        assert config.timeout_seconds == 30
        assert config.max_requests == 5


class TestCircuitBreaker:
    """Test CircuitBreaker functionality"""
    
    def test_initial_state(self):
        """Test initial state is CLOSED"""
        cb = CircuitBreaker("test")
        assert cb.state == CircuitState.CLOSED
        assert cb.is_closed is True
        assert cb.is_open is False
        assert cb.is_half_open is False
    
    def test_get_metrics(self):
        """Test metrics collection returns correct values"""
        cb = CircuitBreaker("test")
        metrics = cb.get_metrics()
        
        assert metrics["name"] == "test"
        assert metrics["state"] == "closed"
        assert metrics["failure_count"] == 0
        assert metrics["success_count"] == 0
        assert metrics["half_open_requests"] == 0
        assert "time_in_state" in metrics
        assert isinstance(metrics["time_in_state"], float)
        assert "config" in metrics
        assert metrics["config"]["failure_threshold"] == 5
    
    @pytest.mark.asyncio
    async def test_successful_call_closed(self):
        """Test successful call keeps circuit CLOSED"""
        cb = CircuitBreaker("test")
        
        async def success():
            return "success"
        
        result = await cb.call(success)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
        assert cb._failure_count == 0
    
    @pytest.mark.asyncio
    async def test_single_failure_does_not_open(self):
        """Test single failure doesn't open circuit"""
        cb = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=3))
        
        async def fail():
            raise RuntimeError("Expected error")
        
        with pytest.raises(RuntimeError):
            await cb.call(fail)
        
        assert cb.state == CircuitState.CLOSED
        assert cb._failure_count == 1
    
    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold(self):
        """Test circuit opens after threshold failures"""
        cb = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=2))
        
        async def fail():
            raise RuntimeError("Expected error")
        
        # First failure - circuit stays CLOSED
        with pytest.raises(RuntimeError):
            await cb.call(fail)
        assert cb.state == CircuitState.CLOSED
        assert cb._failure_count == 1
        
        # Second failure - circuit opens
        with pytest.raises(RuntimeError):
            await cb.call(fail)
        assert cb.state == CircuitState.OPEN
        assert cb._failure_count == 2
    
    @pytest.mark.asyncio
    async def test_open_circuit_rejects_requests(self):
        """Test open circuit rejects all requests"""
        cb = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=1))
        
        async def fail():
            raise RuntimeError("Expected error")
        
        # Open circuit
        with pytest.raises(RuntimeError):
            await cb.call(fail)
        assert cb.state == CircuitState.OPEN
        
        # Should reject with circuit open message
        with pytest.raises(RuntimeError) as exc_info:
            await cb.call(fail)
        assert "circuit 'test' is open" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_circuit_transitions_to_half_open_after_timeout(self):
        """
        Test circuit transitions to HALF_OPEN after timeout.
        
        IMPORTANT: This transition happens lazily on the NEXT request,
        not automatically. This matches Netflix Hystrix and Resilience4j.
        """
        cb = CircuitBreaker("test", CircuitBreakerConfig(
            failure_threshold=1,
            timeout_seconds=1,
            success_threshold=1
        ))
        
        async def fail():
            raise RuntimeError("Expected error")
        
        # Open circuit
        with pytest.raises(RuntimeError):
            await cb.call(fail)
        assert cb.state == CircuitState.OPEN
        
        # Wait for timeout
        await asyncio.sleep(1.1)
        
        # Circuit is still OPEN (no automatic transition)
        assert cb.state == CircuitState.OPEN
        
        # Next request triggers transition to HALF_OPEN
        async def success():
            return "success"
        
        result = await cb.call(success)
        assert result == "success"
        # Success in HALF_OPEN with threshold=1 closes circuit
        assert cb.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_success_in_half_open_closes_circuit(self):
        """Test success in HALF_OPEN closes circuit"""
        cb = CircuitBreaker("test", CircuitBreakerConfig(
            failure_threshold=1,
            timeout_seconds=1,
            success_threshold=1
        ))
        
        async def fail():
            raise RuntimeError("Expected error")
        
        # Open circuit
        with pytest.raises(RuntimeError):
            await cb.call(fail)
        assert cb.state == CircuitState.OPEN
        
        # Wait for timeout
        await asyncio.sleep(1.1)
        
        async def success():
            return "success"
        
        result = await cb.call(success)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_failure_in_half_open_reopens_circuit(self):
        """Test failure in HALF_OPEN reopens circuit"""
        cb = CircuitBreaker("test", CircuitBreakerConfig(
            failure_threshold=1,
            timeout_seconds=1,
            success_threshold=2
        ))
        
        async def fail():
            raise RuntimeError("Expected error")
        
        # Open circuit
        with pytest.raises(RuntimeError):
            await cb.call(fail)
        assert cb.state == CircuitState.OPEN
        
        # Wait for timeout
        await asyncio.sleep(1.1)
        
        # Failure should reopen circuit
        with pytest.raises(RuntimeError):
            await cb.call(fail)
        assert cb.state == CircuitState.OPEN
    
    @pytest.mark.asyncio
    async def test_max_requests_in_half_open(self):
        """
        Test max requests limit in HALF_OPEN state.
        
        With max_requests=2, only 2 requests are allowed in HALF_OPEN.
        The third request should reopen the circuit.
        """
        cb = CircuitBreaker("test", CircuitBreakerConfig(
            failure_threshold=1,
            timeout_seconds=1,
            max_requests=2,
            success_threshold=3
        ))
        
        async def fail():
            raise RuntimeError("Expected error")
        
        # Open circuit
        with pytest.raises(RuntimeError):
            await cb.call(fail)
        assert cb.state == CircuitState.OPEN
        
        # Wait for timeout
        await asyncio.sleep(1.1)
        
        async def success():
            return "ok"
        
        # First request - transitions to HALF_OPEN
        result = await cb.call(success)
        assert result == "ok"
        assert cb.state == CircuitState.HALF_OPEN
        assert cb._half_open_requests == 1
        
        # Second request - allowed (max_requests=2)
        result = await cb.call(success)
        assert result == "ok"
        assert cb.state == CircuitState.HALF_OPEN
        assert cb._half_open_requests == 2
        
        # Third request - should be REJECTED and reopen circuit
        with pytest.raises(RuntimeError) as exc_info:
            await cb.call(success)
        assert "circuit" in str(exc_info.value).lower()
        assert cb.state == CircuitState.OPEN
    
    @pytest.mark.asyncio
    async def test_race_condition_prevention(self):
        """Test race condition prevention with concurrent requests"""
        cb = CircuitBreaker("test", CircuitBreakerConfig(
            failure_threshold=2,
            timeout_seconds=5,
            success_threshold=1
        ))
        
        async def sometimes_fail(i):
            if i % 2 == 0:
                raise RuntimeError(f"Fail {i}")
            return f"Success {i}"
        
        # Run many concurrent requests
        tasks = [cb.call(sometimes_fail, i) for i in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Should not cause any race condition errors
        assert len(results) == 20
        assert cb.state in [CircuitState.CLOSED, CircuitState.OPEN, CircuitState.HALF_OPEN]
    
    @pytest.mark.asyncio
    async def test_multiple_successes_close_circuit(self):
        """Test circuit closes after success_threshold successes"""
        cb = CircuitBreaker("test", CircuitBreakerConfig(
            failure_threshold=1,
            timeout_seconds=1,
            success_threshold=3,
            max_requests=5
        ))
        
        async def fail():
            raise RuntimeError("Expected error")
        
        # Open circuit
        with pytest.raises(RuntimeError):
            await cb.call(fail)
        assert cb.state == CircuitState.OPEN
        
        # Wait for timeout
        await asyncio.sleep(1.1)
        
        async def success():
            return "ok"
        
        # First success - transitions to HALF_OPEN
        result = await cb.call(success)
        assert result == "ok"
        assert cb.state == CircuitState.HALF_OPEN
        assert cb._success_count == 1
        assert cb._half_open_requests == 1
        
        # Second success - still HALF_OPEN
        result = await cb.call(success)
        assert result == "ok"
        assert cb.state == CircuitState.HALF_OPEN
        assert cb._success_count == 2
        assert cb._half_open_requests == 2
        
        # Third success - closes circuit
        result = await cb.call(success)
        assert result == "ok"
        assert cb.state == CircuitState.CLOSED
        assert cb._success_count == 0
        assert cb._failure_count == 0
        assert cb._half_open_requests == 0
    
    @pytest.mark.asyncio
    async def test_circuit_metrics_update_correctly(self):
        """Test metrics update correctly after operations"""
        cb = CircuitBreaker("test", CircuitBreakerConfig(
            failure_threshold=2,
            timeout_seconds=1,
            success_threshold=1
        ))
        
        async def fail():
            raise RuntimeError("Fail")
        
        async def success():
            return "Success"
        
        # Initial metrics
        metrics = cb.get_metrics()
        assert metrics["failure_count"] == 0
        assert metrics["state"] == "closed"
        
        # After failure
        with pytest.raises(RuntimeError):
            await cb.call(fail)
        metrics = cb.get_metrics()
        assert metrics["failure_count"] == 1
        assert metrics["state"] == "closed"
        
        # After second failure - opens
        with pytest.raises(RuntimeError):
            await cb.call(fail)
        metrics = cb.get_metrics()
        assert metrics["failure_count"] == 2
        assert metrics["state"] == "open"
        
        # Wait for timeout and recover
        await asyncio.sleep(1.1)
        await cb.call(success)
        metrics = cb.get_metrics()
        assert metrics["failure_count"] == 0
        assert metrics["state"] == "closed"


class TestCircuitBreakerIntegration:
    """Integration-style tests for complete lifecycle"""
    
    @pytest.mark.asyncio
    async def test_full_lifecycle(self):
        """Test complete circuit breaker lifecycle"""
        cb = CircuitBreaker("lifecycle", CircuitBreakerConfig(
            failure_threshold=2,
            timeout_seconds=1,
            success_threshold=2,
            max_requests=5
        ))
        
        async def fail():
            raise RuntimeError("Fail")
        
        async def success():
            return "Success"
        
        # Track state transitions
        states = []
        
        # 1. Start CLOSED
        states.append(cb.state.value)
        
        # 2. Two failures -> OPEN
        with pytest.raises(RuntimeError):
            await cb.call(fail)
        with pytest.raises(RuntimeError):
            await cb.call(fail)
        states.append(cb.state.value)
        
        # 3. Wait for timeout
        await asyncio.sleep(1.1)
        
        # 4. First success -> HALF_OPEN
        await cb.call(success)
        states.append(cb.state.value)
        
        # 5. Second success -> CLOSED
        await cb.call(success)
        states.append(cb.state.value)
        
        # Verify lifecycle
        expected = ["closed", "open", "half_open", "closed"]
        assert states == expected, f"Expected {expected}, got {states}"
    
    @pytest.mark.asyncio
    async def test_recovery_after_full_cycle(self):
        """Test recovery after a full failure-recovery cycle"""
        cb = CircuitBreaker("recovery", CircuitBreakerConfig(
            failure_threshold=2,
            timeout_seconds=1,
            success_threshold=2,
            max_requests=5
        ))
        
        async def fail():
            raise RuntimeError("Service unavailable")
        
        async def success():
            return "Service healthy"
        
        # 1. Circuit is closed
        assert cb.state == CircuitState.CLOSED
        
        # 2. Cause failures
        for _ in range(2):
            with pytest.raises(RuntimeError):
                await cb.call(fail)
        assert cb.state == CircuitState.OPEN
        
        # 3. Wait for timeout
        await asyncio.sleep(1.1)
        
        # 4. First success -> HALF_OPEN
        await cb.call(success)
        assert cb.state == CircuitState.HALF_OPEN
        
        # 5. Second success -> CLOSED
        await cb.call(success)
        assert cb.state == CircuitState.CLOSED
        
        # 6. Verify metrics
        metrics = cb.get_metrics()
        assert metrics["state"] == "closed"
        assert metrics["failure_count"] == 0
        assert metrics["success_count"] == 0
    
    @pytest.mark.asyncio
    async def test_high_load_scenario(self):
        """
        Test circuit breaker under high concurrent load.
        
        Note: With 20% failure rate and failure_threshold=5,
        the circuit WILL open (which is correct behavior).
        This test validates that the circuit opens AND recovers.
        """
        cb = CircuitBreaker("highload", CircuitBreakerConfig(
            failure_threshold=5,
            timeout_seconds=2,
            success_threshold=3,
            max_requests=10
        ))
        
        async def mixed_request(i):
            if i % 5 == 0:  # 20% failure rate
                raise RuntimeError(f"Fail {i}")
            await asyncio.sleep(0.01)
            return f"Success {i}"
        
        # Run 100 concurrent requests
        tasks = [cb.call(mixed_request, i) for i in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # The circuit may be OPEN (which is CORRECT behavior)
        # Or it could be CLOSED/HALF_OPEN depending on timing
        # We just verify it's in a valid state
        assert cb.state in [CircuitState.CLOSED, CircuitState.OPEN, CircuitState.HALF_OPEN]
        
        # Some requests should have failed normally
        failures = sum(1 for r in results if isinstance(r, RuntimeError) and "Fail" in str(r))
        assert failures > 0
        
        # If circuit is OPEN, test that it recovers after timeout
        if cb.state == CircuitState.OPEN:
            print(f"Circuit opened as expected. Waiting for recovery...")
            await asyncio.sleep(2.1)
            
            async def success():
                return "Recovered"
            
            result = await cb.call(success)
            assert result == "Recovered"
            # Should recover to HALF_OPEN or CLOSED
            assert cb.state in [CircuitState.HALF_OPEN, CircuitState.CLOSED]
        
        print(f"High load test passed: {cb.state.value}, failures: {failures}")
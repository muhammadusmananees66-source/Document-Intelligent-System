"""
Production-grade Circuit Breaker with async support.

Implements the standard circuit breaker pattern used in:
- Netflix Hystrix
- Resilience4j
- Spring Cloud Circuit Breaker

States:
- CLOSED: Normal operation, requests flow through
- OPEN: Failing fast, requests are rejected
- HALF_OPEN: Testing if service has recovered

Thread-safe with asyncio locks. All state transitions are atomic.
"""

import time
import asyncio
from enum import Enum
from typing import Optional, Callable, Any, Dict
import structlog

logger = structlog.get_logger()


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerConfig:
    """
    Configuration for circuit breaker.
    
    Attributes:
        failure_threshold: Number of failures before circuit opens
        success_threshold: Number of successes in HALF_OPEN to close circuit
        timeout_seconds: Time in OPEN state before attempting HALF_OPEN
        max_requests: Maximum requests allowed in HALF_OPEN state
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 3,
        timeout_seconds: int = 60,
        max_requests: int = 1
    ):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds
        self.max_requests = max_requests


class CircuitBreaker:
    """
    Production-grade circuit breaker with async support.
    
    Thread-safe implementation using asyncio locks.
    All state transitions are atomic and logged.
    
    Usage:
        cb = CircuitBreaker("service_name")
        
        async def call_service():
            return await cb.call(service_function, arg1, arg2)
    
    Reference: Netflix Hystrix pattern
    """
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        """
        Initialize circuit breaker.
        
        Args:
            name: Unique identifier for this circuit breaker
            config: Configuration (uses defaults if not provided)
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        
        # State
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._half_open_requests = 0
        self._last_state_change = time.time()
        
        # Thread safety - single lock held for entire operation
        self._lock: Optional[asyncio.Lock] = None
    
    async def _get_lock(self) -> asyncio.Lock:
        """Lazy initialization of lock to avoid event loop issues."""
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock
    
    @property
    def state(self) -> CircuitState:
        """Current circuit state."""
        return self._state
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed."""
        return self._state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open."""
        return self._state == CircuitState.OPEN
    
    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open."""
        return self._state == CircuitState.HALF_OPEN
    
    def _should_allow(self) -> bool:
        """
        Check if request should be allowed.
        
        Called WITH lock held to ensure thread safety.
        
        Returns:
            True if request should proceed, False if it should be rejected
        """
        if self._state == CircuitState.CLOSED:
            return True
        
        if self._state == CircuitState.OPEN:
            # Check if timeout has elapsed
            if time.time() - self._last_state_change >= self.config.timeout_seconds:
                self._state = CircuitState.HALF_OPEN
                # CRITICAL FIX: First request in HALF_OPEN counts toward max_requests
                self._half_open_requests = 1
                self._success_count = 0
                self._last_state_change = time.time()
                logger.info(
                    "Circuit half-open",
                    name=self.name,
                    timeout_seconds=self.config.timeout_seconds,
                    max_requests=self.config.max_requests
                )
                return True
            return False
        
        if self._state == CircuitState.HALF_OPEN:
            # Check max requests limit
            if self._half_open_requests >= self.config.max_requests:
                # Reopen circuit if max requests exceeded
                self._state = CircuitState.OPEN
                self._last_state_change = time.time()
                self._half_open_requests = 0
                self._success_count = 0
                logger.warning(
                    "Circuit reopened - max requests exceeded",
                    name=self.name,
                    max_requests=self.config.max_requests,
                    half_open_requests=self._half_open_requests
                )
                return False
            self._half_open_requests += 1
            return True
        
        return False
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with circuit breaker protection.
        
        CRITICAL: The lock is held for the ENTIRE operation to prevent
        race conditions between checking state and recording results.
        
        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Result of func
            
        Raises:
            RuntimeError: If circuit is open
            Exception: Any exception from func
        """
        lock = await self._get_lock()
        
        # Hold lock for the entire operation
        async with lock:
            if not self._should_allow():
                raise RuntimeError(f"Circuit '{self.name}' is open")
            
            try:
                result = await func(*args, **kwargs)
                self._record_success_unsafe()
                return result
            except Exception as e:
                self._record_failure_unsafe()
                raise
    
    def _record_success_unsafe(self) -> None:
        """
        Record a successful call.
        
        Called WITH lock held - UNSAFE without lock.
        """
        if self._state == CircuitState.CLOSED:
            self._failure_count = 0
        elif self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.config.success_threshold:
                self._close()
    
    def _record_failure_unsafe(self) -> None:
        """
        Record a failed call.
        
        Called WITH lock held - UNSAFE without lock.
        """
        self._failure_count += 1
        
        if self._state == CircuitState.CLOSED:
            if self._failure_count >= self.config.failure_threshold:
                self._open()
        elif self._state == CircuitState.HALF_OPEN:
            # Any failure in HALF_OPEN reopens the circuit
            self._open()
    
    def _open(self) -> None:
        """Open the circuit. Called WITH lock held."""
        self._state = CircuitState.OPEN
        self._last_state_change = time.time()
        self._half_open_requests = 0
        self._success_count = 0
        logger.warning(
            "Circuit opened",
            name=self.name,
            failure_count=self._failure_count,
            threshold=self.config.failure_threshold
        )
    
    def _close(self) -> None:
        """Close the circuit. Called WITH lock held."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._half_open_requests = 0
        logger.info(
            "Circuit closed",
            name=self.name,
            success_count=self._success_count,
            threshold=self.config.success_threshold
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get circuit breaker metrics for monitoring.
        
        Returns:
            Dictionary with current metrics
        """
        return {
            "name": self.name,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "half_open_requests": self._half_open_requests,
            "time_in_state": time.time() - self._last_state_change,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "timeout_seconds": self.config.timeout_seconds,
                "max_requests": self.config.max_requests,
            }
        }
    
    def reset(self) -> None:
        """Reset circuit to CLOSED state. For administrative use."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._half_open_requests = 0
        self._last_state_change = time.time()
        logger.info("Circuit reset", name=self.name)
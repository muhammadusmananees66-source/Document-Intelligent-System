"""Retry decorator with exponential backoff and jitter"""

import asyncio
import random
import time
from functools import wraps
from typing import Type, Tuple, Callable, Any, Optional
import structlog

logger = structlog.get_logger()


class RetryConfig:
    """Retry configuration"""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_multiplier: float = 2.0,
        jitter: bool = True,
        retry_on: Optional[Tuple[Type[Exception], ...]] = None,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter
        self.retry_on = retry_on or (Exception,)


def retry(config: Optional[RetryConfig] = None):
    """Retry decorator with exponential backoff"""
    
    config = config or RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except config.retry_on as e:
                    last_exception = e
                    
                    if attempt == config.max_retries:
                        logger.error(
                            "All retry attempts exhausted",
                            function=func.__name__,
                            attempts=attempt + 1,
                            error=str(e)
                        )
                        raise
                    
                    delay = config.base_delay * (config.backoff_multiplier ** attempt)
                    
                    if config.jitter:
                        delay *= random.uniform(0.8, 1.2)
                    
                    delay = min(delay, config.max_delay)
                    
                    logger.warning(
                        "Retrying after failure",
                        function=func.__name__,
                        attempt=attempt + 1,
                        delay=delay,
                        error=str(e)
                    )
                    
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except config.retry_on as e:
                    last_exception = e
                    
                    if attempt == config.max_retries:
                        logger.error(
                            "All retry attempts exhausted",
                            function=func.__name__,
                            attempts=attempt + 1,
                            error=str(e)
                        )
                        raise
                    
                    delay = config.base_delay * (config.backoff_multiplier ** attempt)
                    
                    if config.jitter:
                        delay *= random.uniform(0.8, 1.2)
                    
                    delay = min(delay, config.max_delay)
                    
                    logger.warning(
                        "Retrying after failure",
                        function=func.__name__,
                        attempt=attempt + 1,
                        delay=delay,
                        error=str(e)
                    )
                    
                    time.sleep(delay)
            
            raise last_exception
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
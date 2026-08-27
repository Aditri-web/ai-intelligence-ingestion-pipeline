"""
Rate Limiter & Retries Handler (429 Too Many Requests Mitigation).
Implements Exponential Backoff with Full Jitter and Token Bucket Rate Limiting
to ensure resilient LLM and HTTP API integrations.
"""

import asyncio
import random
import time
from typing import Callable, Any, TypeVar, Optional
from src.utils.logger import logger

T = TypeVar('T')

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60, max_retries: int = 5, base_delay: float = 1.0, max_delay: float = 60.0):
        self.rpm = requests_per_minute
        self.interval = 60.0 / requests_per_minute
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.last_request_time = 0.0
        # FIX: asyncio.Lock() must be created lazily inside a running event loop
        # Creating it at __init__ time causes DeprecationWarning / RuntimeError in Python 3.10+
        self._lock: Optional[asyncio.Lock] = None

    def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def acquire(self):
        """Token-bucket timing wait before launching API requests."""
        async with self._get_lock():
            now = time.time()
            elapsed = now - self.last_request_time
            if elapsed < self.interval:
                await asyncio.sleep(self.interval - elapsed)
            self.last_request_time = time.time()

    async def execute_with_retry(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Executes async function with exponential backoff + jitter for handling 429s or transient errors.
        Exponential backoff formula: backoff = min(max_delay, base_delay * (2 ^ attempt))
        Jitter: random_delay = random.uniform(0, backoff)
        """
        for attempt in range(self.max_retries + 1):
            await self.acquire()
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                err_msg = str(e)
                is_rate_limit = "429" in err_msg or "rate limit" in err_msg.lower() or "too many requests" in err_msg.lower()
                
                if attempt == self.max_retries:
                    logger.error(f"Max retries ({self.max_retries}) reached for function {func.__name__}. Last error: {e}")
                    raise e

                backoff = min(self.max_delay, self.base_delay * (2 ** attempt))
                # Full Jitter strategy: random value in [0, backoff] — proven best for distributed systems
                jitter = random.uniform(0, backoff)
                total_wait = jitter

                if is_rate_limit:
                    logger.warning(f"[429 Rate Limit Detected] Attempt {attempt+1}/{self.max_retries}. Backing off for {total_wait:.2f}s. Error: {e}")
                else:
                    logger.warning(f"[Transient Failure] Attempt {attempt+1}/{self.max_retries}. Retrying in {total_wait:.2f}s. Error: {e}")

                await asyncio.sleep(total_wait)

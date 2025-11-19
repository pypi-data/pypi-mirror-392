"""Speed optimizations for light-speed CHONKING ⚡"""

import aiohttp
import asyncio
from functools import wraps
from typing import Callable, Any
import time


def speed_decorator(func: Callable) -> Callable:
    """Decorator to measure and optimize CHONK speed"""

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        duration = time.perf_counter() - start

        if duration > 1.0:  # Log slow operations
            print(f"⚡ CHONK took {duration:.3f}s - still fast! 🦛")

        return result

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start

        if duration > 1.0:
            print(f"⚡ CHONK took {duration:.3f}s - still fast! 🦛")

        return result

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


class AIOHTTPPool:
    """Singleton aiohttp client session for performance"""
    _session = None

    @classmethod
    def get_session(cls) -> aiohttp.ClientSession:
        if cls._session is None:
            timeout = aiohttp.ClientTimeout(total=30)
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            cls._session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        return cls._session

    @classmethod
    async def close(cls):
        if cls._session:
            await cls._session.close()
            cls._session = None


def optimize_chunk_size(text: str, target_size: int) -> int:
    """Dynamically adjust chunk size based on content"""
    text_length = len(text)

    if text_length < target_size * 2:
        return int(text_length / 2)

    return target_size


async def batch_process(items: List[Any], processor: Callable, batch_size: int = 50):
    """Process items in batches for speed"""
    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = await asyncio.gather(*[processor(item) for item in batch])
        results.extend(batch_results)

    return results
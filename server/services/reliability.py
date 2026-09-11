import asyncio
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Hashable

from config import settings


@dataclass
class _CacheEntry:
    expires_at: float
    value: Any


_cache: dict[Hashable, _CacheEntry] = {}


def get_cached(key: Hashable) -> Any | None:
    entry = _cache.get(key)
    if entry is None:
        return None
    if entry.expires_at <= time.monotonic():
        _cache.pop(key, None)
        return None
    return entry.value


def set_cached(key: Hashable, value: Any, ttl: int | None = None) -> Any:
    _cache[key] = _CacheEntry(time.monotonic() + (ttl or settings.CACHE_TTL), value)
    return value


async def with_retries(operation: Callable[[], Awaitable[Any]], *, attempts: int = 3, initial_delay: float = 0.25,) -> Any:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return await operation()
        except Exception as error:
            last_error = error
            if attempt == attempts - 1:
                break
            await asyncio.sleep(initial_delay * (2**attempt))
    raise last_error or RuntimeError("Operation failed")

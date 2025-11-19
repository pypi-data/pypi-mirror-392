"""Caching module for pobapi."""

import hashlib
import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

__all__ = ["Cache", "cached", "clear_cache"]

T = TypeVar("T")


class Cache:
    """Simple in-memory cache with TTL support."""

    def __init__(self, default_ttl: int = 3600, max_size: int = 1000):
        """
        Create a Cache configured with a default time-to-live and a maximum size.

        Parameters:
            default_ttl (int): Default time-to-live for entries in
                seconds (defaults to 3600).
            max_size (int): Maximum number of cached items (defaults to 1000).
        """
        self._cache: dict[str, tuple[Any, float]] = {}
        self._default_ttl = default_ttl
        self._max_size = max_size

    def get(self, key: str) -> Any | None:
        """Get value from cache.

        :param key: Cache key.
        :return: Cached value or None if not found or expired.
        """
        if key not in self._cache:
            return None

        value, expiry_time = self._cache[key]
        if time.time() > expiry_time:
            # Expired, remove from cache
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        Store a value under the given key with an associated time-to-live.

        Parameters:
            key (str): Cache key under which the value will be stored.
            value (Any): Value to cache.
            ttl (int | None): Time-to-live in seconds for this entry;
                when None, the cache's default_ttl is used.

        Notes:
            If the cache is at max_size and the key is not already
            present, the oldest entry will be evicted before inserting.
        """
        # Evict oldest entries if cache is full
        if len(self._cache) >= self._max_size and key not in self._cache:
            self._evict_oldest()

        ttl = ttl or self._default_ttl
        expiry_time = time.time() + ttl
        self._cache[key] = (value, expiry_time)

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()

    def delete(self, key: str) -> None:
        """
        Remove the cache entry for the given key if present.

        Parameters:
            key (str): The cache key to remove; no error is raised if
                the key is missing.
        """
        self._cache.pop(key, None)

    def _evict_oldest(self) -> None:
        """
        Remove the cache entry with the earliest expiry time.

        This is a no-op if the cache is empty.
        """
        if not self._cache:
            return

        # Find oldest entry (lowest expiry time)
        oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
        del self._cache[oldest_key]

    def size(self) -> int:
        """Get current cache size.

        :return: Number of cached items.
        """
        return len(self._cache)

    def stats(self) -> dict[str, Any]:
        """
        Return basic statistics about the cache.

        Returns:
            dict: Dictionary with keys:
                - "size": current number of cached items.
                - "max_size": maximum allowed number of cached items.
                - "default_ttl": default time-to-live for entries, in seconds.
        """
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "default_ttl": self._default_ttl,
        }


# Global cache instance
_default_cache = Cache(default_ttl=3600, max_size=1000)


def _make_key(*args, **kwargs) -> str:
    """
    Create a deterministic cache key for a function call from its
    positional and keyword arguments.

    Keyword arguments are sorted before hashing so equivalent kwargs
    orderings produce the same key.

    Parameters:
        args: Positional arguments passed to the function.
        kwargs: Keyword arguments passed to the function.

    Returns:
        str: Hexadecimal MD5 hash representing the combined arguments.
    """
    # Create a hash of the arguments
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(ttl: int | None = None, cache_instance: Cache | None = None):
    """
    Create a decorator that caches a function's return values using a
    Cache and an optional TTL.

    Parameters:
        ttl (int | None): Time-to-live for cache entries in seconds;
            when None the cache's default TTL is used.
        cache_instance (Cache | None): Cache instance to use for storing
            results; when None the module default cache is used.

    Returns:
        Callable: A decorator that caches results of the decorated
            function keyed by the function's module, name, and call
            arguments; on a cache hit the stored value is returned,
            otherwise the function is executed and its result is stored
            and returned.
    """
    cache = cache_instance or _default_cache

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        """
        Wraps a callable to cache its return values using a key composed
        of the function's module, name, and hashed arguments.

        The wrapper returns a cached result when a non-expired entry
        exists for the call; otherwise it invokes the original function,
        stores the result in the cache using the decorator's TTL, and
        returns the freshly computed value.

        Parameters:
            func (Callable[..., T]): The function to wrap and cache.

        Returns:
            Callable[..., T]: A wrapper that behaves like `func` but
                caches its results per-argument.
        """

        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            key = f"{func.__module__}.{func.__name__}:{_make_key(*args, **kwargs)}"
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value  # type: ignore[no-any-return]

            result = func(*args, **kwargs)
            cache.set(key, result, ttl=ttl)
            return result

        return wrapper

    return decorator


def clear_cache() -> None:
    """Clear the default cache."""
    _default_cache.clear()


def get_cache() -> Cache:
    """
    Return the module's default cache instance.

    Returns:
        Cache: The shared default Cache used by the module's caching utilities.
    """
    return _default_cache

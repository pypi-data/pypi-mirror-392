"""Unit tests for cache module."""

import time
from datetime import datetime, timedelta

from freezegun import freeze_time

from pobapi.cache import Cache, cached, clear_cache, get_cache


class TestCache:
    """Tests for Cache class."""

    def test_get_set(self):
        """Test basic get/set operations."""
        cache = Cache()
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_nonexistent(self):
        """Test getting non-existent key."""
        cache = Cache()
        assert cache.get("nonexistent") is None

    def test_expiry(self):
        """Test cache expiry."""
        base_time = datetime(2024, 1, 1, 0, 0, 0)
        with freeze_time(base_time) as frozen_time:
            cache = Cache(default_ttl=1)  # 1 second TTL
            cache.set("key1", "value1")
            assert cache.get("key1") == "value1"
            # Advance time by 1.1 seconds
            frozen_time.tick(timedelta(seconds=1.1))
            assert cache.get("key1") is None

    def test_custom_ttl(self):
        """Test custom TTL."""
        base_time = datetime(2024, 1, 1, 0, 0, 0)
        with freeze_time(base_time) as frozen_time:
            cache = Cache(default_ttl=10)
            cache.set("key1", "value1", ttl=1)
            assert cache.get("key1") == "value1"
            # Advance time by 1.1 seconds
            frozen_time.tick(timedelta(seconds=1.1))
            assert cache.get("key1") is None

    def test_clear(self):
        """Test clearing cache."""
        cache = Cache()
        cache.set("key1", "value1")
        cache.clear()
        assert cache.get("key1") is None

    def test_delete(self):
        """Test deleting specific key."""
        cache = Cache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.delete("key1")
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"

    def test_size(self):
        """Test cache size."""
        cache = Cache()
        assert cache.size() == 0
        cache.set("key1", "value1")
        assert cache.size() == 1
        cache.set("key2", "value2")
        assert cache.size() == 2

    def test_stats(self):
        """Test cache statistics."""
        cache = Cache(default_ttl=3600, max_size=1000)
        stats = cache.stats()
        assert stats["size"] == 0
        assert stats["max_size"] == 1000
        assert stats["default_ttl"] == 3600

    def test_evict_oldest(self):
        """Test evicting oldest entry when cache is full."""
        cache = Cache(default_ttl=10, max_size=2)
        cache.set("key1", "value1")
        time.sleep(0.1)  # Make key1 older
        cache.set("key2", "value2")
        # Adding third key should evict oldest (key1)
        cache.set("key3", "value3")
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_no_evict_if_key_exists(self):
        """Test that existing keys are not evicted."""
        cache = Cache(default_ttl=10, max_size=2)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        # Updating existing key should not evict
        cache.set("key1", "value1_updated")
        assert cache.get("key1") == "value1_updated"
        assert cache.get("key2") == "value2"

    def test_evict_oldest_empty_cache(self):
        """Test eviction when inserting into full cache via public API."""
        cache = Cache(default_ttl=10, max_size=1)
        # Insert first entry
        cache.set("key1", "value1")
        assert cache.size() == 1
        assert cache.get("key1") == "value1"
        # Insert second entry should evict first (cache is full)
        cache.set("key2", "value2")
        # Verify eviction occurred
        assert cache.size() == 1  # Should not exceed max_size
        assert cache.get("key1") is None  # Oldest entry evicted
        assert cache.get("key2") == "value2"  # New entry present


class TestCachedDecorator:
    """Tests for @cached decorator."""

    def test_cached_function(self):
        """Test caching function results."""
        call_count = 0
        test_cache = Cache(default_ttl=10)

        @cached(ttl=10, cache_instance=test_cache)
        def test_func(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = test_func(5)
        assert result1 == 10
        assert call_count == 1

        result2 = test_func(5)
        assert result2 == 10
        assert call_count == 1  # Should use cache

    def test_cache_expiry(self):
        """Test cache expiry for decorated function."""
        base_time = datetime(2024, 1, 1, 0, 0, 0)
        with freeze_time(base_time) as frozen_time:
            call_count = 0
            test_cache = Cache(default_ttl=1)

            @cached(ttl=1, cache_instance=test_cache)
            def test_func(x: int) -> int:
                nonlocal call_count
                call_count += 1
                return x * 2

            test_func(5)
            assert call_count == 1
            # Advance time by 1.1 seconds
            frozen_time.tick(timedelta(seconds=1.1))
            test_func(5)
            assert call_count == 2  # Should call again after expiry

    def test_different_arguments(self):
        """Test that different arguments create different cache entries."""
        call_count = 0
        test_cache = Cache(default_ttl=10)

        @cached(ttl=10, cache_instance=test_cache)
        def test_func(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        test_func(5)
        test_func(10)
        assert call_count == 2  # Different arguments = different calls


class TestCacheFunctions:
    """Tests for cache utility functions."""

    def test_get_cache(self):
        """Test getting default cache."""
        cache = get_cache()
        assert isinstance(cache, Cache)

    def test_clear_cache(self):
        """Test clearing default cache."""
        cache = get_cache()
        cache.set("key1", "value1")
        clear_cache()
        assert cache.get("key1") is None

"""Integration tests for Infrastructure components (HTTPClient, Cache, etc.)."""

import pytest

pytestmark = pytest.mark.integration

from unittest.mock import MagicMock  # noqa: E402

from pobapi import PathOfBuildingAPI  # noqa: E402
from pobapi.cache import Cache  # noqa: E402
from pobapi.factory import BuildFactory  # noqa: E402
from pobapi.interfaces import HTTPClient  # noqa: E402


class TestHTTPClientBuildFactoryIntegration:
    """Test integration between HTTPClient and BuildFactory."""

    def test_factory_with_custom_http_client(self) -> None:
        """Test BuildFactory with custom HTTPClient."""
        # Create mock HTTP client
        mock_client = MagicMock(spec=HTTPClient)
        mock_client.get.return_value = "test_import_code"

        # Create factory with custom client
        factory = BuildFactory(http_client=mock_client)

        # Factory should use custom client
        assert factory._http_client is mock_client

    def test_factory_from_url_uses_http_client(self) -> None:
        """Test BuildFactory.from_url uses injected HTTPClient."""
        import base64
        import zlib

        # Create a valid import code (base64 encoded zlib compressed XML)
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills/>
            <Items/>
            <Tree/>
        </PathOfBuilding>"""
        compressed = zlib.compress(xml_str.encode())
        import_code = base64.urlsafe_b64encode(compressed).decode()

        # Create mock HTTP client that returns valid import code
        mock_client = MagicMock(spec=HTTPClient)
        mock_client.get.return_value = import_code

        # Create factory with custom client
        factory = BuildFactory(http_client=mock_client)

        # Call from_url - this should use mock_client.get
        xml_bytes = factory.from_url("https://pastebin.com/test")

        # Verify HTTP client was used
        assert xml_bytes is not None
        # Verify mock_client.get was called once with the raw URL
        mock_client.get.assert_called_once_with(
            "https://pastebin.com/raw/test", timeout=6.0
        )

    def test_factory_async_with_custom_http_client(self) -> None:
        """Test BuildFactory async methods with custom AsyncHTTPClient."""
        from pobapi.interfaces import AsyncHTTPClient

        # Create mock async HTTP client
        mock_async_client = MagicMock(spec=AsyncHTTPClient)

        # Create factory with custom async client
        factory = BuildFactory(async_http_client=mock_async_client)

        # Factory should use custom async client
        assert factory._async_http_client is mock_async_client


class TestCacheIntegration:
    """Test integration of Cache with API components."""

    def test_cache_with_factory(self) -> None:
        """Test Cache integration with BuildFactory through HTTP client caching."""
        import base64
        import zlib

        # Create cache
        cache = Cache(max_size=100, default_ttl=3600)

        # Create a valid import code (base64 encoded zlib compressed XML)
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills/>
            <Items/>
            <Tree/>
        </PathOfBuilding>"""
        compressed = zlib.compress(xml_str.encode())
        import_code = base64.urlsafe_b64encode(compressed).decode()

        # Create HTTP client that uses cache
        class CachedHTTPClient:
            """HTTP client that caches responses using provided cache."""

            def __init__(self, cache: Cache):
                self._cache = cache
                self._call_count = 0

            def get(self, url: str, timeout: float = 6.0) -> str:
                """Fetch from cache or return mock data."""
                cache_key = f"http:{url}"
                cached_value = self._cache.get(cache_key)
                if cached_value is not None:
                    return cached_value

                # Simulate HTTP call
                self._call_count += 1
                # Return import code for pastebin URLs
                response = import_code
                self._cache.set(cache_key, response)
                return response

        # Create cached HTTP client
        cached_client = CachedHTTPClient(cache)

        # Create factory with cached HTTP client
        factory = BuildFactory(http_client=cached_client)

        # First call should fetch from HTTP (cache miss)
        url = "https://pastebin.com/test"
        xml_bytes_1 = factory.from_url(url)

        # Verify HTTP client was called
        assert cached_client._call_count == 1
        assert cache.size() == 1
        assert xml_bytes_1 is not None

        # Second call should use cache (cache hit)
        xml_bytes_2 = factory.from_url(url)

        # Verify HTTP client was NOT called again (served from cache)
        assert cached_client._call_count == 1
        assert cache.size() == 1
        assert xml_bytes_2 == xml_bytes_1

    def test_cache_stores_and_retrieves_data(self) -> None:
        """Test Cache stores and retrieves data correctly."""
        cache = Cache(max_size=10, default_ttl=3600)

        # Store data
        cache.set("test_key", "test_value")

        # Retrieve data
        value = cache.get("test_key")

        assert value == "test_value"

    def test_cache_integration_with_api_parsing(self, sample_xml: str) -> None:
        """Test Cache can be used alongside API parsing."""
        from lxml.etree import fromstring

        # Create cache
        cache = Cache(max_size=100, default_ttl=3600)

        # Use sample XML from fixture
        xml_bytes = sample_xml.encode()
        xml_root = fromstring(xml_bytes)

        # Create API instance
        build = PathOfBuildingAPI(xml_root)

        # Cache and API should work independently
        cache.set("build_xml", xml_bytes)
        cached_xml = cache.get("build_xml")

        assert cached_xml == xml_bytes
        assert build is not None


class TestHTTPClientCacheIntegration:
    """Test integration between HTTPClient and Cache."""

    def test_http_client_with_caching_strategy(self) -> None:
        """Test HTTPClient can work with caching strategy."""
        # Create cache
        cache = Cache(max_size=100, default_ttl=3600)

        # Create mock HTTP client
        mock_client = MagicMock(spec=HTTPClient)
        mock_client.get.return_value = "cached_response"

        # Simulate caching: check cache first, then HTTP client
        cache_key = "url:https://example.com"
        cached_value = cache.get(cache_key)

        if cached_value is None:
            # Fetch from HTTP client
            response = mock_client.get("https://example.com")
            # Store in cache
            cache.set(cache_key, response)

        # Verify integration
        assert cache is not None
        assert mock_client is not None

        # Verify cache-first behavior: second request should use cached value
        second_cached_value = cache.get(cache_key)
        assert second_cached_value == "cached_response"
        # Verify HTTP client was not called again (only called once initially)
        assert mock_client.get.call_count == 1
        mock_client.get.assert_called_once_with("https://example.com")

    def test_factory_http_cache_integration(self) -> None:
        """Test BuildFactory with HTTP client and cache together."""
        # Create cache
        cache = Cache(max_size=100, default_ttl=3600)

        # Create mock HTTP client
        mock_client = MagicMock(spec=HTTPClient)
        mock_client.get.return_value = "test_response"

        # Create factory
        factory = BuildFactory(http_client=mock_client)

        # Both should work together
        cache.set("test", "value")
        assert cache.get("test") == "value"
        assert factory._http_client is mock_client


class TestInfrastructureErrorHandling:
    """Test error handling in infrastructure components."""

    def test_factory_handles_http_errors(self) -> None:
        """Test BuildFactory handles HTTP client errors."""
        from pobapi.exceptions import NetworkError

        # Create mock HTTP client that raises error
        mock_client = MagicMock(spec=HTTPClient)
        mock_client.get.side_effect = NetworkError("Connection failed")

        # Create factory with error-prone client
        factory = BuildFactory(http_client=mock_client)

        # Factory should still be usable (errors handled in from_url)
        assert factory is not None

        # Call from_url and verify NetworkError is raised
        with pytest.raises(NetworkError, match="Connection failed"):
            factory.from_url("https://pastebin.com/test")

    def test_cache_handles_eviction(self) -> None:
        """Test Cache handles eviction when full."""
        # Create small cache
        cache = Cache(max_size=2, default_ttl=3600)

        # Fill cache
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1

        # key1 should be evicted
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

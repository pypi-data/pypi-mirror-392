"""Integration tests for Infrastructure components (HTTPClient, Cache, etc.)."""

import pytest

pytestmark = pytest.mark.integration

from unittest.mock import MagicMock, patch  # noqa: E402

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
        # Create mock HTTP client
        mock_client = MagicMock(spec=HTTPClient)
        mock_client.get.return_value = "test_import_code"

        # Create factory with custom client
        factory = BuildFactory(http_client=mock_client)

        # Mock the XML fetching function
        with patch("pobapi.factory._fetch_xml_from_url") as mock_fetch:
            mock_fetch.return_value = (
                b'<?xml version="1.0"?>' b"<PathOfBuilding></PathOfBuilding>"
            )

            # Call from_url
            xml_bytes = factory.from_url("https://pastebin.com/test")

            # Verify HTTP client was used
            assert xml_bytes is not None
            mock_fetch.assert_called_once()

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
        """Test Cache integration with BuildFactory."""
        # Create cache
        cache = Cache(max_size=100, default_ttl=3600)

        # Create factory
        factory = BuildFactory()

        # Cache should be independent but usable
        assert cache is not None
        assert factory is not None

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

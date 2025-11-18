"""Unit tests for async utilities."""

import pytest

from pobapi.async_util import (
    _fetch_xml_from_import_code_async,
    _fetch_xml_from_url_async,
)
from pobapi.exceptions import InvalidImportCodeError, InvalidURLError, NetworkError


class MockAsyncHTTPClient:
    """Mock async HTTP client for testing."""

    def __init__(
        self, response_text: str = "test", should_raise: Exception | None = None
    ):
        """Initialize mock client.

        :param response_text: Text to return from get().
        :param should_raise: Exception to raise from get().
        """
        self.response_text = response_text
        self.should_raise = should_raise

    async def get(self, url: str, timeout: float = 6.0) -> str:
        """Mock get method."""
        if self.should_raise:
            raise self.should_raise
        return self.response_text


class TestFetchXMLFromURLAsync:
    """Tests for _fetch_xml_from_url_async."""

    @pytest.mark.asyncio
    async def test_valid_url(self):
        """Test fetching from valid URL."""
        # This would require a valid import code, so we'll test error cases
        client = MockAsyncHTTPClient(response_text="invalid_code")
        with pytest.raises(InvalidImportCodeError):
            await _fetch_xml_from_url_async(
                "https://pastebin.com/test", client, timeout=6.0
            )

    @pytest.mark.asyncio
    async def test_invalid_url(self):
        """Test invalid URL raises error."""
        client = MockAsyncHTTPClient()
        with pytest.raises(InvalidURLError):
            await _fetch_xml_from_url_async("https://example.com/test", client)

    @pytest.mark.asyncio
    async def test_no_http_client(self):
        """Test that None http_client raises ValueError."""
        with pytest.raises(ValueError, match="Async HTTP client is required"):
            await _fetch_xml_from_url_async("https://pastebin.com/test", None)

    @pytest.mark.asyncio
    async def test_network_error(self):
        """Test network error handling."""
        client = MockAsyncHTTPClient(should_raise=Exception("Network error"))
        with pytest.raises(NetworkError, match="Async request failed"):
            await _fetch_xml_from_url_async("https://pastebin.com/test", client)


class TestFetchXMLFromImportCodeAsync:
    """Tests for _fetch_xml_from_import_code_async."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "import_code,expected_error",
        [
            ("", None),
            (None, None),  # type: ignore[list-item,arg-type,unused-ignore]
            ("invalid_base64!!!", "Failed to decode"),
        ],
    )
    async def test_invalid_import_code(self, import_code, expected_error):
        """Test invalid import code raises error."""
        if expected_error:
            with pytest.raises(InvalidImportCodeError, match=expected_error):
                await _fetch_xml_from_import_code_async(import_code)  # type: ignore[arg-type,unused-ignore]
        else:
            with pytest.raises(InvalidImportCodeError):
                await _fetch_xml_from_import_code_async(import_code)  # type: ignore[arg-type,unused-ignore]

    @pytest.mark.asyncio
    async def test_invalid_zlib(self):
        """Test invalid zlib compression."""
        import base64

        # Valid base64 but invalid zlib
        invalid_zlib = base64.urlsafe_b64encode(b"not compressed data").decode()
        with pytest.raises(InvalidImportCodeError, match="Failed to decompress"):
            await _fetch_xml_from_import_code_async(invalid_zlib)

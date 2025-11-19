"""Tests for HTTP client implementations."""

from unittest.mock import Mock, patch

import pytest

from pobapi.exceptions import NetworkError
from pobapi.util import _fetch_xml_from_url, _get_default_http_client


# Clear the cached default client before each test
@pytest.fixture(autouse=True)
def clear_http_client_cache():
    """Clear the cached default HTTP client before each test."""
    import pobapi.util

    pobapi.util._default_http_client = None
    yield
    pobapi.util._default_http_client = None


class TestRequestsHTTPClient:
    """Tests for RequestsHTTPClient implementation."""

    def test_get_default_http_client(self):
        """Test getting default HTTP client."""
        client = _get_default_http_client()
        assert client is not None
        assert hasattr(client, "get")

    @patch("requests.get")
    def test_get_success(self, mock_get):
        """Test successful HTTP request."""
        mock_response = Mock()
        mock_response.text = "test content"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = _get_default_http_client()
        result = client.get("https://example.com", timeout=5.0)
        assert result == "test content"
        mock_get.assert_called_once_with("https://example.com", timeout=5.0)

    @patch("requests.get")
    def test_get_timeout(self, mock_get):
        """Test HTTP request timeout."""
        import requests

        mock_get.side_effect = requests.Timeout("Connection timed out")
        client = _get_default_http_client()
        with pytest.raises(NetworkError, match="Connection timed out"):
            client.get("https://example.com", timeout=5.0)

    @patch("requests.get")
    def test_get_connection_error(self, mock_get):
        """Test HTTP connection error."""
        import requests

        mock_get.side_effect = requests.ConnectionError("Connection failed")
        client = _get_default_http_client()
        with pytest.raises(NetworkError, match="Network connection failed"):
            client.get("https://example.com")

    @patch("requests.get")
    def test_get_http_error(self, mock_get):
        """Test HTTP error response."""
        import requests

        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.side_effect = requests.HTTPError(response=mock_response)
        client = _get_default_http_client()
        with pytest.raises(NetworkError, match="HTTP error"):
            client.get("https://example.com")

    @patch("requests.get")
    def test_get_too_many_redirects(self, mock_get):
        """Test too many redirects error."""
        import requests

        mock_get.side_effect = requests.TooManyRedirects("Too many redirects")
        client = _get_default_http_client()
        with pytest.raises(NetworkError, match="Too many redirects"):
            client.get("https://example.com")

    @patch("requests.get")
    def test_get_request_exception(self, mock_get):
        """Test general request exception."""
        import requests

        mock_get.side_effect = requests.RequestException("Request failed")
        client = _get_default_http_client()
        with pytest.raises(NetworkError, match="Request failed"):
            client.get("https://example.com")

    @patch("pobapi.util._get_default_http_client")
    @patch("pobapi.util._fetch_xml_from_import_code")
    def test_fetch_xml_from_url_with_custom_client(
        self, mock_fetch_xml, mock_get_client
    ):
        """Test _fetch_xml_from_url with custom HTTP client."""
        mock_client = Mock()
        mock_client.get.return_value = "test_import_code"
        mock_fetch_xml.return_value = b"<xml>test</xml>"

        result = _fetch_xml_from_url(
            "https://pastebin.com/test", http_client=mock_client
        )
        assert result == b"<xml>test</xml>"
        mock_client.get.assert_called_once()
        mock_get_client.assert_not_called()

    def test_fetch_xml_from_url_invalid_url(self):
        """Test _fetch_xml_from_url with invalid URL."""
        from pobapi.exceptions import InvalidURLError

        with pytest.raises(InvalidURLError):
            _fetch_xml_from_url("https://example.com/test")

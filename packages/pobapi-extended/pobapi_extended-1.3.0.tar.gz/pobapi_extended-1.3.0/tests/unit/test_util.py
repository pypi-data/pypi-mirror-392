"""Unit tests for utility functions."""

import pytest
import requests

from pobapi.exceptions import (
    InvalidImportCodeError,
    InvalidURLError,
    NetworkError,
)
from pobapi.util import (
    _fetch_xml_from_import_code,
    _fetch_xml_from_url,
    _get_stat,
    _item_text,
)


class TestFetchXMLFromURL:
    """Tests for _fetch_xml_from_url."""

    def test_invalid_url(self):
        """Test invalid URL raises error."""
        with pytest.raises(InvalidURLError):
            _fetch_xml_from_url("https://example.com/test")

    @pytest.mark.parametrize(
        "exception_class,error_match",
        [
            (requests.Timeout, "Connection timed out"),
            (requests.ConnectionError, "Network connection failed"),
            (requests.TooManyRedirects, "Too many redirects"),
            (requests.RequestException, "Request failed"),
        ],
    )
    def test_network_errors(self, mocker, exception_class, error_match):
        """Test various network error handling."""
        # Clear cache to ensure fresh client creation
        import importlib

        util_module = importlib.import_module("pobapi.util")

        util_module._default_http_client = None

        mock_get = mocker.patch("requests.get")
        # Create exception instance properly
        if exception_class == requests.Timeout:
            mock_get.side_effect = requests.Timeout("Connection timeout")
        elif exception_class == requests.ConnectionError:
            mock_get.side_effect = requests.ConnectionError("Connection failed")
        elif exception_class == requests.TooManyRedirects:
            mock_get.side_effect = requests.TooManyRedirects("Too many redirects")
        else:
            mock_get.side_effect = requests.RequestException("Generic error")
        with pytest.raises(NetworkError, match=error_match):
            _fetch_xml_from_url("https://pastebin.com/test")

    def test_http_error(self, mocker):
        """Test HTTP error handling."""
        # Clear cache to ensure fresh client creation
        import importlib

        util_module = importlib.import_module("pobapi.util")

        util_module._default_http_client = None

        mock_get = mocker.patch("requests.get")
        mock_response = mocker.Mock()
        mock_response.status_code = 404
        mock_get.side_effect = requests.HTTPError(response=mock_response)
        with pytest.raises(NetworkError, match="HTTP error"):
            _fetch_xml_from_url("https://pastebin.com/test")


class TestFetchXMLFromImportCode:
    """Tests for _fetch_xml_from_import_code."""

    @pytest.mark.parametrize(
        "import_code,expected_error",
        [
            ("", None),
            (None, None),  # type: ignore[list-item,arg-type,unused-ignore]
            ("invalid_base64!!!", "Failed to decode"),
        ],
    )
    def test_invalid_import_code(self, import_code, expected_error):
        """Test invalid import code raises error."""
        if expected_error:
            with pytest.raises(InvalidImportCodeError, match=expected_error):
                _fetch_xml_from_import_code(import_code)  # type: ignore[arg-type,unused-ignore]
        else:
            with pytest.raises(InvalidImportCodeError):
                _fetch_xml_from_import_code(import_code)  # type: ignore[arg-type,unused-ignore]

    def test_invalid_zlib(self):
        """Test invalid zlib compression."""
        import base64

        # Valid base64 but invalid zlib
        invalid_zlib = base64.urlsafe_b64encode(b"not compressed data").decode()
        with pytest.raises(InvalidImportCodeError, match="Failed to decompress"):
            _fetch_xml_from_import_code(invalid_zlib)


class TestGetStat:
    """Tests for _get_stat function."""

    @pytest.mark.parametrize(
        "text,stat,expected",
        [
            (["Rarity: Unique", "Quality: 20"], "Rarity: ", "Unique"),
            (["Rarity: Unique", "Quality: 20"], "Quality: ", "20"),
            (["Shaper Item", "Elder Item"], "Shaper Item", True),
            (["Shaper Item", "Elder Item"], "Elder Item", True),
            (["Rarity: Unique"], "Quality: ", ""),
            ([], "Rarity: ", ""),
        ],
    )
    def test_get_stat(self, text, stat, expected):
        """Test getting stat from text."""
        assert _get_stat(text, stat) == expected


class TestItemText:
    """Tests for _item_text function."""

    @pytest.mark.parametrize(
        "text,expected_items,expected_not_in",
        [
            (
                [
                    "Rarity: Unique",
                    "Test Item",
                    "Implicits: 2",
                    "+10 to maximum Life",
                    "+20 to maximum Mana",
                ],
                ["+10 to maximum Life", "+20 to maximum Mana"],
                ["Rarity: Unique"],
            ),
            (["Rarity: Unique", "Test Item"], [], []),
            (["Rarity: Unique", "Test Item", "Implicits: 1"], [], []),
        ],
    )
    def test_item_text(self, text, expected_items, expected_not_in):
        """Test extracting item text after Implicits."""
        result = list(_item_text(text))
        for item in expected_items:
            assert item in result
        for item in expected_not_in:
            assert item not in result


class TestGetPos:
    """Tests for _get_pos function."""

    @pytest.mark.parametrize(
        "text,stat,expected",
        [
            (["Rarity: Unique", "Quality: 20", "LevelReq: 68"], "Quality: ", 1),
            (["Rarity: Unique", "Quality: 20", "LevelReq: 68"], "LevelReq: ", 2),
            (["Rarity: Unique"], "Quality: ", None),
        ],
    )
    def test_get_pos(self, text, stat, expected):
        """Test getting position of stat."""
        from pobapi.util import _get_pos

        assert _get_pos(text, stat) == expected

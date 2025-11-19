"""Tests for factory functions (from_url, from_import_code)."""

import pytest

from pobapi import api
from pobapi.exceptions import (
    InvalidImportCodeError,
    InvalidURLError,
    ParsingError,
)


class TestFromURL:
    """Tests for from_url function."""

    def test_from_url_with_custom_timeout(self, mocker):
        """TC-API-003: Load build from URL with custom timeout."""
        # Mock the HTTP request
        mock_fetch = mocker.patch("pobapi.api._fetch_xml_from_url")
        mock_fetch.return_value = b"""<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills/>
            <Items/>
            <Tree/>
        </PathOfBuilding>"""

        url = "https://pastebin.com/raw/test123"
        build = api.from_url(url, timeout=10.0)

        assert build is not None
        assert build.class_name == "Scion"
        mock_fetch.assert_called_once_with(url, 10.0)

    def test_from_url_with_invalid_url(self):
        """TC-API-005: Load build from invalid URL."""
        invalid_url = "https://example.com/test"

        with pytest.raises(InvalidURLError):
            api.from_url(invalid_url)

    def test_from_url_network_error(self, mocker):
        """TC-API-006: Network error handling."""
        from pobapi.exceptions import NetworkError

        # Mock network error
        mock_fetch = mocker.patch("pobapi.api._fetch_xml_from_url")
        mock_fetch.side_effect = NetworkError("Connection timeout")

        url = "https://pastebin.com/raw/test123"

        with pytest.raises(NetworkError, match="Connection timeout"):
            api.from_url(url)

    def test_from_url_parsing_error(self, mocker):
        """TC-API-007: Parsing error handling."""
        # Mock invalid XML response
        mock_fetch = mocker.patch("pobapi.api._fetch_xml_from_url")
        mock_fetch.return_value = b"<invalid>xml</invalid>"

        url = "https://pastebin.com/raw/test123"

        with pytest.raises(ParsingError):
            api.from_url(url)


class TestFromImportCode:
    """Tests for from_import_code function."""

    def test_from_import_code_with_invalid_code(self):
        """TC-API-004: Load build from invalid import code."""
        invalid_codes = ["", None, "invalid_code", "123"]

        for invalid_code in invalid_codes:
            with pytest.raises(InvalidImportCodeError):
                api.from_import_code(invalid_code)  # type: ignore[arg-type]

    def test_from_import_code_parsing_error(self, mocker):
        """TC-API-007: Parsing error handling for import code."""
        # Mock invalid XML from import code
        mock_fetch = mocker.patch("pobapi.api._fetch_xml_from_import_code")
        mock_fetch.return_value = b"<invalid>xml</invalid>"

        import_code = "eNpVzMEKgzAMBuBXyXkP0g=="

        with pytest.raises(ParsingError):
            api.from_import_code(import_code)

"""Tests for interfaces module."""

import pytest

from pobapi.interfaces import (
    AsyncHTTPClient,
    BuildParser,
    HTTPClient,
    XMLParser,
)


class TestHTTPClient:
    """Tests for HTTPClient protocol."""

    def test_http_client_protocol(self, mocker) -> None:
        """Test HTTPClient protocol implementation."""
        mock_client = mocker.Mock()
        mock_client.get = mocker.Mock(return_value="response")

        # Protocol should be runtime checkable
        assert isinstance(mock_client, HTTPClient)
        assert mock_client.get("http://example.com") == "response"


class TestAsyncHTTPClient:
    """Tests for AsyncHTTPClient protocol."""

    def test_async_http_client_protocol(self, mocker) -> None:
        """Test AsyncHTTPClient protocol implementation."""

        async def mock_get(url: str, timeout: float = 6.0) -> str:
            return "async_response"

        mock_client = mocker.Mock()
        mock_client.get = mock_get

        # Protocol should be runtime checkable
        assert isinstance(mock_client, AsyncHTTPClient)


class TestXMLParser:
    """Tests for XMLParser abstract class."""

    def test_xml_parser_abstract(self) -> None:
        """Test XMLParser is abstract."""

        class ConcreteParser(XMLParser):
            def parse(self, xml_bytes: bytes) -> dict:
                return {"parsed": True}

        parser = ConcreteParser()
        result = parser.parse(b"<root></root>")
        assert result == {"parsed": True}

    def test_xml_parser_abstract_raises(self) -> None:
        """Test XMLParser raises error if not implemented."""
        with pytest.raises(TypeError):
            XMLParser()  # type: ignore


class TestBuildParser:
    """Tests for BuildParser abstract class."""

    def test_build_parser_abstract(self) -> None:
        """Test BuildParser is abstract."""

        class ConcreteParser(BuildParser):
            def parse_build_info(self, xml_element) -> dict:
                return {"build": "info"}

            def parse_skills(self, xml_element) -> list:
                return []

            def parse_items(self, xml_element) -> list:
                return []

            def parse_trees(self, xml_element) -> list:
                return []

        parser = ConcreteParser()
        assert parser.parse_build_info(None) == {"build": "info"}
        assert parser.parse_skills(None) == []
        assert parser.parse_items(None) == []
        assert parser.parse_trees(None) == []

    def test_build_parser_abstract_raises(self) -> None:
        """Test BuildParser raises error if not implemented."""
        with pytest.raises(TypeError):
            BuildParser()  # type: ignore

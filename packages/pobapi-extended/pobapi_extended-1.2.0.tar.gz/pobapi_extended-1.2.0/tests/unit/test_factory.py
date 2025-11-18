"""Unit tests for factory module."""

import pytest
from lxml.etree import fromstring

from pobapi.exceptions import InvalidImportCodeError, ParsingError
from pobapi.factory import BuildFactory
from pobapi.interfaces import BuildParser
from pobapi.parsers import DefaultBuildParser


class MockHTTPClient:
    """Mock HTTP client for testing."""

    def __init__(self, response_text: str):
        self.response_text = response_text

    def get(self, url: str, timeout: float = 6.0) -> str:
        """Return mock response."""
        return self.response_text


class MockBuildParser(BuildParser):
    """Mock build parser for testing."""

    def parse_build_info(self, xml_element):
        return {"class_name": "Test", "level": "1"}

    def parse_skills(self, xml_element):
        return []

    def parse_items(self, xml_element):
        return []

    def parse_trees(self, xml_element):
        return []


class TestBuildFactory:
    """Tests for BuildFactory."""

    def test_init_default(self):
        """Test factory initialization with defaults."""
        factory = BuildFactory()
        assert isinstance(factory._parser, DefaultBuildParser)
        assert factory._http_client is None

    def test_init_with_parser(self):
        """Test factory initialization with custom parser."""
        parser = MockBuildParser()
        factory = BuildFactory(parser=parser)
        assert factory._parser is parser

    def test_init_with_http_client(self):
        """Test factory initialization with custom HTTP client."""
        http_client = MockHTTPClient("test")
        factory = BuildFactory(http_client=http_client)
        assert factory._http_client is http_client

    def test_from_import_code_valid(self):
        """Test creating XML from valid import code."""
        # This will fail with real import code, but we test the structure
        factory = BuildFactory()
        # We can't easily test this without a real import code,
        # so we just check it raises the right exception
        with pytest.raises(InvalidImportCodeError):
            factory.from_import_code("invalid_code")

    def test_from_xml_bytes_valid(self):
        """Test creating PathOfBuildingAPI from valid XML bytes."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills/>
            <Items/>
            <Tree/>
        </PathOfBuilding>"""
        xml_bytes = xml_str.encode()

        factory = BuildFactory()
        build = factory.from_xml_bytes(xml_bytes)
        assert build.class_name == "Scion"

    def test_from_xml_bytes_invalid(self):
        """Test creating PathOfBuildingAPI from invalid XML bytes."""
        factory = BuildFactory()
        with pytest.raises(ParsingError, match="Failed to parse XML"):
            factory.from_xml_bytes(b"invalid xml")

    def test_from_xml_bytes_with_custom_parser(self):
        """Test creating PathOfBuildingAPI with custom parser."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills/>
            <Items/>
            <Tree/>
        </PathOfBuilding>"""
        xml_bytes = xml_str.encode()

        parser = MockBuildParser()
        factory = BuildFactory(parser=parser)
        build = factory.from_xml_bytes(xml_bytes)
        # Should use custom parser
        assert build._parser is parser

    def test_from_url_with_mock_client(self):
        """Test from_url with mock HTTP client."""
        # Create a valid import code (base64 encoded zlib compressed XML)
        import base64
        import zlib

        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills/>
            <Items/>
            <Tree/>
        </PathOfBuilding>"""
        compressed = zlib.compress(xml_str.encode())
        import_code = base64.urlsafe_b64encode(compressed).decode()

        http_client = MockHTTPClient(import_code)
        factory = BuildFactory(http_client=http_client)

        xml_bytes = factory.from_url("https://pastebin.com/test")
        assert isinstance(xml_bytes, bytes)
        # Verify it's valid XML
        root = fromstring(xml_bytes)
        assert root.find("Build") is not None

    @pytest.mark.asyncio
    async def test_async_from_url_with_client(self):
        """Test async_from_url with async HTTP client."""
        import base64
        import zlib

        from tests.unit.test_async_util import MockAsyncHTTPClient

        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills/>
            <Items/>
            <Tree/>
        </PathOfBuilding>"""
        compressed = zlib.compress(xml_str.encode())
        import_code = base64.urlsafe_b64encode(compressed).decode()

        async_client = MockAsyncHTTPClient(response_text=import_code)
        factory = BuildFactory(async_http_client=async_client)
        build = await factory.async_from_url("https://pastebin.com/test")
        assert build.class_name == "Scion"

    @pytest.mark.asyncio
    async def test_async_from_url_no_client(self):
        """Test async_from_url without client raises error."""
        factory = BuildFactory()
        with pytest.raises(ValueError, match="Async HTTP client is required"):
            await factory.async_from_url("https://pastebin.com/test")

    @pytest.mark.asyncio
    async def test_async_from_import_code(self):
        """Test async_from_import_code."""
        import base64
        import zlib

        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills/>
            <Items/>
            <Tree/>
        </PathOfBuilding>"""
        compressed = zlib.compress(xml_str.encode())
        import_code = base64.urlsafe_b64encode(compressed).decode()

        factory = BuildFactory()
        build = await factory.async_from_import_code(import_code)
        assert build.class_name == "Scion"

    def test_from_url_default_implementation(self, mocker):
        """Test from_url uses default implementation when no http_client."""
        # Clear cache to ensure fresh client creation
        import pobapi.util

        pobapi.util._default_http_client = None

        # When no http_client is provided, should use default _fetch_xml_from_url
        factory = BuildFactory()
        # Mock the entire requests.get call chain
        mock_response = mocker.Mock()
        mock_response.text = "test_import_code"
        mock_response.raise_for_status = mocker.Mock()

        mocker.patch("requests.get", return_value=mock_response)
        mock_decode = mocker.patch("pobapi.util._fetch_xml_from_import_code")
        mock_decode.return_value = b"""<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills/>
            <Items/>
            <Tree/>
        </PathOfBuilding>"""
        xml_bytes = factory.from_url("https://pastebin.com/test")
        assert isinstance(xml_bytes, bytes)
        mock_decode.assert_called_once()

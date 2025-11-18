"""Factory pattern for creating Path of Building API instances."""

from lxml.etree import fromstring

from pobapi.async_util import (
    _fetch_xml_from_import_code_async,
    _fetch_xml_from_url_async,
)
from pobapi.exceptions import ParsingError
from pobapi.interfaces import AsyncHTTPClient, BuildParser, HTTPClient
from pobapi.parsers import DefaultBuildParser
from pobapi.util import _fetch_xml_from_import_code, _fetch_xml_from_url

__all__ = ["BuildFactory"]


class BuildFactory:
    """Factory for creating Path of Building build instances."""

    def __init__(
        self,
        parser: BuildParser | None = None,
        http_client: HTTPClient | None = None,
        async_http_client: AsyncHTTPClient | None = None,
    ):
        """Initialize factory with optional parser and HTTP clients.

        :param parser: Build parser implementation. Defaults to DefaultBuildParser.
        :param http_client: Synchronous HTTP client implementation.
            Defaults to requests.
        :param async_http_client: Asynchronous HTTP client implementation.
        """
        self._parser = parser or DefaultBuildParser()
        self._http_client = http_client
        self._async_http_client = async_http_client

    def from_url(self, url: str, timeout: float = 6.0) -> bytes:
        """Create build XML from URL.

        :param url: pastebin.com URL.
        :param timeout: Request timeout.
        :return: XML bytes.
        :raises: NetworkError, InvalidURLError
        """
        # Use injected HTTP client if available, otherwise use default
        return _fetch_xml_from_url(url, timeout, http_client=self._http_client)

    def from_import_code(self, import_code: str) -> bytes:
        """Create build XML from import code.

        :param import_code: Path of Building import code.
        :return: XML bytes.
        :raises: InvalidImportCodeError
        """
        return _fetch_xml_from_import_code(import_code)  # type: ignore[no-any-return]

    def from_xml_bytes(self, xml_bytes: bytes):
        """Create PathOfBuildingAPI instance from XML bytes.

        :param xml_bytes: XML content as bytes.
        :return: PathOfBuildingAPI instance.
        :raises: ParsingError
        """
        try:
            xml_root = fromstring(xml_bytes)
        except Exception as e:
            raise ParsingError("Failed to parse XML") from e

        # Import here to avoid circular dependency
        from pobapi.api import PathOfBuildingAPI

        return PathOfBuildingAPI(xml_root, parser=self._parser)

    async def async_from_url(self, url: str, timeout: float = 6.0):
        """Create build XML from URL asynchronously.

        :param url: pastebin.com URL.
        :param timeout: Request timeout.
        :return: PathOfBuildingAPI instance.
        :raises: NetworkError, InvalidURLError, ValueError
        """
        if self._async_http_client is None:
            raise ValueError(
                "Async HTTP client is required. "
                "Set async_http_client in factory initialization."
            )

        xml_bytes = await _fetch_xml_from_url_async(
            url, self._async_http_client, timeout
        )
        return self.from_xml_bytes(xml_bytes)

    async def async_from_import_code(self, import_code: str):
        """Create build XML from import code asynchronously.

        :param import_code: Path of Building import code.
        :return: PathOfBuildingAPI instance.
        :raises: InvalidImportCodeError
        """
        xml_bytes = await _fetch_xml_from_import_code_async(import_code)
        return self.from_xml_bytes(xml_bytes)

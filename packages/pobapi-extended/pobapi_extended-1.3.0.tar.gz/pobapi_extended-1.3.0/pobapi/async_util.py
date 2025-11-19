"""Async utilities for pobapi."""

import base64
import logging
import zlib

from pobapi.exceptions import (
    InvalidImportCodeError,
    InvalidURLError,
    NetworkError,
)
from pobapi.interfaces import AsyncHTTPClient

logger = logging.getLogger(__name__)


async def _fetch_xml_from_url_async(
    url: str, http_client: AsyncHTTPClient | None = None, timeout: float = 6.0
) -> bytes:
    """
    Retrieve and decode a Path Of Building import code from a Pastebin URL.

    Validates that `url` is a pastebin.com URL and requires a provided
    async HTTP client to perform the request.

    Parameters:
        url (str): Pastebin URL containing the import code.
        timeout (float): Request timeout in seconds (default 6.0).

    Returns:
        bytes: Decompressed XML build document.

    Raises:
        InvalidURLError: If `url` is not a pastebin.com URL.
        ValueError: If no async HTTP client is provided.
        InvalidImportCodeError: If the fetched import code cannot be
            decoded or decompressed.
        NetworkError: For other failures while performing the HTTP request.
    """
    if not url.startswith("https://pastebin.com/"):
        raise InvalidURLError(f"{url} is not a valid pastebin.com URL.")

    if http_client is None:
        raise ValueError("Async HTTP client is required for async operations")

    try:
        response_text = await http_client.get(url, timeout=timeout)
        return await _fetch_xml_from_import_code_async(response_text)
    except Exception as e:
        if isinstance(e, InvalidURLError | InvalidImportCodeError):
            raise
        logger.exception("Network error in async request")
        raise NetworkError(f"Async request failed: {str(e)}") from e


async def _fetch_xml_from_import_code_async(import_code: str) -> bytes:
    """
    Decode a Path Of Building import code and return the decompressed XML document.

    Parameters:
        import_code (str): URL-safe base64-encoded string containing
            zlib-compressed Path Of Building XML.

    Returns:
        bytes: Decompressed XML build document.

    Raises:
        InvalidImportCodeError: If `import_code` is not a non-empty
            string, or if decoding or decompression fails.
    """
    if not import_code or not isinstance(import_code, str):
        raise InvalidImportCodeError("Import code must be a non-empty string")

    try:
        # These operations are CPU-bound but fast, so we can run them
        # in the event loop without blocking significantly
        base64_decode = base64.urlsafe_b64decode(import_code)
        decompressed_xml = zlib.decompress(base64_decode)
    except (TypeError, ValueError) as e:
        logger.exception("Error while decoding.")
        raise InvalidImportCodeError("Failed to decode import code") from e
    except zlib.error as e:
        logger.exception("Error while decompressing.")
        raise InvalidImportCodeError("Failed to decompress import code") from e

    return decompressed_xml

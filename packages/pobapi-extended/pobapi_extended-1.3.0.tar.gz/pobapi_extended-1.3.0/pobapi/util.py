import base64
import decimal
import logging
import re
import struct
import zlib
from collections.abc import Iterator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pobapi.interfaces import HTTPClient

from pobapi.cache import cached
from pobapi.constants import TREE_OFFSET
from pobapi.exceptions import (
    InvalidImportCodeError,
    InvalidURLError,
    NetworkError,
)

logger = logging.getLogger(__name__)

# Default HTTP client implementation using requests
_default_http_client: "HTTPClient | None" = None


def _get_default_http_client() -> "HTTPClient":
    """Get or create default HTTP client implementation.

    :return: Default HTTP client using requests library.
    """
    global _default_http_client
    if _default_http_client is None:
        try:
            import requests

            class RequestsHTTPClient:
                """Default HTTP client implementation using requests library."""

                def get(self, url: str, timeout: float = 6.0) -> str:
                    """Fetch content from URL using requests.

                    :param url: URL to fetch from.
                    :param timeout: Request timeout in seconds.
                    :return: Response text content.
                    :raises: NetworkError for various request failures.
                    """
                    try:
                        response = requests.get(url, timeout=timeout)
                        response.raise_for_status()
                        text: str = response.text
                        return text
                    except requests.Timeout as e:
                        logger.exception(
                            f"Connection timed out, try again or raise "
                            f"the timeout ({timeout}s)."
                        )
                        raise NetworkError(
                            f"Connection timed out after {timeout}s"
                        ) from e
                    except requests.ConnectionError as e:
                        logger.exception(
                            "There was a network problem "
                            "(DNS failure, refused connection, etc)."
                        )
                        raise NetworkError("Network connection failed") from e
                    except requests.HTTPError as e:
                        logger.exception(
                            "HTTP request returned unsuccessful status code."
                        )
                        status_code = (
                            e.response.status_code if e.response else "unknown"
                        )
                        raise NetworkError(f"HTTP error: {status_code}") from e
                    except requests.TooManyRedirects as e:
                        logger.exception(
                            "Request exceeds the maximum number of redirects."
                        )
                        raise NetworkError("Too many redirects") from e
                    except requests.RequestException as e:
                        logger.exception(
                            "Some other unspecified fatal error; cannot continue."
                        )
                        raise NetworkError("Request failed") from e

            _default_http_client = RequestsHTTPClient()
        except ImportError:
            raise ImportError(
                "requests library is required. Install it with: pip install requests"
            )
    return _default_http_client


def _fetch_xml_from_url(
    url: str, timeout: float = 6.0, http_client: "HTTPClient | None" = None
) -> bytes:
    """Get a Path Of Building import code shared with pastebin.com.

    :param url: pastebin.com URL.
    :param timeout: Request timeout in seconds.
    :param http_client: Optional HTTP client implementation. Uses default if None.
    :raises: :class:`~pobapi.exceptions.InvalidURLError`,
        :class:`~pobapi.exceptions.NetworkError`
    :return: Decompressed XML build document."""
    if not url.startswith("https://pastebin.com/"):
        raise InvalidURLError(f"{url} is not a valid pastebin.com URL.")

    raw = url.replace("https://pastebin.com/", "https://pastebin.com/raw/")
    client = http_client or _get_default_http_client()
    response_text: str = client.get(raw, timeout=timeout)
    xml_bytes: bytes = _fetch_xml_from_import_code(response_text)
    return xml_bytes


@cached(ttl=3600)  # Cache for 1 hour
def _fetch_xml_from_import_code(import_code: str) -> bytes:
    """Decodes and unzips a Path Of Building import code.

    :raises: :class:`~pobapi.exceptions.InvalidImportCodeError`

    :return: Decompressed XML build document."""
    if not import_code or not isinstance(import_code, str):
        raise InvalidImportCodeError("Import code must be a non-empty string")

    try:
        base64_decode = base64.urlsafe_b64decode(import_code)
        decompressed_xml = zlib.decompress(base64_decode)
    except (TypeError, ValueError) as e:
        logger.exception("Error while decoding.")
        raise InvalidImportCodeError("Failed to decode import code") from e
    except zlib.error as e:
        logger.exception("Error while decompressing.")
        raise InvalidImportCodeError("Failed to decompress import code") from e

    return decompressed_xml


@cached(ttl=86400)  # Cache for 24 hours (skill trees rarely change)
def _skill_tree_nodes(url: str) -> list[int]:
    """Get a list of passive tree node IDs.

    :param url: Skill tree URL.
    :return: Passive tree node IDs.
    :raises: ValueError if URL format is invalid."""
    *_, url_part = url.rpartition("/")
    try:
        bin_tree = base64.urlsafe_b64decode(url_part)
    except Exception as e:
        raise ValueError(f"Invalid skill tree URL format: {url}") from e

    if len(bin_tree) < TREE_OFFSET:
        raise ValueError(f"Skill tree data too short: {url}")

    return list(
        struct.unpack_from(
            "!" + "H" * ((len(bin_tree) - TREE_OFFSET) // 2),
            bin_tree,
            offset=TREE_OFFSET,
        )
    )


def _get_stat(text: list[str], stat: str) -> str | bool:
    """Get the value of an item affix.
    If an affix is found without a value, returns True instead.

    :param text: List of item text lines.
    :param stat: Stat name to search for.
    :return: Item affix value or True if found without value."""
    for line in text:
        if line.startswith(stat):
            *_, result = line.partition(stat)
            return result.strip() if result.strip() else True
    return ""


def _get_pos(text: list[str], stat: str) -> int | None:
    """Get the text line index of an item affix.

    :param text: List of item text lines.
    :param stat: Stat name to search for.
    :return: Item affix line index or None if not found."""
    for index, line in enumerate(text):
        if line.startswith(stat):
            return index
    return None


def _item_text(text: list[str]) -> Iterator[str]:
    """Get all affixes on an item.

    :return: Generator for an item's affixes."""
    for index, line in enumerate(text):
        if line.startswith("Implicits: "):
            try:
                yield from text[index + 1 :]
            except (KeyError, IndexError):
                return


def _get_text(
    text: list[str], variant: str, alt_variant: str, mod_ranges: list[float]
) -> str:
    def _parse_text(text_, variant_, alt_variant_, mod_ranges_):
        """Get the correct variant and item affix values
            for items made in Path Of Building.

        :return: Multiline string of correct item variants and item affix values."""
        counter = 0
        # We have to advance this every time we get a line with ranges to replace.
        for line in _item_text(text_):
            # We want to skip all mods of alternative item versions.
            if line.startswith("{variant:"):
                item_variants = (
                    line.partition("{variant:")[-1].partition("}")[0].split(",")
                )
                # "alt_variant_" is only used for the second aura mod on Watcher's Eye
                if variant_ not in item_variants and alt_variant_ not in item_variants:
                    continue
            # Check for "{range:" used in range tags to filter unsupported mods.
            if "{range:" in line:
                # "Adds (A-B) to (C-D) to something" mods need to be replaced twice.
                while "(" in line:
                    value = mod_ranges_[counter]
                    line = _calculate_mod_text(line, value)
                counter += 1
            # Omit "{variant: *}" and "{range: *}" tags.
            *_, mod = line.rpartition("}")
            yield mod

    return "\n".join(_parse_text(text, variant, alt_variant, mod_ranges))


def _calculate_mod_text(line: str, value: float) -> str:
    """Calculate an item affix's correct value from range and offset.

    :return: Corrected item affix value."""
    start, stop = line.partition("(")[-1].partition(")")[0].split("-")
    width = float(stop) - float(start) + 1
    # Python's round() function uses banker's rounding from 3.0 onwards
    # We have to emulate Path of Exile's "towards 0" rounding.
    # https://en.wikipedia.org/w/index.php?title=IEEE_754#Rounding_rules
    offset = decimal.Decimal(width * value).to_integral(decimal.ROUND_HALF_DOWN)
    result = float(start) + float(offset)
    replace_string = f"({start}-{stop})"
    result_string = f"{result if result % 1 else int(result)}"
    return line.replace(replace_string, result_string)


def clean_pob_formatting(text: str) -> str:
    """Remove Path of Building color and formatting codes from text.

    Path of Building uses formatting codes like:
    - ^xRRGGBB for color codes (hex RGB)
    - ^# for reset codes (where # is a number)

    :param text: Text with PoB formatting codes.
    :return: Cleaned text without formatting codes.
    """
    # Remove color codes: ^x followed by 6 hex digits
    text = re.sub(r"\^x[0-9A-Fa-f]{6}", "", text)
    # Remove reset codes: ^ followed by one or more digits
    text = re.sub(r"\^\d+", "", text)
    return text

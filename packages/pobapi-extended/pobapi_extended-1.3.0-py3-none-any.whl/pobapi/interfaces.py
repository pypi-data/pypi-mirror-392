"""Interfaces and abstractions for pobapi."""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

__all__ = [
    "HTTPClient",
    "AsyncHTTPClient",
    "XMLParser",
    "BuildParser",
    "BuildData",
]


@runtime_checkable
class HTTPClient(Protocol):
    """Protocol for synchronous HTTP client implementations."""

    def get(self, url: str, timeout: float = 6.0) -> str:
        """Fetch content from URL.

        :param url: URL to fetch from.
        :param timeout: Request timeout in seconds.
        :return: Response text content.
        :raises: Network-related exceptions.
        """
        ...  # pragma: no cover


@runtime_checkable
class AsyncHTTPClient(Protocol):
    """Protocol for asynchronous HTTP client implementations."""

    async def get(self, url: str, timeout: float = 6.0) -> str:
        """Fetch content from URL asynchronously.

        :param url: URL to fetch from.
        :param timeout: Request timeout in seconds.
        :return: Response text content.
        :raises: Network-related exceptions.
        """
        ...  # pragma: no cover


class XMLParser(ABC):
    """Abstract base class for XML parsers."""

    @abstractmethod
    def parse(self, xml_bytes: bytes) -> dict:
        """Parse XML bytes into structured data.

        :param xml_bytes: XML content as bytes.
        :return: Parsed data as dictionary.
        :raises: ParsingError if parsing fails.
        """
        pass


class BuildParser(ABC):
    """Abstract base class for build data parsers."""

    @abstractmethod
    def parse_build_info(self, xml_element) -> dict:
        """Parse build information from XML element.

        :param xml_element: XML element containing build info.
        :return: Dictionary with build information.
        """
        pass

    @abstractmethod
    def parse_skills(self, xml_element) -> list:
        """Parse skills from XML element.

        :param xml_element: XML element containing skills.
        :return: List of skill data.
        """
        pass

    @abstractmethod
    def parse_items(self, xml_element) -> list:
        """Parse items from XML element.

        :param xml_element: XML element containing items.
        :return: List of item data.
        """
        pass

    @abstractmethod
    def parse_trees(self, xml_element) -> list:
        """Parse skill trees from XML element.

        :param xml_element: XML element containing trees.
        :return: List of tree data.
        """
        pass


@runtime_checkable
class BuildData(Protocol):
    """Protocol for build data objects.

    This protocol defines the interface that build data objects must implement
    to be used with the calculation engine and other build processing components.
    """

    @property
    def items(self) -> list:
        """Get list of items in the build."""
        ...  # pragma: no cover

    @property
    def trees(self) -> list:
        """Get list of skill trees in the build."""
        ...  # pragma: no cover

    @property
    def skill_groups(self) -> list:
        """Get list of skill groups in the build."""
        ...  # pragma: no cover

    @property
    def active_skill_tree(self):
        """Get the active skill tree."""
        ...  # pragma: no cover

    @property
    def active_skill_group(self):
        """Get the active skill group."""
        ...  # pragma: no cover

    @property
    def keystones(self):
        """Get keystones in the build."""
        ...  # pragma: no cover

    @property
    def config(self):
        """Get configuration settings."""
        ...  # pragma: no cover

    @property
    def party_members(self) -> list:
        """Get party members (optional)."""
        ...  # pragma: no cover

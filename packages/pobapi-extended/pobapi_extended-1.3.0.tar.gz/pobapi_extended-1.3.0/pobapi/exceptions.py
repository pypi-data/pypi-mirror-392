"""Custom exceptions for pobapi."""

__all__ = [
    "PobAPIError",
    "InvalidImportCodeError",
    "InvalidURLError",
    "NetworkError",
    "ParsingError",
    "ValidationError",
]


class PobAPIError(Exception):
    """Base exception for all pobapi errors."""

    pass


class InvalidImportCodeError(PobAPIError):
    """Raised when import code is invalid or cannot be decoded."""

    pass


class InvalidURLError(PobAPIError):
    """Raised when URL is invalid or not supported."""

    pass


class NetworkError(PobAPIError):
    """Raised when network request fails."""

    pass


class ParsingError(PobAPIError):
    """Raised when XML parsing fails."""

    pass


class ValidationError(PobAPIError):
    """Raised when input validation fails."""

    pass

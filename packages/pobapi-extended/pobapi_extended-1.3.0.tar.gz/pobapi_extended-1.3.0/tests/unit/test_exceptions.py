"""Unit tests for exceptions module."""

import pytest

from pobapi.exceptions import (
    InvalidImportCodeError,
    InvalidURLError,
    NetworkError,
    ParsingError,
    PobAPIError,
    ValidationError,
)


@pytest.mark.parametrize(
    "exception_class,base_class",
    [
        (PobAPIError, Exception),
        (InvalidImportCodeError, PobAPIError),
        (InvalidURLError, PobAPIError),
        (NetworkError, PobAPIError),
        (ParsingError, PobAPIError),
        (ValidationError, PobAPIError),
    ],
)
class TestExceptionInheritance:
    """Tests for exception inheritance."""

    def test_inheritance(self, exception_class, base_class):
        """Test that exception inherits from base class."""
        assert issubclass(exception_class, base_class)


@pytest.mark.parametrize(
    "exception_class,message",
    [
        (PobAPIError, "Test error"),
        (InvalidImportCodeError, "Invalid import code"),
        (InvalidURLError, "Invalid URL"),
        (NetworkError, "Network error"),
        (ParsingError, "Parsing error"),
        (ValidationError, "Validation error"),
    ],
)
class TestExceptionRaising:
    """Tests for exception raising."""

    def test_can_raise(self, exception_class, message):
        """Test that exception can be raised."""
        with pytest.raises(exception_class):
            raise exception_class(message)

    def test_message_preserved(self, exception_class, message):
        """Test that error message is preserved."""
        with pytest.raises(exception_class, match=message):
            raise exception_class(message)

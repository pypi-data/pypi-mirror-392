"""Validators for input data."""

from typing import Any

from pobapi.exceptions import InvalidImportCodeError, InvalidURLError, ValidationError

__all__ = ["InputValidator", "XMLValidator"]


class InputValidator:
    """Validator for user input."""

    @staticmethod
    def validate_url(url: str) -> None:
        """Validate URL format.

        :param url: URL to validate.
        :raises: InvalidURLError if URL is invalid.
        """
        if not isinstance(url, str):
            raise InvalidURLError("URL must be a string")
        if not url.strip():
            raise InvalidURLError("URL cannot be empty")
        if not url.startswith("https://pastebin.com/"):
            raise InvalidURLError("URL must be a pastebin.com link")

    @staticmethod
    def validate_import_code(import_code: str) -> None:
        """Validate import code format.

        :param import_code: Import code to validate.
        :raises: InvalidImportCodeError if import code is invalid.
        """
        if not isinstance(import_code, str):
            raise InvalidImportCodeError("Import code must be a string")
        if not import_code.strip():
            raise InvalidImportCodeError("Import code cannot be empty")

    @staticmethod
    def validate_xml_bytes(xml_bytes: bytes) -> None:
        """Validate XML bytes.

        :param xml_bytes: XML content to validate.
        :raises: ValidationError if XML is invalid.
        """
        if not isinstance(xml_bytes, bytes):
            raise ValidationError("XML must be bytes")
        if not xml_bytes:
            raise ValidationError("XML cannot be empty")


class XMLValidator:
    """Validator for XML structure."""

    @staticmethod
    def validate_build_structure(xml_root: Any) -> None:
        """Validate that XML has required build structure.

        :param xml_root: XML root element.
        :raises: ValidationError if structure is invalid.
        """
        if xml_root is None:
            raise ValidationError("XML root is None")

        required_elements = ["Build", "Skills", "Items", "Tree"]
        for element_name in required_elements:
            if xml_root.find(element_name) is None:
                raise ValidationError(
                    f"Required element '{element_name}' not found in XML"
                )

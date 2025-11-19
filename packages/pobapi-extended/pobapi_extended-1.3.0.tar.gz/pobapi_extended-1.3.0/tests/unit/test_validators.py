"""Unit tests for validators module."""

import pytest
from lxml.etree import fromstring

from pobapi.exceptions import ValidationError
from pobapi.validators import InputValidator, XMLValidator


class TestInputValidator:
    """Tests for InputValidator class."""

    @pytest.mark.parametrize(
        "url",
        [
            "https://pastebin.com/abc123",
            "https://pastebin.com/test",
        ],
    )
    def test_validate_url_valid(self, url):
        """Test validation of valid URL."""
        # Should not raise
        InputValidator.validate_url(url)

    @pytest.mark.parametrize(
        "url,expected_error",
        [
            (123, "URL must be a string"),  # type: ignore[list-item,arg-type,unused-ignore]
            ("", "URL cannot be empty"),
            ("https://example.com/test", "must be a pastebin.com link"),
        ],
    )
    def test_validate_url_invalid(self, url, expected_error):
        """Test validation fails for invalid URL."""
        from pobapi.exceptions import InvalidURLError

        with pytest.raises(InvalidURLError, match=expected_error):
            InputValidator.validate_url(url)  # type: ignore[arg-type,unused-ignore]

    @pytest.mark.parametrize(
        "code",
        [
            "eNqVkM1qwzAQhF8lz7kHXwIhB5NCaQq9+BAw1lq7YFm7WpNC3r1rJ...",
            "test_code",
        ],
    )
    def test_validate_import_code_valid(self, code):
        """Test validation of valid import code."""
        # Should not raise
        InputValidator.validate_import_code(code)

    @pytest.mark.parametrize(
        "code,expected_error",
        [
            (123, "Import code must be a string"),  # type: ignore[list-item,arg-type,unused-ignore]
            ("", "Import code cannot be empty"),
        ],
    )
    def test_validate_import_code_invalid(self, code, expected_error):
        """Test validation fails for invalid import code."""
        from pobapi.exceptions import InvalidImportCodeError

        with pytest.raises(InvalidImportCodeError, match=expected_error):
            InputValidator.validate_import_code(code)  # type: ignore[arg-type,unused-ignore]

    @pytest.mark.parametrize(
        "xml_bytes",
        [
            b'<?xml version="1.0"?><root><Build/></root>',
            b"<PathOfBuilding><Build/></PathOfBuilding>",
        ],
    )
    def test_validate_xml_bytes_valid(self, xml_bytes):
        """Test validation of valid XML bytes."""
        # Should not raise
        InputValidator.validate_xml_bytes(xml_bytes)

    @pytest.mark.parametrize(
        "xml_bytes,expected_error",
        [
            ("not bytes", "XML must be bytes"),  # type: ignore[list-item,arg-type,unused-ignore]
            (b"", "XML cannot be empty"),
        ],
    )
    def test_validate_xml_bytes_invalid(self, xml_bytes, expected_error):
        """Test validation fails for invalid XML bytes."""
        with pytest.raises(ValidationError, match=expected_error):
            InputValidator.validate_xml_bytes(xml_bytes)  # type: ignore[arg-type,unused-ignore]


class TestXMLValidator:
    """Tests for XMLValidator class."""

    def test_validate_build_structure_valid(self, minimal_xml):
        """Test validation of valid XML structure."""
        xml_root = fromstring(minimal_xml.encode())
        # Should not raise
        XMLValidator.validate_build_structure(xml_root)

    def test_validate_build_structure_none(self):
        """Test validation fails for None root."""
        with pytest.raises(ValidationError, match="XML root is None"):
            XMLValidator.validate_build_structure(None)

    @pytest.mark.parametrize(
        "missing_element,element_name",
        [
            ("Build", "Build"),
            ("Skills", "Skills"),
            ("Items", "Items"),
            ("Tree", "Tree"),
        ],
    )
    def test_validate_build_structure_missing_element(
        self, missing_element, element_name
    ):
        """Test validation fails when required element is missing."""

        # Create XML without the specified element
        if missing_element == "Build":
            xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Skills/>
            <Items/>
            <Tree/>
        </PathOfBuilding>"""
        elif missing_element == "Skills":
            xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Items/>
            <Tree/>
        </PathOfBuilding>"""
        elif missing_element == "Items":
            xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills/>
            <Tree/>
        </PathOfBuilding>"""
        else:  # Tree
            xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills/>
            <Items/>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())
        with pytest.raises(
            ValidationError, match=f"Required element '{element_name}' not found"
        ):
            XMLValidator.validate_build_structure(xml_root)

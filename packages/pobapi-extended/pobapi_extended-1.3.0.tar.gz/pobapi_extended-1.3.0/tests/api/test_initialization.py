"""Tests for PathOfBuildingAPI initialization."""

import pytest

from pobapi import api
from pobapi.exceptions import ValidationError


class TestInitialization:
    """Tests for PathOfBuildingAPI initialization."""

    def test_init_from_xml_bytes(self, sample_xml):
        """TC-API-008: Initialize from XML bytes."""
        xml_bytes = sample_xml.encode()

        build = api.PathOfBuildingAPI(xml_bytes)

        assert build is not None
        assert build.class_name == "Scion"
        assert build.level == 1

    def test_init_with_custom_parser(self, sample_xml):
        """TC-API-010: Initialize with custom parser."""
        from pobapi.interfaces import BuildParser

        class CustomParser(BuildParser):
            """Custom parser for testing."""

            def parse_build_info(self, xml):
                """Parse build info with custom logic."""
                # Use default parser but mark as custom
                from pobapi.parsers import DefaultBuildParser

                default_parser = DefaultBuildParser()
                info = default_parser.parse_build_info(xml)
                info["_custom_parser"] = True
                return info

            def parse_skills(self, xml):
                """Parse skills with custom logic."""
                from pobapi.parsers import DefaultBuildParser

                default_parser = DefaultBuildParser()
                return default_parser.parse_skills(xml)

            def parse_items(self, xml):
                """Parse items with custom logic."""
                from pobapi.parsers import DefaultBuildParser

                default_parser = DefaultBuildParser()
                return default_parser.parse_items(xml)

            def parse_trees(self, xml):
                """Parse trees with custom logic."""
                from pobapi.parsers import DefaultBuildParser

                default_parser = DefaultBuildParser()
                return default_parser.parse_trees(xml)

        xml_bytes = sample_xml.encode()
        custom_parser = CustomParser()

        build = api.PathOfBuildingAPI(xml_bytes, parser=custom_parser)

        assert build is not None
        assert build.class_name == "Scion"
        # Verify custom parser was used
        assert build._build_info_cache.get("_custom_parser") is True

    def test_init_with_invalid_xml_structure(self):
        """TC-API-013: Initialize with invalid XML structure."""
        # Valid XML but invalid PoB structure (missing required elements)
        invalid_xml = b"""<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion"/>
        </PathOfBuilding>"""

        with pytest.raises(ValidationError):
            api.PathOfBuildingAPI(invalid_xml)

"""Integration tests for new components working together."""

import pytest

pytestmark = pytest.mark.integration
from lxml.etree import fromstring  # noqa: E402

from pobapi.builders import ConfigBuilder, ItemSetBuilder, StatsBuilder  # noqa: E402
from pobapi.exceptions import ParsingError, ValidationError  # noqa: E402
from pobapi.factory import BuildFactory  # noqa: E402
from pobapi.parsers import (  # noqa: E402
    BuildInfoParser,
    DefaultBuildParser,
    ItemsParser,
    SkillsParser,
)
from pobapi.validators import InputValidator, XMLValidator  # noqa: E402


class TestValidatorParserIntegration:
    """Test integration between validators and parsers."""

    def test_validate_then_parse(self, sample_xml):
        """Test that validated XML can be parsed."""
        xml_bytes = sample_xml.encode()

        # Validate
        InputValidator.validate_xml_bytes(xml_bytes)
        xml_root = fromstring(xml_bytes)
        XMLValidator.validate_build_structure(xml_root)

        # Parse
        build_info = BuildInfoParser.parse(xml_root)
        assert build_info["class_name"] == "Scion"

    def test_invalid_xml_fails_validation(self):
        """Test that invalid XML fails validation."""
        with pytest.raises(ValidationError):
            InputValidator.validate_xml_bytes(b"")

    def test_incomplete_xml_fails_structure_validation(self):
        """Test that incomplete XML fails structure validation."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())

        with pytest.raises(ValidationError, match="Required element"):
            XMLValidator.validate_build_structure(xml_root)


class TestParserBuilderIntegration:
    """Test integration between parsers and builders."""

    def test_parser_to_builder_flow(self, sample_xml):
        """Test that parsed data can be used by builders."""
        xml_root = fromstring(sample_xml.encode())

        # Parse
        build_info = BuildInfoParser.parse(xml_root)
        skills = SkillsParser.parse_skill_groups(xml_root)
        items = ItemsParser.parse_items(xml_root)

        # Build
        stats = StatsBuilder.build(xml_root)
        level_str = build_info["level"]
        character_level = int(level_str) if level_str else 1
        config = ConfigBuilder.build(xml_root, character_level=character_level)
        item_sets = ItemSetBuilder.build_all(xml_root)

        # Verify
        assert stats.life == 163.0
        assert config.enemy_level == 84
        assert len(item_sets) == 1
        assert len(skills) == 1
        assert len(items) == 1


class TestFactoryIntegration:
    """Test integration of factory with other components."""

    def test_factory_with_parser(self, sample_xml):
        """Test factory using custom parser."""
        xml_bytes = sample_xml.encode()
        parser = DefaultBuildParser()
        factory = BuildFactory(parser=parser)

        build = factory.from_xml_bytes(xml_bytes)
        assert build.class_name == "Scion"
        assert build._parser is parser

    def test_factory_creates_valid_build(self, sample_xml):
        """Test that factory creates valid build instance."""
        xml_bytes = sample_xml.encode()
        factory = BuildFactory()

        build = factory.from_xml_bytes(xml_bytes)

        # Test that all components work
        assert build.class_name == "Scion"
        assert build.level == 1
        assert build.stats.life == 163.0
        assert build.config.enemy_level == 84
        assert len(build.skill_groups) == 1
        assert len(build.items) == 1


class TestFullWorkflow:
    """Test complete workflow from validation to build creation."""

    def test_complete_workflow(self, sample_xml):
        """Test complete workflow: validate -> parse -> build."""
        xml_bytes = sample_xml.encode()

        # Step 1: Validate
        InputValidator.validate_xml_bytes(xml_bytes)
        xml_root = fromstring(xml_bytes)
        XMLValidator.validate_build_structure(xml_root)

        # Step 2: Parse
        parser = DefaultBuildParser()
        build_info = parser.parse_build_info(xml_root)
        skills = parser.parse_skills(xml_root)
        items = parser.parse_items(xml_root)
        trees = parser.parse_trees(xml_root)

        # Step 3: Build
        stats = StatsBuilder.build(xml_root)
        level_str = build_info.get("level")
        character_level = int(level_str) if level_str else 1
        config = ConfigBuilder.build(xml_root, character_level=character_level)
        item_sets = ItemSetBuilder.build_all(xml_root)

        # Step 4: Verify all components
        assert build_info["class_name"] == "Scion"
        assert len(skills) == 1
        assert len(items) == 1
        assert len(trees) == 1
        assert stats.life == 163.0
        assert config.enemy_level == 84
        assert len(item_sets) == 1

    def test_factory_workflow(self, sample_xml):
        """Test factory handles complete workflow."""
        xml_bytes = sample_xml.encode()
        factory = BuildFactory()

        build = factory.from_xml_bytes(xml_bytes)

        # Verify all properties work
        assert build.class_name == "Scion"
        assert build.ascendancy_name == "Ascendant"
        assert build.level == 1
        assert build.bandit == "Alira"
        assert build.stats.life == 163.0
        assert build.config.enemy_level == 84
        assert len(build.skill_groups) == 1
        assert len(build.items) == 1
        assert len(build.trees) == 1


class TestErrorHandlingIntegration:
    """Test error handling across components."""

    def test_validation_error_propagates(self):
        """Test that validation errors are caught."""
        with pytest.raises(ValidationError):
            InputValidator.validate_xml_bytes(b"")

    def test_parsing_error_propagates(self):
        """Test that parsing errors are caught."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Skills/>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())

        with pytest.raises(ParsingError):
            BuildInfoParser.parse(xml_root)

    def test_factory_handles_errors(self):
        """Test that factory properly handles errors."""
        factory = BuildFactory()

        with pytest.raises(ParsingError):
            factory.from_xml_bytes(b"invalid xml")

"""Unit tests for parsers module."""

import pytest
from lxml.etree import fromstring

from pobapi.exceptions import ParsingError
from pobapi.parsers import (
    BuildInfoParser,
    DefaultBuildParser,
    ItemsParser,
    SkillsParser,
    TreesParser,
)


class TestBuildInfoParser:
    """Tests for BuildInfoParser."""

    def test_parse_valid(self, sample_xml_root):
        """Test parsing valid build info."""
        result = BuildInfoParser.parse(sample_xml_root)
        assert result["class_name"] == "Scion"
        assert result["ascendancy_name"] == "Ascendant"
        assert result["level"] == "1"
        assert result["bandit"] == "Alira"
        assert result["main_socket_group"] == "1"

    def test_parse_missing_build_element(self):
        """Test parsing fails when Build element is missing."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Skills/>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())
        with pytest.raises(ParsingError, match="Build element not found"):
            BuildInfoParser.parse(xml_root)

    def test_parse_optional_fields(self):
        """Test parsing with optional fields missing."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())
        result = BuildInfoParser.parse(xml_root)
        assert result["class_name"] == "Scion"
        assert result["ascendancy_name"] is None
        assert result["bandit"] is None


class TestSkillsParser:
    """Tests for SkillsParser."""

    def test_parse_skill_groups_valid(self, sample_xml_root):
        """Test parsing valid skill groups."""
        result = SkillsParser.parse_skill_groups(sample_xml_root)
        assert len(result) == 1
        assert result[0]["enabled"] is True
        assert result[0]["label"] == "Test label"
        assert result[0]["main_active_skill"] == 1
        assert len(result[0]["abilities"]) == 1

    def test_parse_skill_groups_multiple(self):
        """Test parsing multiple skill groups."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Skills>
                <Skill enabled="true" label="Group 1" mainActiveSkill="1">
                    <Ability name="Arc" enabled="true" level="20" gemId="1"/>
                </Skill>
                <Skill enabled="false" label="Group 2" mainActiveSkill="nil">
                    <Ability name="Fireball" enabled="true" level="20" gemId="2"/>
                </Skill>
            </Skills>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())
        result = SkillsParser.parse_skill_groups(xml_root)
        assert len(result) == 2
        assert result[0]["enabled"] is True
        assert result[1]["enabled"] is False
        assert result[1]["main_active_skill"] is None

    def test_parse_skill_groups_empty(self):
        """Test parsing when Skills element is missing (covers line 56)."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())
        result = SkillsParser.parse_skill_groups(xml_root)
        assert result == []  # Covers line 56 in parsers.py


class TestItemsParser:
    """Tests for ItemsParser."""

    def test_parse_items_valid(self, sample_xml_root):
        """Test parsing valid items."""
        result = ItemsParser.parse_items(sample_xml_root)
        assert len(result) == 1
        item = result[0]
        assert item["rarity"] == "Unique"
        assert item["name"] == "Inpulsa's Broken Heart"
        assert item["base"] == "Sadist Garb"

    def test_parse_items_default_rarity(self):
        """Test parsing items with no rarity specified (defaults to Normal)."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Items>
                <Item>
                    Test Item
                    Test Base
                </Item>
            </Items>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())
        items = ItemsParser.parse_items(xml_root)
        assert len(items) == 1
        assert items[0]["rarity"] == "Normal"

    def test_parse_items_empty(self):
        """Test parsing when Items element is missing."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())
        result = ItemsParser.parse_items(xml_root)
        assert result == []

    def test_parse_item_sets_valid(self, sample_xml_root):
        """Test parsing item sets."""
        # sample_xml_root already has ItemSet with Body Armour and Helmet
        result = ItemsParser.parse_item_sets(sample_xml_root)
        assert len(result) == 1
        assert result[0]["body_armour"] == 0  # itemId - 1
        assert result[0]["helmet"] == 1  # itemId - 1

    def test_parse_item_sets_empty(self):
        """Test parsing when Items element is missing."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())
        result = ItemsParser.parse_item_sets(xml_root)
        assert result == []


class TestTreesParser:
    """Tests for TreesParser."""

    def test_parse_trees_valid(self, sample_xml_root):
        """Test parsing valid trees."""
        result = TreesParser.parse_trees(sample_xml_root)
        assert len(result) == 1
        tree = result[0]
        assert "pathofexile.com/passive-skill-tree/" in tree["url"]
        assert isinstance(tree["nodes"], list)
        assert isinstance(tree["sockets"], dict)

    def test_parse_trees_empty(self):
        """Test parsing when Tree element is missing."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())
        result = TreesParser.parse_trees(xml_root)
        assert result == []

    def test_parse_trees_no_url(self):
        """Test parsing when URL element is missing."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Tree>
                <Spec/>
            </Tree>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())
        result = TreesParser.parse_trees(xml_root)
        assert result == []


class TestDefaultBuildParser:
    """Tests for DefaultBuildParser."""

    def test_parse_build_info(self, sample_xml_root):
        """Test parsing build info."""
        parser = DefaultBuildParser()
        result = parser.parse_build_info(sample_xml_root)
        assert result["class_name"] == "Scion"

    def test_parse_skills(self, sample_xml_root):
        """Test parsing skills."""
        parser = DefaultBuildParser()
        result = parser.parse_skills(sample_xml_root)
        assert len(result) == 1

    def test_parse_items(self, sample_xml_root):
        """Test parsing items."""
        parser = DefaultBuildParser()
        result = parser.parse_items(sample_xml_root)
        assert len(result) == 1

    def test_parse_trees(self, sample_xml_root):
        """Test parsing trees."""
        parser = DefaultBuildParser()
        result = parser.parse_trees(sample_xml_root)
        assert len(result) == 1

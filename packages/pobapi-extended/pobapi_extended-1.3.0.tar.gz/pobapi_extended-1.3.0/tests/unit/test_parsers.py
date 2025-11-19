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

    @pytest.mark.parametrize(
        (
            "enabled1",
            "enabled2",
            "main_active1",
            "main_active2",
            "expected_main1",
            "expected_main2",
        ),
        [
            ("true", "false", "1", "nil", 1, None),
            ("false", "true", "nil", "2", None, 2),
            ("true", "true", "1", "2", 1, 2),
            ("false", "false", "nil", "nil", None, None),
        ],
    )
    def test_parse_skill_groups_multiple(
        self,
        enabled1,
        enabled2,
        main_active1,
        main_active2,
        expected_main1,
        expected_main2,
    ):
        """Test parsing multiple skill groups (parametrized)."""
        xml_str = f"""<?xml version="1.0"?>
        <PathOfBuilding>
            <Skills>
                <Skill
                    enabled="{enabled1}"
                    label="Group 1"
                    mainActiveSkill="{main_active1}"
                >
                    <Ability name="Arc" enabled="true" level="20" gemId="1"/>
                </Skill>
                <Skill
                    enabled="{enabled2}"
                    label="Group 2"
                    mainActiveSkill="{main_active2}"
                >
                    <Ability name="Fireball" enabled="true" level="20" gemId="2"/>
                </Skill>
            </Skills>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())
        result = SkillsParser.parse_skill_groups(xml_root)
        assert len(result) == 2
        assert result[0]["enabled"] == (enabled1 == "true")
        assert result[1]["enabled"] == (enabled2 == "true")
        assert result[0]["main_active_skill"] == expected_main1
        assert result[1]["main_active_skill"] == expected_main2

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

    @pytest.mark.parametrize(
        ("rarity_text", "expected_rarity"),
        [
            ("Rarity: NORMAL", "Normal"),
            ("Rarity: MAGIC", "Magic"),
            ("Rarity: RARE", "Rare"),
            ("Rarity: UNIQUE", "Unique"),
            ("", "Normal"),  # Default when not specified
        ],
    )
    def test_parse_items_rarity(self, rarity_text, expected_rarity):
        """Test parsing items with different rarity values (parametrized)."""
        if rarity_text:
            item_text = f"""{rarity_text}
Test Item
Test Base"""
        else:
            item_text = """Test Item
Test Base"""
        xml_str = f"""<?xml version="1.0"?>
        <PathOfBuilding>
            <Items>
                <Item>
                    {item_text}
                </Item>
            </Items>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())
        items = ItemsParser.parse_items(xml_root)
        assert len(items) == 1
        assert items[0]["rarity"] == expected_rarity

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

    @pytest.mark.parametrize(
        ("has_tree", "has_spec", "has_url", "expected_count"),
        [
            (False, False, False, 0),  # No Tree element
            (True, False, False, 0),  # Tree without Spec
            (True, True, False, 0),  # Tree with Spec but no URL
            (True, True, True, 1),  # Complete tree: Tree -> Spec -> URL
        ],
    )
    def test_parse_trees_scenarios(
        self, mocker, has_tree, has_spec, has_url, expected_count
    ):
        """Test parsing trees with different scenarios (parametrized)."""
        # Mock _skill_tree_nodes to avoid dependency on base64 URL parsing
        mocker.patch(
            "pobapi.parsers.xml._skill_tree_nodes", return_value=[12345, 12346]
        )

        tree_part = ""
        if has_tree:
            if has_spec:
                # Use a valid base64-encoded URL format for the test
                url_part = (
                    "<URL>https://pathofexile.com/passive-skill-tree/AAAA</URL>"
                    if has_url
                    else ""
                )
                spec_part = f'<Spec active="true">{url_part}</Spec>'
                tree_part = f"""<Tree>
                    {spec_part}
                </Tree>"""
            else:
                tree_part = """<Tree>
                </Tree>"""

        xml_str = f"""<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            {tree_part}
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())
        result = TreesParser.parse_trees(xml_root)
        assert len(result) == expected_count


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

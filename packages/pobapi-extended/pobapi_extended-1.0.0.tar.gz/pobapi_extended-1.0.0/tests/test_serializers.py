"""Tests for serializers module."""

import base64
import zlib

import pytest
from lxml.etree import fromstring

from pobapi import create_build, models
from pobapi.serializers import BuildXMLSerializer, ImportCodeGenerator
from pobapi.types import (
    Ascendancy,
    CharacterClass,
    ItemSlot,
    PassiveNodeID,
    SkillName,
)


class TestBuildXMLSerializer:
    """Tests for BuildXMLSerializer class."""

    def test_serialize_basic_build(self):
        """Test serializing a basic build."""
        builder = create_build()
        builder.set_class(CharacterClass.WITCH, Ascendancy.NECROMANCER)
        builder.set_level(90)

        xml_element = BuildXMLSerializer.serialize(builder)

        assert xml_element.tag == "PathOfBuilding"
        build_elem = xml_element.find("Build")
        assert build_elem is not None
        assert build_elem.get("className") == "Witch"
        assert build_elem.get("ascendClassName") == "Necromancer"
        assert build_elem.get("level") == "90"

    def test_serialize_with_bandit(self):
        """Test serializing with bandit choice."""
        builder = create_build()
        builder.set_bandit("Alira")

        xml_element = BuildXMLSerializer.serialize(builder)
        build_elem = xml_element.find("Build")
        assert build_elem.get("bandit") == "Alira"

    def test_serialize_with_skills(self):
        """Test serializing with skill groups."""
        builder = create_build()
        gem = models.Gem(
            name=SkillName.ARC.value,
            enabled=True,
            level=20,
            quality=20,
            support=False,
        )
        builder.add_skill(gem)

        xml_element = BuildXMLSerializer.serialize(builder)
        skills_elem = xml_element.find("Skills")
        assert skills_elem is not None
        skill_elem = skills_elem.find("Skill")
        assert skill_elem is not None
        ability_elem = skill_elem.find("Ability")
        assert ability_elem is not None
        assert ability_elem.get("nameSpec") == "Arc"
        assert ability_elem.get("level") == "20"
        assert ability_elem.get("quality") == "20"

    def test_serialize_with_active_skill(self):
        """Test serializing with active skill set - covers line 47."""
        builder = create_build()
        gem = models.Gem(
            name=SkillName.ARC.value,
            enabled=True,
            level=20,
            quality=20,
            support=False,
        )
        builder.add_skill(gem)
        # Set active skill on the skill group (covers line 47)
        # Get the skill group from builder
        skill_group = builder.skill_groups[0]
        skill_group.active = 0
        xml_element = BuildXMLSerializer.serialize(builder)
        skill_elem = xml_element.find(".//Skill")
        assert skill_elem is not None
        assert skill_elem.get("mainActiveSkill") == "0"

    def test_serialize_with_support_gem(self):
        """Test serializing with support gem."""
        builder = create_build()
        gem = models.Gem(
            name=SkillName.MINION_DAMAGE.value,
            enabled=True,
            level=20,
            quality=20,
            support=True,
        )
        builder.add_skill(gem)

        xml_element = BuildXMLSerializer.serialize(builder)
        ability_elem = xml_element.find(".//Ability")
        assert ability_elem.get("support") == "true"
        assert "Support" in ability_elem.get("skillId")

    def test_serialize_with_granted_ability(self):
        """Test serializing with GrantedAbility."""
        builder = create_build()
        ability = models.GrantedAbility(
            name="Test Ability",
            enabled=True,
            level=10,
            quality=None,
            support=False,
        )
        builder.add_skill(ability)

        xml_element = BuildXMLSerializer.serialize(builder)
        ability_elem = xml_element.find(".//Ability")
        assert ability_elem.get("granted") == "true"
        assert ability_elem.get("name") == "Test Ability"

    def test_serialize_with_granted_ability_quality(self):
        """Test serializing with GrantedAbility with quality - covers line 71."""
        builder = create_build()
        ability = models.GrantedAbility(
            name="Test Ability",
            enabled=True,
            level=10,
            quality=15,  # Set quality to trigger line 71
            support=False,
        )
        builder.add_skill(ability)

        xml_element = BuildXMLSerializer.serialize(builder)
        ability_elem = xml_element.find(".//Ability")
        assert ability_elem.get("granted") == "true"
        assert ability_elem.get("quality") == "15"  # Covers line 71

    def test_serialize_with_items(self):
        """Test serializing with items."""
        builder = create_build()
        item = models.Item(
            rarity="Rare",
            name="Test Item",
            base="Test Base",
            uid="",
            shaper=False,
            elder=False,
            crafted=False,
            quality=None,
            sockets=None,
            level_req=1,
            item_level=80,
            implicit=None,
            text="Test item text",
        )
        builder.add_item(item)

        xml_element = BuildXMLSerializer.serialize(builder)
        items_elem = xml_element.find("Items")
        assert items_elem is not None
        assert items_elem.get("activeItemSet") == "1"
        item_elem = items_elem.find("Item")
        assert item_elem is not None
        assert item_elem.text == "Test item text"

    def test_serialize_with_item_sets(self):
        """Test serializing with item sets."""
        builder = create_build()
        item = models.Item(
            rarity="Rare",
            name="Test Belt",
            base="Leather Belt",
            uid="",
            shaper=False,
            elder=False,
            crafted=False,
            quality=None,
            sockets=None,
            level_req=1,
            item_level=80,
            implicit=None,
            text="Test belt",
        )
        item_index = builder.add_item(item)
        builder.create_item_set()
        builder.equip_item(item_index, ItemSlot.BELT)

        xml_element = BuildXMLSerializer.serialize(builder)
        item_set_elem = xml_element.find(".//ItemSet")
        assert item_set_elem is not None
        slot_elem = item_set_elem.find("Slot")
        assert slot_elem is not None
        assert slot_elem.get("name") == "Belt"
        assert slot_elem.get("itemId") == "1"  # 0-based + 1

    def test_serialize_with_tree(self):
        """Test serializing with passive tree."""
        builder = create_build()
        builder.create_tree()
        builder.allocate_node(PassiveNodeID.ELEMENTAL_EQUILIBRIUM)

        xml_element = BuildXMLSerializer.serialize(builder)
        tree_elem = xml_element.find("Tree")
        assert tree_elem is not None
        spec_elem = tree_elem.find("Spec")
        assert spec_elem is not None
        url_elem = spec_elem.find("URL")
        assert url_elem is not None
        nodes_elem = spec_elem.find("Nodes")
        assert nodes_elem is not None
        node_elem = nodes_elem.find("Node")
        assert node_elem is not None
        assert node_elem.get("id") == str(PassiveNodeID.ELEMENTAL_EQUILIBRIUM)

    def test_serialize_with_tree_sockets(self):
        """Test serializing with tree sockets."""
        builder = create_build()
        builder.create_tree()
        item = models.Item(
            rarity="Rare",
            name="Test Jewel",
            base="Crimson Jewel",
            uid="",
            shaper=False,
            elder=False,
            crafted=False,
            quality=None,
            sockets=None,
            level_req=1,
            item_level=80,
            implicit=None,
            text="Test jewel",
        )
        item_index = builder.add_item(item)
        builder.socket_jewel(12345, item_index)

        xml_element = BuildXMLSerializer.serialize(builder)
        socket_elem = xml_element.find(".//Socket")
        assert socket_elem is not None
        assert socket_elem.get("nodeId") == "12345"
        assert socket_elem.get("itemId") == "1"  # 0-based + 1

    def test_serialize_with_notes(self):
        """Test serializing with notes."""
        builder = create_build()
        builder.set_notes("Test notes")

        xml_element = BuildXMLSerializer.serialize(builder)
        notes_elem = xml_element.find("Notes")
        assert notes_elem is not None
        assert notes_elem.text == "Test notes"

    def test_serialize_without_notes(self):
        """Test serializing without notes."""
        builder = create_build()
        xml_element = BuildXMLSerializer.serialize(builder)
        notes_elem = xml_element.find("Notes")
        assert notes_elem is None

    def test_serialize_with_config(self):
        """Test serializing with config - covers line 119."""
        from pobapi import config

        builder = create_build()
        # Set config to trigger line 119
        builder.config = config.Config()
        xml_element = BuildXMLSerializer.serialize(builder)
        config_elem = xml_element.find("Config")
        assert config_elem is not None  # Covers line 119

    def test_serialize_with_main_socket_group(self):
        """Test serializing with main socket group."""
        builder = create_build()
        builder.add_skill_group()
        xml_element = BuildXMLSerializer.serialize(builder)
        build_elem = xml_element.find("Build")
        assert build_elem.get("mainSocketGroup") == "1"

    def test_serialize_from_api_with_main_socket_group(self, build):
        """Test serialize_from_api with main_socket_group - covers line 179."""
        # Set main_socket_group property
        build.main_socket_group = 2  # type: ignore[assignment]
        xml_element = BuildXMLSerializer.serialize_from_api(build)
        build_elem = xml_element.find("Build")
        assert build_elem.get("mainSocketGroup") == "2"  # Covers line 179

    def test_serialize_from_api(self, build):
        """Test serialize_from_api with existing build."""
        xml_element = BuildXMLSerializer.serialize_from_api(build)
        assert xml_element.tag == "PathOfBuilding"
        build_elem = xml_element.find("Build")
        assert build_elem is not None
        assert build_elem.get("className") == build.class_name

    def test_serialize_from_api_with_skills(self, build):
        """Test serialize_from_api preserves skills."""
        xml_element = BuildXMLSerializer.serialize_from_api(build)
        skills_elem = xml_element.find("Skills")
        assert skills_elem is not None

    def test_serialize_from_api_with_items(self, build):
        """Test serialize_from_api preserves items."""
        xml_element = BuildXMLSerializer.serialize_from_api(build)
        items_elem = xml_element.find("Items")
        assert items_elem is not None
        assert items_elem.get("activeItemSet") == "1"

    def test_serialize_from_api_with_granted_ability_quality(self, build):
        """Test serialize_from_api with GrantedAbility with quality.

        Covers line 212."""
        from pobapi import models

        # Add GrantedAbility with quality to build
        ability = models.GrantedAbility(
            name="Test Ability",
            enabled=True,
            level=10,
            quality=20,  # Set quality to trigger line 212
            support=False,
        )
        build.add_skill(ability)
        xml_element = BuildXMLSerializer.serialize_from_api(build)
        ability_elem = xml_element.find(".//Ability[@granted='true']")
        assert ability_elem is not None
        assert ability_elem.get("quality") == "20"  # Covers line 212

    def test_serialize_from_api_with_pending_items(self, build):
        """Test serialize_from_api with pending items - covers lines 227-229."""
        from pobapi import models

        # Add pending item with text
        item = models.Item(
            rarity="Rare",
            name="Test Belt",
            base="Leather Belt",
            uid="",
            shaper=False,
            elder=False,
            crafted=False,
            quality=None,
            sockets=None,
            level_req=1,
            item_level=80,
            implicit=None,
            text=(
                "Rarity: RARE\nTest Belt\nLeather Belt\n--------\n"
                "LevelReq: 1\nItem Level: 80\n+25 to maximum Life\n"
            ),
        )
        # Initialize _pending_items if needed
        if not hasattr(build, "_pending_items"):
            build._pending_items = []
        build._pending_items.append(item)
        xml_element = BuildXMLSerializer.serialize_from_api(build)
        items_elem = xml_element.find("Items")
        # Should include pending item (covers lines 227-229)
        item_elems = items_elem.findall("Item")
        assert len(item_elems) > 0
        # Check that pending item text is included
        assert any("Test Belt" in (elem.text or "") for elem in item_elems)


class TestImportCodeGenerator:
    """Tests for ImportCodeGenerator class."""

    def test_generate_from_xml(self):
        """Test generating import code from XML element."""
        root = fromstring(
            b'<?xml version="1.0"?><PathOfBuilding>'
            b'<Build className="Scion" level="1"/></PathOfBuilding>'
        )
        import_code = ImportCodeGenerator.generate(root)

        # Should be base64 encoded
        assert isinstance(import_code, str)
        assert len(import_code) > 0

        # Should be decodable
        try:
            decoded = base64.urlsafe_b64decode(import_code)
            decompressed = zlib.decompress(decoded)
            assert b"PathOfBuilding" in decompressed
        except Exception:
            pytest.fail("Import code should be valid base64 and zlib compressed")

    def test_generate_from_builder(self):
        """Test generating import code from BuildBuilder."""
        builder = create_build()
        builder.set_class(CharacterClass.WITCH)
        builder.set_level(90)

        import_code = ImportCodeGenerator.generate_from_builder(builder)

        assert isinstance(import_code, str)
        assert len(import_code) > 0

    def test_generate_from_api(self, build):
        """Test generating import code from PathOfBuildingAPI."""
        import_code = ImportCodeGenerator.generate_from_api(build)

        assert isinstance(import_code, str)
        assert len(import_code) > 0

    def test_import_code_roundtrip(self):
        """Test that import code can be decoded back to XML."""
        builder = create_build()
        builder.set_class(CharacterClass.WITCH, Ascendancy.NECROMANCER)
        builder.set_level(90)

        import_code = ImportCodeGenerator.generate_from_builder(builder)

        # Decode and verify
        decoded = base64.urlsafe_b64decode(import_code)
        decompressed = zlib.decompress(decoded)
        xml_root = fromstring(decompressed)

        assert xml_root.tag == "PathOfBuilding"
        build_elem = xml_root.find("Build")
        assert build_elem.get("className") == "Witch"
        assert build_elem.get("ascendClassName") == "Necromancer"

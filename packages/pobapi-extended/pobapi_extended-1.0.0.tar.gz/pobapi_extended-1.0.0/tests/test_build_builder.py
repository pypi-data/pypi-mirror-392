"""Tests for BuildBuilder class."""

import pytest

from pobapi import create_build, models
from pobapi.exceptions import ValidationError
from pobapi.types import (
    Ascendancy,
    BanditChoice,
    CharacterClass,
    ItemSlot,
    PassiveNodeID,
    SkillName,
)


class TestBuildBuilder:
    """Tests for BuildBuilder class."""

    def test_init(self):
        """Test BuildBuilder initialization."""
        builder = create_build()
        assert builder.class_name == "Scion"
        assert builder.ascendancy_name is None
        assert builder.level == 1
        assert builder.bandit is None
        assert builder.items == []
        assert builder.item_sets == []
        assert builder.trees == []
        assert builder.skill_groups == []
        assert builder.notes == ""

    def test_set_class_with_enums(self):
        """Test set_class with Enum types."""
        builder = create_build()
        builder.set_class(CharacterClass.WITCH, Ascendancy.NECROMANCER)
        assert builder.class_name == "Witch"
        assert builder.ascendancy_name == "Necromancer"

    def test_set_class_with_strings(self):
        """Test set_class with string types."""
        builder = create_build()
        builder.set_class("Ranger", "Deadeye")
        assert builder.class_name == "Ranger"
        assert builder.ascendancy_name == "Deadeye"

    def test_set_class_without_ascendancy(self):
        """Test set_class without ascendancy."""
        builder = create_build()
        builder.set_class(CharacterClass.WITCH)
        assert builder.class_name == "Witch"
        assert builder.ascendancy_name is None

    def test_set_level_valid(self):
        """Test set_level with valid level."""
        builder = create_build()
        builder.set_level(90)
        assert builder.level == 90

    def test_set_level_invalid_low(self):
        """Test set_level with level too low."""
        builder = create_build()
        with pytest.raises(ValidationError, match="Level must be between 1 and 100"):
            builder.set_level(0)

    def test_set_level_invalid_high(self):
        """Test set_level with level too high."""
        builder = create_build()
        with pytest.raises(ValidationError, match="Level must be between 1 and 100"):
            builder.set_level(101)

    def test_set_bandit_with_enum(self):
        """Test set_bandit with Enum type."""
        builder = create_build()
        builder.set_bandit(BanditChoice.ALIRA)
        assert builder.bandit == "Alira"

    def test_set_bandit_with_string(self):
        """Test set_bandit with string type."""
        builder = create_build()
        builder.set_bandit("Oak")
        assert builder.bandit == "Oak"

    def test_set_bandit_none(self):
        """Test set_bandit with None."""
        builder = create_build()
        builder.set_bandit(None)
        assert builder.bandit is None

    def test_set_bandit_invalid(self):
        """Test set_bandit with invalid choice."""
        builder = create_build()
        with pytest.raises(ValidationError, match="Invalid bandit choice"):
            builder.set_bandit("Invalid")

    def test_add_item(self):
        """Test add_item."""
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
        index = builder.add_item(item)
        assert index == 0
        assert len(builder.items) == 1
        assert builder.items[0] == item

    def test_create_item_set(self):
        """Test create_item_set."""
        builder = create_build()
        item_set = builder.create_item_set()
        assert len(builder.item_sets) == 1
        assert isinstance(item_set, models.Set)
        assert item_set.weapon1 is None
        assert item_set.helmet is None

    def test_equip_item(self):
        """Test equip_item."""
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
        assert builder.item_sets[0].belt == item_index

    def test_equip_item_with_string_slot(self):
        """Test equip_item with string slot."""
        builder = create_build()
        item = models.Item(
            rarity="Rare",
            name="Test Helmet",
            base="Iron Helmet",
            uid="",
            shaper=False,
            elder=False,
            crafted=False,
            quality=None,
            sockets=None,
            level_req=1,
            item_level=80,
            implicit=None,
            text="Test helmet",
        )
        item_index = builder.add_item(item)
        builder.create_item_set()
        builder.equip_item(item_index, "Helmet")
        assert builder.item_sets[0].helmet == item_index

    def test_equip_item_invalid_index(self):
        """Test equip_item with invalid item index."""
        builder = create_build()
        builder.create_item_set()
        with pytest.raises(ValidationError, match="Invalid item index"):
            builder.equip_item(0, ItemSlot.BELT)

    def test_equip_item_invalid_slot(self):
        """Test equip_item with invalid slot."""
        builder = create_build()
        item = models.Item(
            rarity="Rare",
            name="Test",
            base="Test",
            uid="",
            shaper=False,
            elder=False,
            crafted=False,
            quality=None,
            sockets=None,
            level_req=1,
            item_level=80,
            implicit=None,
            text="Test",
        )
        item_index = builder.add_item(item)
        builder.create_item_set()
        with pytest.raises(ValidationError, match="Invalid slot name"):
            builder.equip_item(item_index, "InvalidSlot")

    def test_create_tree(self):
        """Test create_tree."""
        builder = create_build()
        tree = builder.create_tree()
        assert len(builder.trees) == 1
        assert isinstance(tree, models.Tree)
        assert tree.url == ""
        assert tree.nodes == []
        assert tree.sockets == {}

    def test_create_tree_with_url(self):
        """Test create_tree with URL."""
        builder = create_build()
        tree = builder.create_tree(url="https://example.com/tree")
        assert tree.url == "https://example.com/tree"

    def test_allocate_node(self):
        """Test allocate_node."""
        builder = create_build()
        builder.create_tree()
        builder.allocate_node(PassiveNodeID.ELEMENTAL_EQUILIBRIUM)
        assert PassiveNodeID.ELEMENTAL_EQUILIBRIUM in builder.trees[0].nodes

    def test_allocate_node_with_int(self):
        """Test allocate_node with integer."""
        builder = create_build()
        builder.create_tree()
        builder.allocate_node(39085)
        assert 39085 in builder.trees[0].nodes

    def test_allocate_node_auto_create_tree(self):
        """Test allocate_node auto-creates tree if none exists."""
        builder = create_build()
        builder.allocate_node(PassiveNodeID.ELEMENTAL_EQUILIBRIUM)
        assert len(builder.trees) == 1
        assert PassiveNodeID.ELEMENTAL_EQUILIBRIUM in builder.trees[0].nodes

    def test_allocate_node_duplicate(self):
        """Test allocate_node doesn't add duplicate nodes."""
        builder = create_build()
        builder.create_tree()
        builder.allocate_node(PassiveNodeID.ELEMENTAL_EQUILIBRIUM)
        builder.allocate_node(PassiveNodeID.ELEMENTAL_EQUILIBRIUM)
        assert builder.trees[0].nodes.count(PassiveNodeID.ELEMENTAL_EQUILIBRIUM) == 1

    def test_allocate_node_invalid_tree_index(self):
        """Test allocate_node with invalid tree index."""
        builder = create_build()
        builder.create_tree()
        with pytest.raises(ValidationError, match="Invalid tree index"):
            builder.allocate_node(PassiveNodeID.ELEMENTAL_EQUILIBRIUM, tree_index=1)

    def test_remove_node(self):
        """Test remove_node."""
        builder = create_build()
        builder.create_tree()
        builder.allocate_node(PassiveNodeID.ELEMENTAL_EQUILIBRIUM)
        builder.remove_node(PassiveNodeID.ELEMENTAL_EQUILIBRIUM)
        assert PassiveNodeID.ELEMENTAL_EQUILIBRIUM not in builder.trees[0].nodes

    def test_remove_node_not_present(self):
        """Test remove_node when node is not present."""
        builder = create_build()
        builder.create_tree()
        # Should not raise
        builder.remove_node(PassiveNodeID.ELEMENTAL_EQUILIBRIUM)

    def test_socket_jewel(self):
        """Test socket_jewel."""
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
        assert builder.trees[0].sockets[12345] == item_index

    def test_socket_jewel_invalid_item_index(self):
        """Test socket_jewel with invalid item index."""
        builder = create_build()
        builder.create_tree()
        with pytest.raises(ValidationError, match="Invalid item index"):
            builder.socket_jewel(12345, 0)

    def test_add_skill_group(self):
        """Test add_skill_group."""
        builder = create_build()
        skill_group = builder.add_skill_group(label="Test Group")
        assert len(builder.skill_groups) == 1
        assert skill_group.label == "Test Group"
        assert skill_group.enabled is True
        assert skill_group.active is None

    def test_add_skill_group_with_options(self):
        """Test add_skill_group with options."""
        builder = create_build()
        skill_group = builder.add_skill_group(label="Test", enabled=False, active=1)
        assert skill_group.enabled is False
        assert skill_group.active == 1

    def test_add_skill(self):
        """Test add_skill."""
        builder = create_build()
        gem = models.Gem(
            name=SkillName.ARC.value,
            enabled=True,
            level=20,
            quality=20,
            support=False,
        )
        builder.add_skill(gem)
        assert len(builder.skill_groups) == 1
        assert len(builder.skill_groups[0].abilities) == 1
        assert builder.skill_groups[0].abilities[0] == gem

    def test_add_skill_to_existing_group(self):
        """Test add_skill to existing group."""
        builder = create_build()
        builder.add_skill_group(label="Main")
        gem1 = models.Gem(
            name=SkillName.ARC.value,
            enabled=True,
            level=20,
            quality=20,
            support=False,
        )
        gem2 = models.Gem(
            name=SkillName.MINION_DAMAGE.value,
            enabled=True,
            level=20,
            quality=20,
            support=True,
        )
        builder.add_skill(gem1, group_label="Main")
        builder.add_skill(gem2, group_label="Main")
        assert len(builder.skill_groups) == 1
        assert len(builder.skill_groups[0].abilities) == 2

    def test_set_config(self):
        """Test set_config."""
        builder = create_build()
        config = {"enemy_level": 84}
        builder.set_config(config)
        assert builder.config == config

    def test_set_notes(self):
        """Test set_notes."""
        builder = create_build()
        notes = "Test notes"
        builder.set_notes(notes)
        assert builder.notes == notes

    def test_set_active_spec(self):
        """Test set_active_spec."""
        builder = create_build()
        builder.set_active_spec(2)
        assert builder.active_spec == 2

    def test_set_active_spec_invalid(self):
        """Test set_active_spec with invalid index."""
        builder = create_build()
        with pytest.raises(ValidationError, match="Spec index must be >= 1"):
            builder.set_active_spec(0)

    def test_build(self):
        """Test build method creates PathOfBuildingAPI."""
        builder = create_build()
        builder.set_class(CharacterClass.WITCH, Ascendancy.NECROMANCER)
        builder.set_level(90)
        build = builder.build()
        from pobapi.api import PathOfBuildingAPI

        assert isinstance(build, PathOfBuildingAPI)
        assert build.class_name == "Witch"
        assert build.ascendancy_name == "Necromancer"
        assert build.level == 90

    def test_build_with_items_and_skills(self):
        """Test build with items and skills."""
        builder = create_build()
        builder.set_class(CharacterClass.WITCH)

        # Add item
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
        item_index = builder.add_item(item)
        builder.create_item_set()
        builder.equip_item(item_index, ItemSlot.BELT)

        # Add skill
        gem = models.Gem(
            name=SkillName.ARC.value,
            enabled=True,
            level=20,
            quality=20,
            support=False,
        )
        builder.add_skill(gem)

        # Add tree
        builder.create_tree()
        builder.allocate_node(PassiveNodeID.ELEMENTAL_EQUILIBRIUM)

        build = builder.build()
        assert len(build.items) == 1
        assert len(build.skill_groups) == 1
        assert len(build.trees) == 1

    def test_equip_item_creates_item_set_if_needed(self):
        """Test equip_item creates item set if index is out of range.

        Covers lines 166-167.
        """
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
            text=(
                "Rarity: RARE\nTest Belt\nLeather Belt\n--------\n"
                "LevelReq: 1\nItem Level: 80\n+25 to maximum Life\n"
            ),
        )
        item_index = builder.add_item(item)
        # Try to equip to item_set_index=2 when no sets exist (covers lines 166-167)
        builder.equip_item(item_index, ItemSlot.BELT, item_set_index=2)
        # Should create 3 item sets (indices 0, 1, 2)
        assert len(builder.item_sets) == 3
        assert builder.item_sets[2].belt == item_index

    def test_socket_jewel_creates_tree_if_none(self):
        """Test socket_jewel creates tree if none exists - covers lines 262-265."""
        builder = create_build()
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
            text=(
                "Rarity: RARE\nTest Jewel\nCrimson Jewel\n--------\n"
                "LevelReq: 1\nItem Level: 80\n+10 to Strength\n"
            ),
        )
        item_index = builder.add_item(item)
        # Socket jewel when no trees exist (covers lines 262-265)
        builder.socket_jewel(12345, item_index)
        # Should create a tree automatically
        assert len(builder.trees) == 1
        assert builder.trees[0].sockets[12345] == item_index

    def test_socket_jewel_invalid_tree_index(self):
        """Test socket_jewel with invalid tree index when trees exist.

        Covers lines 262-265.
        """
        builder = create_build()
        builder.create_tree()  # Create one tree
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
            text=(
                "Rarity: RARE\nTest Jewel\nCrimson Jewel\n--------\n"
                "LevelReq: 1\nItem Level: 80\n+10 to Strength\n"
            ),
        )
        item_index = builder.add_item(item)
        # Try to socket in tree_index=1 when only tree 0 exists (covers lines 262-265)
        with pytest.raises(ValidationError, match="Invalid tree index"):
            builder.socket_jewel(12345, item_index, tree_index=1)

"""Tests for build modification methods."""

import pytest

from pobapi import models
from pobapi.exceptions import ValidationError
from pobapi.types import ItemSlot


class TestEquipItem:
    """Tests for equip_item method."""

    def test_equip_item_with_itemslot_enum(self, simple_build, create_test_item):
        """TC-API-058: Equip item with ItemSlot enum."""
        item = create_test_item(name="Test Helmet", base="Iron Helmet")

        item_index = simple_build.equip_item(item, ItemSlot.HELMET)

        assert item_index is not None
        assert isinstance(item_index, int)
        # Verify item is in active_item_set
        assert simple_build.active_item_set.helmet is not None

    def test_equip_item_with_invalid_item_set_index(
        self, simple_build, create_test_item
    ):
        """TC-API-060: Equip item with invalid item_set_index."""
        item = create_test_item(name="Test Helmet", base="Iron Helmet")

        # Try to equip to non-existent item set
        with pytest.raises(ValidationError):
            simple_build.equip_item(item, ItemSlot.HELMET, item_set_index=999)


class TestUnequipItem:
    """Tests for unequip_item method."""

    def test_unequip_item_from_slot(self, simple_build, create_test_item):
        """TC-API-063: Unequip item from slot."""
        item = create_test_item(name="Test Helmet", base="Iron Helmet")

        # First equip the item
        simple_build.equip_item(item, ItemSlot.HELMET)
        assert simple_build.active_item_set.helmet is not None

        # Then unequip it
        simple_build.unequip_item(ItemSlot.HELMET)

        # Verify item is removed
        assert simple_build.active_item_set.helmet is None

    def test_unequip_item_from_empty_slot(self, simple_build):
        """TC-API-064: Unequip item from empty slot."""
        # Try to unequip from already empty slot
        # Should not raise exception or handle gracefully
        try:
            simple_build.unequip_item(ItemSlot.HELMET)
        except (ValidationError, ValueError):
            # If it raises, that's also acceptable behavior
            pass


class TestAddSkill:
    """Tests for add_skill method."""

    def test_add_skill_to_new_group(self, simple_build):
        """TC-API-067: Add skill to new group."""
        gem = models.Gem(
            name="Fireball", level=20, quality=0, enabled=True, support=False
        )

        # Add skill to new group
        simple_build.add_skill(gem, "New Group")

        # Verify new group was created
        groups = list(simple_build.skill_groups)
        group_labels = [g.label for g in groups]
        assert "New Group" in group_labels

        # Verify skill is in the new group
        new_group = next((g for g in groups if g.label == "New Group"), None)
        assert new_group is not None
        assert len(new_group.abilities) > 0


class TestRemoveSkill:
    """Tests for remove_skill method."""

    def test_remove_skill_from_group(self, simple_build):
        """TC-API-068: Remove skill from group."""
        gem = models.Gem(
            name="Fireball", level=20, quality=0, enabled=True, support=False
        )

        # First add the skill
        simple_build.add_skill(gem, "Main")

        # Verify skill is present
        groups = list(simple_build.skill_groups)
        main_group = next((g for g in groups if g.label == "Main"), None)
        assert main_group is not None
        initial_count = len(main_group.abilities)

        # Remove the skill
        simple_build.remove_skill(gem, "Main")

        # Verify skill is removed
        groups_after = list(simple_build.skill_groups)
        main_group_after = next((g for g in groups_after if g.label == "Main"), None)
        assert main_group_after is not None
        assert len(main_group_after.abilities) < initial_count

    def test_remove_skill_from_nonexistent_group(self, simple_build):
        """TC-API-069: Remove skill from nonexistent group."""
        gem = models.Gem(
            name="Fireball", level=20, quality=0, enabled=True, support=False
        )

        # Try to remove from non-existent group
        # Should handle gracefully (either ignore or raise ValidationError)
        try:
            simple_build.remove_skill(gem, "Nonexistent Group")
        except ValidationError:
            # If it raises, that's acceptable behavior
            pass

    def test_remove_skill_not_in_group(self, simple_build):
        """TC-API-070: Remove skill not in group."""
        gem = models.Gem(
            name="Fireball", level=20, quality=0, enabled=True, support=False
        )
        other_gem = models.Gem(
            name="Icebolt", level=20, quality=0, enabled=True, support=False
        )

        # Add one gem
        simple_build.add_skill(gem, "Main")

        # Try to remove different gem
        # Should handle gracefully
        try:
            simple_build.remove_skill(other_gem, "Main")
        except ValidationError:
            # If it raises, that's acceptable behavior
            pass


class TestSetLevel:
    """Tests for set_level method."""

    def test_set_level(self, simple_build):
        """TC-API-071: Set level."""
        simple_build.set_level(90)

        assert simple_build.level == 90

    def test_set_level_with_boundary_values(self, simple_build):
        """TC-API-072: Set level with boundary values."""
        # Test minimum level
        simple_build.set_level(1)
        assert simple_build.level == 1

        # Test maximum level
        simple_build.set_level(100)
        assert simple_build.level == 100

    def test_set_level_with_invalid_value(self, simple_build):
        """TC-API-073: Set level with invalid value."""
        # Test level < 1
        with pytest.raises(ValidationError):
            simple_build.set_level(0)

        # Test level > 100
        with pytest.raises(ValidationError):
            simple_build.set_level(101)


class TestSetBandit:
    """Tests for set_bandit method."""

    def test_set_bandit(self, simple_build):
        """TC-API-074: Set bandit."""
        simple_build.set_bandit("Alira")

        assert simple_build.bandit == "Alira"

    def test_set_bandit_to_none(self, simple_build):
        """TC-API-075: Set bandit to None."""
        # First set a bandit
        simple_build.set_bandit("Alira")
        assert simple_build.bandit == "Alira"

        # Then unset it
        simple_build.set_bandit(None)

        assert simple_build.bandit is None

    def test_set_bandit_with_invalid_value(self, simple_build):
        """TC-API-076: Set bandit with invalid value."""
        with pytest.raises(ValidationError):
            simple_build.set_bandit("Invalid Bandit")

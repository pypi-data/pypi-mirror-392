"""Tests for types module."""

from pobapi.types import (
    Ascendancy,
    BanditChoice,
    CharacterClass,
    ItemSlot,
    PassiveNodeID,
    SkillName,
)


class TestCharacterClass:
    """Tests for CharacterClass enum."""

    def test_character_class_values(self) -> None:
        """Test CharacterClass enum values."""
        assert CharacterClass.WITCH.value == "Witch"
        assert CharacterClass.RANGER.value == "Ranger"
        assert CharacterClass.SCION.value == "Scion"


class TestAscendancy:
    """Tests for Ascendancy enum."""

    def test_ascendancy_values(self) -> None:
        """Test Ascendancy enum values."""
        assert Ascendancy.NECROMANCER.value == "Necromancer"
        assert Ascendancy.DEADEYE.value == "Deadeye"


class TestItemSlot:
    """Tests for ItemSlot enum."""

    def test_item_slot_values(self) -> None:
        """Test ItemSlot enum values."""
        assert ItemSlot.BODY_ARMOUR.value == "Body Armour"
        assert ItemSlot.HELMET.value == "Helmet"


class TestBanditChoice:
    """Tests for BanditChoice enum."""

    def test_bandit_choice_values(self) -> None:
        """Test BanditChoice enum values."""
        assert BanditChoice.ALIRA.value == "Alira"
        assert BanditChoice.OAK.value == "Oak"


class TestSkillName:
    """Tests for SkillName enum."""

    def test_skill_name_values(self) -> None:
        """Test SkillName enum values."""
        assert SkillName.ARC.value == "Arc"
        assert SkillName.FIREBALL.value == "Fireball"


class TestPassiveNodeID:
    """Tests for PassiveNodeID class."""

    def test_passive_node_id_constants(self) -> None:
        """Test PassiveNodeID constants."""
        assert PassiveNodeID.ELEMENTAL_EQUILIBRIUM == 39085
        assert PassiveNodeID.MINION_INSTABILITY == 55906
        assert PassiveNodeID.ZEALOTS_OATH == 10490

    def test_get_name_existing(self) -> None:
        """Test get_name method with existing node ID - covers lines 312-315."""
        # Test with existing node ID
        name = PassiveNodeID.get_name(39085)  # ELEMENTAL_EQUILIBRIUM
        assert name == "ELEMENTAL_EQUILIBRIUM"

        name = PassiveNodeID.get_name(55906)  # MINION_INSTABILITY
        assert name == "MINION_INSTABILITY"

    def test_get_name_not_found(self) -> None:
        """Test get_name method with non-existing node ID - covers lines 312-315."""
        # Test with non-existing node ID
        name = PassiveNodeID.get_name(999999)
        assert name is None

    def test_get_id_existing(self) -> None:
        """Test get_id method with existing name - covers line 324."""
        # Test with existing name (case-insensitive)
        node_id = PassiveNodeID.get_id("ELEMENTAL_EQUILIBRIUM")
        assert node_id == 39085

        node_id = PassiveNodeID.get_id("elemental_equilibrium")  # lowercase
        assert node_id == 39085

        node_id = PassiveNodeID.get_id("MINION_INSTABILITY")
        assert node_id == 55906

    def test_get_id_not_found(self) -> None:
        """Test get_id method with non-existing name - covers line 324."""
        # Test with non-existing name
        node_id = PassiveNodeID.get_id("NON_EXISTING_NODE")
        assert node_id is None

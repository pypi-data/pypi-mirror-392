"""Tests for crafting module."""

import pytest

from pobapi.calculator.modifiers import ModifierType
from pobapi.crafting import (
    CraftingModifier,
    CraftingResult,
    ItemCraftingAPI,
    ItemModifier,
    ModifierTier,
)


class TestItemModifier:
    """Tests for ItemModifier dataclass."""

    def test_init_defaults(self) -> None:
        """Test ItemModifier initialization with defaults."""
        mod = ItemModifier(
            name="of Life",
            stat="Life",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.FLAT,
            tier=ModifierTier.T1,
        )
        assert mod.name == "of Life"
        assert mod.stat == "Life"
        assert mod.min_value == 10.0
        assert mod.max_value == 20.0
        assert mod.tags == []

    def test_init_with_tags(self) -> None:
        """Test ItemModifier initialization with tags."""
        mod = ItemModifier(
            name="of Life",
            stat="Life",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.FLAT,
            tier=ModifierTier.T1,
            tags=["armour", "belt"],
        )
        assert mod.tags == ["armour", "belt"]


class TestCraftingModifier:
    """Tests for CraftingModifier dataclass."""

    def test_to_modifier(self) -> None:
        """Test converting CraftingModifier to Modifier."""
        item_mod = ItemModifier(
            name="of Life",
            stat="Life",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.FLAT,
            tier=ModifierTier.T1,
        )
        crafting_mod = CraftingModifier(modifier=item_mod, roll_value=15.0)
        modifier = crafting_mod.to_modifier(source="test")
        assert modifier.stat == "Life"
        assert modifier.value == 15.0
        assert modifier.mod_type == ModifierType.FLAT
        assert modifier.source == "test"


class TestCraftingResult:
    """Tests for CraftingResult dataclass."""

    def test_init_defaults(self) -> None:
        """Test CraftingResult initialization with defaults."""
        result = CraftingResult(success=True)
        assert result.success is True
        assert result.item_text == ""
        assert result.modifiers == []
        assert result.prefix_count == 0
        assert result.suffix_count == 0
        assert result.error == ""

    def test_init_with_values(self) -> None:
        """Test CraftingResult initialization with values."""
        from pobapi.calculator.modifiers import Modifier

        modifiers = [
            Modifier(
                stat="Life",
                value=100.0,
                mod_type=ModifierType.FLAT,
                source="crafted",
            )
        ]
        result = CraftingResult(
            success=True,
            item_text="Test Item",
            modifiers=modifiers,
            prefix_count=1,
            suffix_count=0,
        )
        assert result.success is True
        assert result.item_text == "Test Item"
        assert result.modifiers is not None
        assert len(result.modifiers) == 1
        assert result.prefix_count == 1
        assert result.suffix_count == 0


class TestItemCraftingAPI:
    """Tests for ItemCraftingAPI."""

    def test_get_modifiers_by_type_prefix(self) -> None:
        """Test getting modifiers by type (prefix)."""
        modifiers = ItemCraftingAPI.get_modifiers_by_type("prefix", item_level=100)
        assert isinstance(modifiers, list)

    def test_get_modifiers_by_type_suffix(self) -> None:
        """Test getting modifiers by type (suffix)."""
        modifiers = ItemCraftingAPI.get_modifiers_by_type("suffix", item_level=100)
        assert isinstance(modifiers, list)

    def test_get_modifiers_by_type_invalid(self) -> None:
        """Test getting modifiers with invalid type."""
        modifiers = ItemCraftingAPI.get_modifiers_by_type("invalid", item_level=100)
        assert modifiers == []

    def test_get_modifiers_by_type_with_item_level(self) -> None:
        """Test getting modifiers filtered by item level."""
        # Get modifiers for low level item
        low_level_mods = ItemCraftingAPI.get_modifiers_by_type("prefix", item_level=1)
        # Get modifiers for high level item
        high_level_mods = ItemCraftingAPI.get_modifiers_by_type(
            "prefix", item_level=100
        )
        # High level should have at least as many as low level
        assert len(high_level_mods) >= len(low_level_mods)

    def test_get_modifiers_by_type_with_tags(self) -> None:
        """Test getting modifiers filtered by tags."""
        modifiers = ItemCraftingAPI.get_modifiers_by_type(
            "prefix", item_level=100, tags=["armour"]
        )
        assert isinstance(modifiers, list)
        # If any modifiers found, they should have armour tag
        if modifiers:
            for mod in modifiers:
                assert mod.tags is not None
                assert any("armour" in tag.lower() for tag in mod.tags)

    def test_get_modifiers_by_stat(self) -> None:
        """Test getting modifiers by stat name."""
        modifiers = ItemCraftingAPI.get_modifiers_by_stat("Life", item_level=100)
        assert isinstance(modifiers, list)

    def test_get_modifiers_by_stat_with_tags(self) -> None:
        """Test getting modifiers by stat with tags."""
        modifiers = ItemCraftingAPI.get_modifiers_by_stat(
            "Life", item_level=100, tags=["armour"]
        )
        assert isinstance(modifiers, list)

    def test_get_available_prefixes(self) -> None:
        """Test getting available prefixes."""
        prefixes = ItemCraftingAPI.get_available_prefixes(item_level=100)
        assert isinstance(prefixes, list)

    def test_get_available_suffixes(self) -> None:
        """Test getting available suffixes."""
        suffixes = ItemCraftingAPI.get_available_suffixes(item_level=100)
        assert isinstance(suffixes, list)

    def test_craft_item_success(self) -> None:
        """Test successful item crafting."""
        # Get available modifiers
        prefixes_list = ItemCraftingAPI.get_modifiers_by_type("prefix", item_level=84)
        suffixes_list = ItemCraftingAPI.get_modifiers_by_type("suffix", item_level=84)

        if not prefixes_list or not suffixes_list:
            pytest.skip("No modifiers available in database")

        # Create crafting modifiers
        prefix_mod = CraftingModifier(
            modifier=prefixes_list[0], roll_value=prefixes_list[0].max_value
        )
        suffix_mod = CraftingModifier(
            modifier=suffixes_list[0], roll_value=suffixes_list[0].max_value
        )

        result = ItemCraftingAPI.craft_item(
            base_item_type="Leather Belt",
            item_level=84,
            prefixes=[prefix_mod],
            suffixes=[suffix_mod],
        )

        assert result.success is True
        assert result.prefix_count == 1
        assert result.suffix_count == 1
        assert result.item_text != ""
        assert result.modifiers is not None
        assert len(result.modifiers) == 2

    def test_craft_item_too_many_prefixes(self) -> None:
        """Test crafting with too many prefixes."""
        prefixes_list = ItemCraftingAPI.get_modifiers_by_type("prefix", item_level=84)
        if len(prefixes_list) < 4:
            pytest.skip("Not enough modifiers in database")

        crafting_mods = [
            CraftingModifier(modifier=mod, roll_value=mod.max_value)
            for mod in prefixes_list[:4]
        ]

        result = ItemCraftingAPI.craft_item(
            base_item_type="Leather Belt",
            item_level=84,
            prefixes=crafting_mods,
        )

        assert result.success is False
        assert "Maximum 3 prefixes" in result.error

    def test_craft_item_too_many_suffixes(self) -> None:
        """Test crafting with too many suffixes."""
        suffixes_list = ItemCraftingAPI.get_modifiers_by_type("suffix", item_level=84)
        if len(suffixes_list) < 4:
            pytest.skip("Not enough modifiers in database")

        crafting_mods = [
            CraftingModifier(modifier=mod, roll_value=mod.max_value)
            for mod in suffixes_list[:4]
        ]

        result = ItemCraftingAPI.craft_item(
            base_item_type="Leather Belt",
            item_level=84,
            suffixes=crafting_mods,
        )

        assert result.success is False
        assert "Maximum 3 suffixes" in result.error

    def test_craft_item_insufficient_item_level(self) -> None:
        """Test crafting with insufficient item level."""
        prefixes_list = ItemCraftingAPI.get_modifiers_by_type("prefix", item_level=100)
        if not prefixes_list:
            pytest.skip("No modifiers available in database")

        # Find a modifier that requires high item level
        high_level_mod = None
        for mod in prefixes_list:
            if mod.item_level_required > 50:
                high_level_mod = mod
                break

        if not high_level_mod:
            pytest.skip("No high level modifier found")

        crafting_mod = CraftingModifier(
            modifier=high_level_mod, roll_value=high_level_mod.max_value
        )

        result = ItemCraftingAPI.craft_item(
            base_item_type="Leather Belt",
            item_level=50,  # Lower than required
            prefixes=[crafting_mod],
        )

        assert result.success is False
        assert "requires item level" in result.error

    def test_craft_item_with_implicits(self) -> None:
        """Test crafting with implicit modifiers."""
        prefixes_list = ItemCraftingAPI.get_modifiers_by_type("prefix", item_level=84)
        if not prefixes_list:
            pytest.skip("No modifiers available in database")

        prefix_mod = CraftingModifier(
            modifier=prefixes_list[0], roll_value=prefixes_list[0].max_value
        )

        result = ItemCraftingAPI.craft_item(
            base_item_type="Leather Belt",
            item_level=84,
            prefixes=[prefix_mod],
            implicit_mods=["+20 to maximum Life"],
        )

        assert result.success is True
        assert "+20 to maximum Life" in result.item_text

    @pytest.mark.parametrize(
        ("mod_type", "stat", "expected_pattern"),
        [
            (ModifierType.FLAT, "Life", "+{value} to maximum Life"),
            (ModifierType.FLAT, "Mana", "+{value} to maximum Mana"),
            (ModifierType.FLAT, "EnergyShield", "+{value} to maximum Energy Shield"),
            (ModifierType.FLAT, "PhysicalDamage", "+{value} to Physical Damage"),
            (ModifierType.INCREASED, "Life", "{value}% increased maximum Life"),
            (ModifierType.MORE, "FireDamage", "{value}% more Fire Damage"),
            (ModifierType.REDUCED, "ManaCost", "{value}% reduced Manacost"),
            (ModifierType.LESS, "Damage", "{value}% less Damage"),
        ],
    )
    def test_generate_item_text_modifier_types(
        self, mod_type: ModifierType, stat: str, expected_pattern: str
    ) -> None:
        """Test generating item text with different modifier types."""
        item_mod = ItemModifier(
            name="Test Mod",
            stat=stat,
            min_value=10.0,
            max_value=20.0,
            mod_type=mod_type,
            tier=ModifierTier.T1,
            is_prefix=True,
        )
        crafting_mod = CraftingModifier(modifier=item_mod, roll_value=15.0)

        item_text = ItemCraftingAPI.generate_item_text(
            base_item_type="Test Item",
            prefixes=[crafting_mod] if mod_type != ModifierType.LESS else None,
            suffixes=[crafting_mod] if mod_type == ModifierType.LESS else None,
        )

        assert "Test Item" in item_text
        assert "Rarity: RARE" in item_text
        # Check that the modifier text is present (pattern matching)
        expected_text = expected_pattern.format(value=15)
        assert expected_text in item_text

    def test_generate_item_text_with_implicits(self) -> None:
        """Test generating item text with implicit modifiers."""
        item_text = ItemCraftingAPI.generate_item_text(
            base_item_type="Leather Belt",
            implicit_mods=["+20 to maximum Life", "+10 to Strength"],
        )

        assert "Leather Belt" in item_text
        assert "+20 to maximum Life" in item_text
        assert "+10 to Strength" in item_text

    def test_generate_item_text_empty(self) -> None:
        """Test generating item text with no modifiers."""
        item_text = ItemCraftingAPI.generate_item_text(base_item_type="Test Item")
        assert "Test Item" in item_text
        assert "Rarity: RARE" in item_text

    def test_calculate_modifier_value_perfect_roll(self) -> None:
        """Test calculating modifier value with perfect roll."""
        item_mod = ItemModifier(
            name="Test Mod",
            stat="Life",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.FLAT,
            tier=ModifierTier.T1,
        )

        value = ItemCraftingAPI.calculate_modifier_value(item_mod, roll_percent=100.0)
        assert value == 20.0

    def test_calculate_modifier_value_minimum_roll(self) -> None:
        """Test calculating modifier value with minimum roll."""
        item_mod = ItemModifier(
            name="Test Mod",
            stat="Life",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.FLAT,
            tier=ModifierTier.T1,
        )

        value = ItemCraftingAPI.calculate_modifier_value(item_mod, roll_percent=0.0)
        assert value == 10.0

    def test_calculate_modifier_value_mid_roll(self) -> None:
        """Test calculating modifier value with mid roll."""
        item_mod = ItemModifier(
            name="Test Mod",
            stat="Life",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.FLAT,
            tier=ModifierTier.T1,
        )

        value = ItemCraftingAPI.calculate_modifier_value(item_mod, roll_percent=50.0)
        assert value == 15.0

    def test_calculate_modifier_value_clamped(self) -> None:
        """Test calculating modifier value with clamped roll percent."""
        item_mod = ItemModifier(
            name="Test Mod",
            stat="Life",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.FLAT,
            tier=ModifierTier.T1,
        )

        # Test values outside 0-100 range
        value_negative = ItemCraftingAPI.calculate_modifier_value(
            item_mod, roll_percent=-10.0
        )
        assert value_negative == 10.0

        value_over_100 = ItemCraftingAPI.calculate_modifier_value(
            item_mod, roll_percent=150.0
        )
        assert value_over_100 == 20.0

    def test_craft_item_prefix_flat_non_life_mana_es(self) -> None:
        """Test crafting prefix with FLAT modifier for non-life/mana/es stat.

        Covers line 483."""
        # Create a FLAT modifier for a stat that's not Life/Mana/EnergyShield
        item_mod = ItemModifier(
            name="of Strength",
            stat="Strength",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.FLAT,
            tier=ModifierTier.T1,
            is_prefix=True,
        )
        crafting_mod = CraftingModifier(modifier=item_mod, roll_value=15.0)

        result = ItemCraftingAPI.craft_item(
            base_item_type="Leather Belt",
            item_level=84,
            prefixes=[crafting_mod],
        )

        assert result.success is True
        # Should use "+{value} to {display_stat}" format (covers line 483)
        assert "+15 to" in result.item_text

    def test_craft_item_prefix_increased(self) -> None:
        """Test crafting prefix with INCREASED modifier - covers line 485."""
        item_mod = ItemModifier(
            name="of Damage",
            stat="PhysicalDamage",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.INCREASED,
            tier=ModifierTier.T1,
            is_prefix=True,
        )
        crafting_mod = CraftingModifier(modifier=item_mod, roll_value=15.0)

        result = ItemCraftingAPI.craft_item(
            base_item_type="Leather Belt",
            item_level=84,
            prefixes=[crafting_mod],
        )

        assert result.success is True
        # Should use "{value}% increased {display_stat}" format (covers line 485)
        assert "15% increased" in result.item_text

    def test_craft_item_prefix_more(self) -> None:
        """Test crafting prefix with MORE modifier - covers line 487."""
        item_mod = ItemModifier(
            name="of Damage",
            stat="FireDamage",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.MORE,
            tier=ModifierTier.T1,
            is_prefix=True,
        )
        crafting_mod = CraftingModifier(modifier=item_mod, roll_value=15.0)

        result = ItemCraftingAPI.craft_item(
            base_item_type="Leather Belt",
            item_level=84,
            prefixes=[crafting_mod],
        )

        assert result.success is True
        # Should use "{value}% more {display_stat}" format (covers line 487)
        assert "15% more" in result.item_text

    def test_craft_item_prefix_reduced(self) -> None:
        """Test crafting prefix with REDUCED modifier - covers line 489."""
        item_mod = ItemModifier(
            name="of Cost",
            stat="ManaCost",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.REDUCED,
            tier=ModifierTier.T1,
            is_prefix=True,
        )
        crafting_mod = CraftingModifier(modifier=item_mod, roll_value=15.0)

        result = ItemCraftingAPI.craft_item(
            base_item_type="Leather Belt",
            item_level=84,
            prefixes=[crafting_mod],
        )

        assert result.success is True
        # Should use "{value}% reduced {display_stat}" format (covers line 489)
        assert "15% reduced" in result.item_text

    def test_craft_item_prefix_less(self) -> None:
        """Test crafting prefix with LESS modifier - covers line 491."""
        item_mod = ItemModifier(
            name="of Damage",
            stat="Damage",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.LESS,
            tier=ModifierTier.T1,
            is_prefix=True,
        )
        crafting_mod = CraftingModifier(modifier=item_mod, roll_value=15.0)

        result = ItemCraftingAPI.craft_item(
            base_item_type="Leather Belt",
            item_level=84,
            prefixes=[crafting_mod],
        )

        assert result.success is True
        # Should use "{value}% less {display_stat}" format (covers line 491)
        assert "15% less" in result.item_text

    def test_craft_item_suffix_flat(self) -> None:
        """Test crafting suffix with FLAT modifier - covers line 500."""
        item_mod = ItemModifier(
            name="of Strength",
            stat="Strength",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.FLAT,
            tier=ModifierTier.T1,
            is_suffix=True,
        )
        crafting_mod = CraftingModifier(modifier=item_mod, roll_value=15.0)

        result = ItemCraftingAPI.craft_item(
            base_item_type="Leather Belt",
            item_level=84,
            suffixes=[crafting_mod],
        )

        assert result.success is True
        # Should use "+{value} to {display_stat}" format (covers line 500)
        assert "+15 to" in result.item_text

    def test_craft_item_suffix_increased(self) -> None:
        """Test crafting suffix with INCREASED modifier - covers line 502."""
        item_mod = ItemModifier(
            name="of Damage",
            stat="PhysicalDamage",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.INCREASED,
            tier=ModifierTier.T1,
            is_suffix=True,
        )
        crafting_mod = CraftingModifier(modifier=item_mod, roll_value=15.0)

        result = ItemCraftingAPI.craft_item(
            base_item_type="Leather Belt",
            item_level=84,
            suffixes=[crafting_mod],
        )

        assert result.success is True
        # Should use "{value}% increased {display_stat}" format (covers line 502)
        assert "15% increased" in result.item_text

    def test_craft_item_suffix_more(self) -> None:
        """Test crafting suffix with MORE modifier - covers line 504."""
        item_mod = ItemModifier(
            name="of Damage",
            stat="FireDamage",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.MORE,
            tier=ModifierTier.T1,
            is_suffix=True,
        )
        crafting_mod = CraftingModifier(modifier=item_mod, roll_value=15.0)

        result = ItemCraftingAPI.craft_item(
            base_item_type="Leather Belt",
            item_level=84,
            suffixes=[crafting_mod],
        )

        assert result.success is True
        # Should use "{value}% more {display_stat}" format (covers line 504)
        assert "15% more" in result.item_text

    def test_craft_item_suffix_reduced(self) -> None:
        """Test crafting suffix with REDUCED modifier - covers line 506."""
        item_mod = ItemModifier(
            name="of Cost",
            stat="ManaCost",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.REDUCED,
            tier=ModifierTier.T1,
            is_suffix=True,
        )
        crafting_mod = CraftingModifier(modifier=item_mod, roll_value=15.0)

        result = ItemCraftingAPI.craft_item(
            base_item_type="Leather Belt",
            item_level=84,
            suffixes=[crafting_mod],
        )

        assert result.success is True
        # Should use "{value}% reduced {display_stat}" format (covers line 506)
        assert "15% reduced" in result.item_text

    def test_craft_item_suffix_less(self) -> None:
        """Test crafting suffix with LESS modifier - covers line 508."""
        item_mod = ItemModifier(
            name="of Damage",
            stat="Damage",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.LESS,
            tier=ModifierTier.T1,
            is_suffix=True,
        )
        crafting_mod = CraftingModifier(modifier=item_mod, roll_value=15.0)

        result = ItemCraftingAPI.craft_item(
            base_item_type="Leather Belt",
            item_level=84,
            suffixes=[crafting_mod],
        )

        assert result.success is True
        # Should use "{value}% less {display_stat}" format (covers line 508)
        assert "15% less" in result.item_text

    def test_generate_item_text_prefix_less(self) -> None:
        """Test generating item text with prefix LESS modifier.

        Covers lines 601-602."""
        item_mod = ItemModifier(
            name="of Damage",
            stat="Damage",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.LESS,
            tier=ModifierTier.T1,
            is_prefix=True,
        )
        crafting_mod = CraftingModifier(modifier=item_mod, roll_value=15.0)

        item_text = ItemCraftingAPI.generate_item_text(
            base_item_type="Test Item",
            prefixes=[crafting_mod],
        )

        # Should use "{value}% less {display_stat}" format (covers lines 601-602)
        assert "15% less" in item_text

    def test_generate_item_text_suffix_flat_life_mana_es(self) -> None:
        """Test generating item text with suffix FLAT modifier for Life/Mana/ES.

        Covers lines 615-617."""
        # Test Life
        item_mod_life = ItemModifier(
            name="of Life",
            stat="Life",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.FLAT,
            tier=ModifierTier.T1,
            is_suffix=True,
        )
        crafting_mod_life = CraftingModifier(modifier=item_mod_life, roll_value=15.0)

        item_text = ItemCraftingAPI.generate_item_text(
            base_item_type="Test Item",
            suffixes=[crafting_mod_life],
        )

        # Should use "+{value} to maximum {clean_stat}" format (covers lines 615-617)
        assert "+15 to maximum Life" in item_text

        # Test Mana
        item_mod_mana = ItemModifier(
            name="of Mana",
            stat="Mana",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.FLAT,
            tier=ModifierTier.T1,
            is_suffix=True,
        )
        crafting_mod_mana = CraftingModifier(modifier=item_mod_mana, roll_value=15.0)

        item_text = ItemCraftingAPI.generate_item_text(
            base_item_type="Test Item",
            suffixes=[crafting_mod_mana],
        )

        assert "+15 to maximum Mana" in item_text

        # Test EnergyShield
        item_mod_es = ItemModifier(
            name="of Energy Shield",
            stat="EnergyShield",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.FLAT,
            tier=ModifierTier.T1,
            is_suffix=True,
        )
        crafting_mod_es = CraftingModifier(modifier=item_mod_es, roll_value=15.0)

        item_text = ItemCraftingAPI.generate_item_text(
            base_item_type="Test Item",
            suffixes=[crafting_mod_es],
        )

        assert "+15 to maximum Energy Shield" in item_text

    def test_generate_item_text_suffix_flat_non_life_mana_es(self) -> None:
        """Test generating item text with suffix FLAT modifier for
        non-Life/Mana/ES stat.

        Covers line 619."""
        # Test with a stat that's not Life/Mana/EnergyShield
        item_mod = ItemModifier(
            name="of Strength",
            stat="Strength",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.FLAT,
            tier=ModifierTier.T1,
            is_suffix=True,
        )
        crafting_mod = CraftingModifier(modifier=item_mod, roll_value=15.0)

        item_text = ItemCraftingAPI.generate_item_text(
            base_item_type="Test Item",
            suffixes=[crafting_mod],
        )

        # Should use "+{value} to {display_stat}" format (covers line 619)
        assert "+15 to" in item_text

    def test_generate_item_text_suffix_increased(self) -> None:
        """Test generating item text with suffix INCREASED modifier.

        Covers line 621."""
        item_mod = ItemModifier(
            name="of Damage",
            stat="PhysicalDamage",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.INCREASED,
            tier=ModifierTier.T1,
            is_suffix=True,
        )
        crafting_mod = CraftingModifier(modifier=item_mod, roll_value=15.0)

        item_text = ItemCraftingAPI.generate_item_text(
            base_item_type="Test Item",
            suffixes=[crafting_mod],
        )

        # Should use "{value}% increased {display_stat}" format (covers line 621)
        assert "15% increased" in item_text

    def test_generate_item_text_suffix_more(self) -> None:
        """Test generating item text with suffix MORE modifier - covers line 623."""
        item_mod = ItemModifier(
            name="of Damage",
            stat="FireDamage",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.MORE,
            tier=ModifierTier.T1,
            is_suffix=True,
        )
        crafting_mod = CraftingModifier(modifier=item_mod, roll_value=15.0)

        item_text = ItemCraftingAPI.generate_item_text(
            base_item_type="Test Item",
            suffixes=[crafting_mod],
        )

        # Should use "{value}% more {display_stat}" format (covers line 623)
        assert "15% more" in item_text

    def test_generate_item_text_suffix_reduced(self) -> None:
        """Test generating item text with suffix REDUCED modifier - covers line 625."""
        item_mod = ItemModifier(
            name="of Cost",
            stat="ManaCost",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.REDUCED,
            tier=ModifierTier.T1,
            is_suffix=True,
        )
        crafting_mod = CraftingModifier(modifier=item_mod, roll_value=15.0)

        item_text = ItemCraftingAPI.generate_item_text(
            base_item_type="Test Item",
            suffixes=[crafting_mod],
        )

        # Should use "{value}% reduced {display_stat}" format (covers line 625)
        assert "15% reduced" in item_text

    def test_generate_item_text_suffix_less(self) -> None:
        """Test generating item text with suffix LESS modifier - covers line 627."""
        item_mod = ItemModifier(
            name="of Damage",
            stat="Damage",
            min_value=10.0,
            max_value=20.0,
            mod_type=ModifierType.LESS,
            tier=ModifierTier.T1,
            is_suffix=True,
        )
        crafting_mod = CraftingModifier(modifier=item_mod, roll_value=15.0)

        item_text = ItemCraftingAPI.generate_item_text(
            base_item_type="Test Item",
            suffixes=[crafting_mod],
        )

        # Should use "{value}% less {display_stat}" format (covers line 627)
        assert "15% less" in item_text

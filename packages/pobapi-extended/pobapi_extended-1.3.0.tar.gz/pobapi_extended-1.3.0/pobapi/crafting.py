"""Item crafting API for Path of Building.

This module provides functionality for crafting items, including:
- Modifier database (prefixes and suffixes)
- Item crafting with selected modifiers
- Modifier roll ranges
- Crafting calculations
"""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Union

from pobapi.calculator.modifiers import Modifier, ModifierType

if TYPE_CHECKING:
    from pobapi.types import ModType

__all__ = [
    "ModifierTier",
    "ItemModifier",
    "CraftingModifier",
    "ItemCraftingAPI",
    "CraftingResult",
]


class ModifierTier(Enum):
    """Modifier tier levels."""

    T1 = "T1"  # Tier 1 (highest)
    T2 = "T2"
    T3 = "T3"
    T4 = "T4"
    T5 = "T5"
    T6 = "T6"
    T7 = "T7"
    T8 = "T8"  # Tier 8 (lowest)


@dataclass
class ItemModifier:
    """Represents a craftable item modifier.

    :param name: Modifier name (e.g., "of the Elder").
    :param stat: Stat name affected by this modifier.
    :param mod_type: Type of modifier (flat, increased, etc.).
    :param tier: Modifier tier (T1-T8).
    :param min_value: Minimum roll value.
    :param max_value: Maximum roll value.
    :param is_prefix: Whether this is a prefix modifier.
    :param is_suffix: Whether this is a suffix modifier.
    :param item_level_required: Minimum item level required.
    :param tags: List of item tags this modifier can appear on.
    """

    name: str
    stat: str
    mod_type: ModifierType
    tier: ModifierTier
    min_value: float
    max_value: float
    is_prefix: bool = False
    is_suffix: bool = False
    item_level_required: int = 1
    tags: list[str] | None = None

    def __post_init__(self):
        """Initialize default values."""
        if self.tags is None:
            self.tags = []


@dataclass
class CraftingModifier:
    """Represents a modifier selected for crafting.

    :param modifier: ItemModifier definition.
    :param roll_value: Selected roll value (between min and max).
    """

    modifier: ItemModifier
    roll_value: float

    def to_modifier(self, source: str = "crafted") -> Modifier:
        """Convert to Modifier object.

        :param source: Source identifier.
        :return: Modifier object.
        """
        return Modifier(
            stat=self.modifier.stat,
            value=self.roll_value,
            mod_type=self.modifier.mod_type,
            source=source,
        )


@dataclass
class CraftingResult:
    """Result of item crafting operation.

    :param success: Whether crafting was successful.
    :param item_text: Generated item text.
    :param modifiers: List of Modifier objects from crafted item.
    :param prefix_count: Number of prefixes.
    :param suffix_count: Number of suffixes.
    :param error: Error message if crafting failed.
    """

    success: bool
    item_text: str = ""
    modifiers: list[Modifier] | None = None
    prefix_count: int = 0
    suffix_count: int = 0
    error: str = ""

    def __post_init__(self):
        """Initialize default values."""
        if self.modifiers is None:
            self.modifiers = []


class ItemCraftingAPI:
    """API for crafting items.

    This class provides functionality to craft items with selected modifiers,
    replicating Path of Building's crafting system.
    """

    # Modifier database (prefixes and suffixes)
    # This is a simplified database - full version would load from game data files
    MODIFIER_DATABASE: dict[str, list[ItemModifier]] = {
        # Prefix modifiers
        "prefix": [
            # Life modifiers
            ItemModifier(
                name="of the Elder",
                stat="Life",
                mod_type=ModifierType.FLAT,
                tier=ModifierTier.T1,
                min_value=90.0,
                max_value=99.0,
                is_prefix=True,
                item_level_required=84,
                tags=["life", "defense"],
            ),
            ItemModifier(
                name="of the Elder",
                stat="Life",
                mod_type=ModifierType.FLAT,
                tier=ModifierTier.T2,
                min_value=80.0,
                max_value=89.0,
                is_prefix=True,
                item_level_required=75,
                tags=["life", "defense"],
            ),
            # Mana modifiers
            ItemModifier(
                name="of the Elder",
                stat="Mana",
                mod_type=ModifierType.FLAT,
                tier=ModifierTier.T1,
                min_value=50.0,
                max_value=59.0,
                is_prefix=True,
                item_level_required=84,
                tags=["mana", "defense"],
            ),
            # Energy Shield modifiers
            ItemModifier(
                name="of the Elder",
                stat="EnergyShield",
                mod_type=ModifierType.FLAT,
                tier=ModifierTier.T1,
                min_value=120.0,
                max_value=139.0,
                is_prefix=True,
                item_level_required=84,
                tags=["energy_shield", "defense"],
            ),
            # Damage modifiers
            ItemModifier(
                name="of the Elder",
                stat="PhysicalDamage",
                mod_type=ModifierType.INCREASED,
                tier=ModifierTier.T1,
                min_value=140.0,
                max_value=159.0,
                is_prefix=True,
                item_level_required=84,
                tags=["weapon", "attack"],
            ),
            ItemModifier(
                name="of the Elder",
                stat="FireDamage",
                mod_type=ModifierType.INCREASED,
                tier=ModifierTier.T1,
                min_value=140.0,
                max_value=159.0,
                is_prefix=True,
                item_level_required=84,
                tags=["weapon", "spell"],
            ),
            # Attack Speed modifiers
            ItemModifier(
                name="of the Elder",
                stat="AttackSpeed",
                mod_type=ModifierType.INCREASED,
                tier=ModifierTier.T1,
                min_value=20.0,
                max_value=25.0,
                is_prefix=True,
                item_level_required=84,
                tags=["weapon", "attack"],
            ),
        ],
        # Suffix modifiers
        "suffix": [
            # Resistance modifiers
            ItemModifier(
                name="of the Elder",
                stat="FireResistance",
                mod_type=ModifierType.FLAT,
                tier=ModifierTier.T1,
                min_value=40.0,
                max_value=45.0,
                is_suffix=True,
                item_level_required=84,
                tags=["resistance", "defense"],
            ),
            ItemModifier(
                name="of the Elder",
                stat="ColdResistance",
                mod_type=ModifierType.FLAT,
                tier=ModifierTier.T1,
                min_value=40.0,
                max_value=45.0,
                is_suffix=True,
                item_level_required=84,
                tags=["resistance", "defense"],
            ),
            ItemModifier(
                name="of the Elder",
                stat="LightningResistance",
                mod_type=ModifierType.FLAT,
                tier=ModifierTier.T1,
                min_value=40.0,
                max_value=45.0,
                is_suffix=True,
                item_level_required=84,
                tags=["resistance", "defense"],
            ),
            # Crit modifiers
            ItemModifier(
                name="of the Elder",
                stat="CritChance",
                mod_type=ModifierType.INCREASED,
                tier=ModifierTier.T1,
                min_value=30.0,
                max_value=38.0,
                is_suffix=True,
                item_level_required=84,
                tags=["weapon", "crit"],
            ),
            ItemModifier(
                name="of the Elder",
                stat="CritMultiplier",
                mod_type=ModifierType.INCREASED,
                tier=ModifierTier.T1,
                min_value=25.0,
                max_value=30.0,
                is_suffix=True,
                item_level_required=84,
                tags=["weapon", "crit"],
            ),
            # Movement Speed modifiers
            ItemModifier(
                name="of the Elder",
                stat="MovementSpeed",
                mod_type=ModifierType.INCREASED,
                tier=ModifierTier.T1,
                min_value=25.0,
                max_value=30.0,
                is_suffix=True,
                item_level_required=84,
                tags=["boots", "movement"],
            ),
            # Attribute modifiers
            ItemModifier(
                name="of the Elder",
                stat="Strength",
                mod_type=ModifierType.FLAT,
                tier=ModifierTier.T1,
                min_value=50.0,
                max_value=55.0,
                is_suffix=True,
                item_level_required=84,
                tags=["attribute"],
            ),
            ItemModifier(
                name="of the Elder",
                stat="Dexterity",
                mod_type=ModifierType.FLAT,
                tier=ModifierTier.T1,
                min_value=50.0,
                max_value=55.0,
                is_suffix=True,
                item_level_required=84,
                tags=["attribute"],
            ),
            ItemModifier(
                name="of the Elder",
                stat="Intelligence",
                mod_type=ModifierType.FLAT,
                tier=ModifierTier.T1,
                min_value=50.0,
                max_value=55.0,
                is_suffix=True,
                item_level_required=84,
                tags=["attribute"],
            ),
        ],
    }

    # Stat display mapping for converting internal stat names to display format
    STAT_DISPLAY_MAP: dict[str, str] = {
        "Life": "Life",
        "Mana": "Mana",
        "EnergyShield": "Energy Shield",
        "PhysicalDamage": "Physical Damage",
        "FireDamage": "Fire Damage",
        "ColdDamage": "Cold Damage",
        "LightningDamage": "Lightning Damage",
        "ChaosDamage": "Chaos Damage",
        "AttackSpeed": "Attack Speed",
        "CastSpeed": "Cast Speed",
        "CritChance": "Critical Strike Chance",
        "CritMultiplier": "Critical Strike Multiplier",
        "FireResistance": "Fire Resistance",
        "ColdResistance": "Cold Resistance",
        "LightningResistance": "Lightning Resistance",
        "ChaosResistance": "Chaos Resistance",
        "MovementSpeed": "Movement Speed",
    }

    @staticmethod
    def get_modifiers_by_type(
        modifier_type: Union[str, "ModType"],
        item_level: int = 100,
        tags: list[str] | None = None,
    ) -> list[ItemModifier]:
        """Get available modifiers by type (prefix/suffix).

        :param modifier_type: "prefix" or "suffix", or ModType enum.
        :param item_level: Item level (filters by item_level_required).
        :param tags: Optional list of item tags to filter by.
        :return: List of available ItemModifier objects.
        """
        from pobapi.types import ModType

        # Convert enum to string if needed
        if isinstance(modifier_type, ModType):
            modifier_type = modifier_type.value

        if modifier_type not in ItemCraftingAPI.MODIFIER_DATABASE:
            return []

        all_modifiers = ItemCraftingAPI.MODIFIER_DATABASE[modifier_type]

        # Filter by item level
        filtered = [
            mod for mod in all_modifiers if mod.item_level_required <= item_level
        ]

        # Filter by tags if provided
        if tags:
            filtered = [
                mod
                for mod in filtered
                if mod.tags
                and any(tag.lower() in [t.lower() for t in mod.tags] for tag in tags)
            ]

        return filtered

    @staticmethod
    def get_modifiers_by_stat(
        stat: str, item_level: int = 100, tags: list[str] | None = None
    ) -> list[ItemModifier]:
        """Get available modifiers for a specific stat.

        :param stat: Stat name (e.g., "Life", "FireResistance").
        :param item_level: Item level (filters by item_level_required).
        :param tags: Optional list of item tags to filter by.
        :return: List of available ItemModifier objects.
        """
        from pobapi.types import ModType

        all_modifiers: list[ItemModifier] = []
        for modifier_type in [ModType.PREFIX.value, ModType.SUFFIX.value]:
            all_modifiers.extend(
                ItemCraftingAPI.MODIFIER_DATABASE.get(modifier_type, [])
            )

        # Filter by stat
        filtered = [mod for mod in all_modifiers if mod.stat == stat]

        # Filter by item level
        filtered = [mod for mod in filtered if mod.item_level_required <= item_level]

        # Filter by tags if provided
        if tags:
            filtered = [
                mod
                for mod in filtered
                if mod.tags
                and any(tag.lower() in [t.lower() for t in mod.tags] for tag in tags)
            ]

        return filtered

    @staticmethod
    def craft_item(
        base_item_type: str,
        item_level: int,
        prefixes: list[CraftingModifier] | None = None,
        suffixes: list[CraftingModifier] | None = None,
        implicit_mods: list[str] | None = None,
    ) -> CraftingResult:
        """Craft an item with selected modifiers.

        :param base_item_type: Base item type
            (e.g., "Leather Belt", "Two-Handed Sword").
        :param item_level: Item level.
        :param prefixes: List of prefix modifiers to apply.
        :param suffixes: List of suffix modifiers to apply.
        :param implicit_mods: List of implicit modifier texts (optional).
        :return: CraftingResult with crafted item.
        """
        if prefixes is None:
            prefixes = []
        if suffixes is None:
            suffixes = []
        if implicit_mods is None:
            implicit_mods = []

        # Validate modifier counts
        if len(prefixes) > 3:
            return CraftingResult(
                success=False, error="Maximum 3 prefixes allowed on rare items"
            )
        if len(suffixes) > 3:
            return CraftingResult(
                success=False, error="Maximum 3 suffixes allowed on rare items"
            )

        # Validate item level
        for crafting_mod in prefixes + suffixes:
            if crafting_mod.modifier.item_level_required > item_level:
                return CraftingResult(
                    success=False,
                    error=(
                        f"Modifier {crafting_mod.modifier.name} requires "
                        f"item level {crafting_mod.modifier.item_level_required}, "
                        f"but item is level {item_level}"
                    ),
                )

        # Build item text
        item_lines: list[str] = []
        item_lines.append(base_item_type)
        item_lines.append("Rarity: RARE")

        # Add implicit modifiers
        for implicit in implicit_mods:
            item_lines.append(implicit)

        # Add prefixes
        for prefix in prefixes:
            mod: ItemModifier = prefix.modifier
            value = prefix.roll_value
            display_stat = (
                ItemCraftingAPI.STAT_DISPLAY_MAP.get(mod.stat)
                or mod.stat.replace("_", " ").title()
            )
            # Format modifier text based on type
            if mod.mod_type == ModifierType.FLAT:
                # For life/mana/es, use "to maximum"
                if mod.stat in ["Life", "Mana", "EnergyShield"]:
                    item_lines.append(f"+{int(value)} to maximum {display_stat}")
                else:
                    item_lines.append(f"+{int(value)} to {display_stat}")
            elif mod.mod_type == ModifierType.INCREASED:
                # For life/mana/es, use "maximum"
                if mod.stat in ["Life", "Mana", "EnergyShield"]:
                    item_lines.append(f"{int(value)}% increased maximum {display_stat}")
                else:
                    item_lines.append(f"{int(value)}% increased {display_stat}")
            elif mod.mod_type == ModifierType.MORE:
                item_lines.append(f"{int(value)}% more {display_stat}")
            elif mod.mod_type == ModifierType.REDUCED:
                item_lines.append(f"{int(value)}% reduced {display_stat}")
            elif mod.mod_type == ModifierType.LESS:
                item_lines.append(f"{int(value)}% less {display_stat}")

        # Add suffixes
        for suffix in suffixes:
            suffix_mod: ItemModifier = suffix.modifier
            value = suffix.roll_value
            display_stat = (
                ItemCraftingAPI.STAT_DISPLAY_MAP.get(suffix_mod.stat)
                or suffix_mod.stat.replace("_", " ").title()
            )
            # Format modifier text based on type
            if suffix_mod.mod_type == ModifierType.FLAT:
                # For life/mana/es, use "to maximum"
                if suffix_mod.stat in ["Life", "Mana", "EnergyShield"]:
                    item_lines.append(f"+{int(value)} to maximum {display_stat}")
                else:
                    item_lines.append(f"+{int(value)} to {display_stat}")
            elif suffix_mod.mod_type == ModifierType.INCREASED:
                # For life/mana/es, use "maximum"
                if suffix_mod.stat in ["Life", "Mana", "EnergyShield"]:
                    item_lines.append(f"{int(value)}% increased maximum {display_stat}")
                else:
                    item_lines.append(f"{int(value)}% increased {display_stat}")
            elif suffix_mod.mod_type == ModifierType.MORE:
                item_lines.append(f"{int(value)}% more {display_stat}")
            elif suffix_mod.mod_type == ModifierType.REDUCED:
                item_lines.append(f"{int(value)}% reduced {display_stat}")
            elif suffix_mod.mod_type == ModifierType.LESS:
                item_lines.append(f"{int(value)}% less {display_stat}")

        item_text = "\n".join(item_lines)

        # Convert to Modifier objects
        modifiers: list[Modifier] = []
        for prefix_crafting_mod in prefixes:
            modifiers.append(prefix_crafting_mod.to_modifier(source="crafted:prefix"))
        for suffix_crafting_mod in suffixes:
            modifiers.append(suffix_crafting_mod.to_modifier(source="crafted:suffix"))

        return CraftingResult(
            success=True,
            item_text=item_text,
            modifiers=modifiers,
            prefix_count=len(prefixes),
            suffix_count=len(suffixes),
        )

    @staticmethod
    def generate_item_text(
        base_item_type: str,
        prefixes: list[CraftingModifier] | None = None,
        suffixes: list[CraftingModifier] | None = None,
        implicit_mods: list[str] | None = None,
    ) -> str:
        """Generate item text from crafted modifiers.

        :param base_item_type: Base item type.
        :param prefixes: List of prefix modifiers.
        :param suffixes: List of suffix modifiers.
        :param implicit_mods: List of implicit modifier texts.
        :return: Item text string.
        """
        if prefixes is None:
            prefixes = []
        if suffixes is None:
            suffixes = []
        if implicit_mods is None:
            implicit_mods = []

        item_lines: list[str] = []
        item_lines.append(base_item_type)
        item_lines.append("Rarity: RARE")

        # Add implicit modifiers
        for implicit in implicit_mods:
            item_lines.append(implicit)

        # Add prefixes
        for prefix in prefixes:
            mod: ItemModifier = prefix.modifier
            value = prefix.roll_value
            display_stat = (
                ItemCraftingAPI.STAT_DISPLAY_MAP.get(mod.stat)
                or mod.stat.replace("_", " ").title()
            )
            # Format modifier text based on type
            if mod.mod_type == ModifierType.FLAT:
                # For life/mana/es, use "to maximum"
                if mod.stat in ["Life", "Mana", "EnergyShield"]:
                    item_lines.append(f"+{int(value)} to maximum {display_stat}")
                else:
                    item_lines.append(f"+{int(value)} to {display_stat}")
            elif mod.mod_type == ModifierType.INCREASED:
                # For life/mana/es, use "maximum"
                if mod.stat in ["Life", "Mana", "EnergyShield"]:
                    item_lines.append(f"{int(value)}% increased maximum {display_stat}")
                else:
                    item_lines.append(f"{int(value)}% increased {display_stat}")
            elif mod.mod_type == ModifierType.MORE:
                item_lines.append(f"{int(value)}% more {display_stat}")
            elif mod.mod_type == ModifierType.REDUCED:
                item_lines.append(f"{int(value)}% reduced {display_stat}")
            elif mod.mod_type == ModifierType.LESS:
                item_lines.append(f"{int(value)}% less {display_stat}")

        # Add suffixes
        for suffix in suffixes:
            suffix_mod: ItemModifier = suffix.modifier
            value = suffix.roll_value
            display_stat = (
                ItemCraftingAPI.STAT_DISPLAY_MAP.get(suffix_mod.stat)
                or suffix_mod.stat.replace("_", " ").title()
            )
            # Format modifier text based on type
            if suffix_mod.mod_type == ModifierType.FLAT:
                # For life/mana/es, use "to maximum"
                if suffix_mod.stat in ["Life", "Mana", "EnergyShield"]:
                    item_lines.append(f"+{int(value)} to maximum {display_stat}")
                else:
                    item_lines.append(f"+{int(value)} to {display_stat}")
            elif suffix_mod.mod_type == ModifierType.INCREASED:
                # For life/mana/es, use "maximum"
                if suffix_mod.stat in ["Life", "Mana", "EnergyShield"]:
                    item_lines.append(f"{int(value)}% increased maximum {display_stat}")
                else:
                    item_lines.append(f"{int(value)}% increased {display_stat}")
            elif suffix_mod.mod_type == ModifierType.MORE:
                item_lines.append(f"{int(value)}% more {display_stat}")
            elif suffix_mod.mod_type == ModifierType.REDUCED:
                item_lines.append(f"{int(value)}% reduced {display_stat}")
            elif suffix_mod.mod_type == ModifierType.LESS:
                item_lines.append(f"{int(value)}% less {display_stat}")

        return "\n".join(item_lines)

    @staticmethod
    def calculate_modifier_value(
        modifier: ItemModifier, roll_percent: float = 100.0
    ) -> float:
        """Calculate modifier value based on roll percentage.

        :param modifier: ItemModifier definition.
        :param roll_percent: Roll percentage (0-100, where 100 is perfect roll).
        :return: Calculated modifier value.
        """
        roll_percent = max(0.0, min(100.0, roll_percent))
        value_range = modifier.max_value - modifier.min_value
        roll_value = modifier.min_value + (value_range * roll_percent / 100.0)
        return roll_value

    @staticmethod
    def get_available_prefixes(
        item_level: int = 100, tags: list[str] | None = None
    ) -> list[ItemModifier]:
        """Get available prefix modifiers.

        :param item_level: Item level.
        :param tags: Optional item tags.
        :return: List of available prefix modifiers.
        """
        from pobapi.types import ModType

        return ItemCraftingAPI.get_modifiers_by_type(ModType.PREFIX, item_level, tags)

    @staticmethod
    def get_available_suffixes(
        item_level: int = 100, tags: list[str] | None = None
    ) -> list[ItemModifier]:
        """Get available suffix modifiers.

        :param item_level: Item level.
        :param tags: Optional item tags.
        :return: List of available suffix modifiers.
        """
        from pobapi.types import ModType

        return ItemCraftingAPI.get_modifiers_by_type(ModType.SUFFIX, item_level, tags)

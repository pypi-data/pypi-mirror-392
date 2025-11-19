"""Modifier system for Path of Building calculations.

This module handles parsing and applying modifiers from items, passive tree,
skills, and configuration. It replicates Path of Building's modifier system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

__all__ = ["ModifierType", "Modifier", "ModifierSystem"]


class ModifierType(Enum):
    """Types of modifiers in Path of Exile."""

    # Additive modifiers (stack additively)
    FLAT = "flat"  # Flat addition: +X
    INCREASED = "increased"  # Increased: +X%
    REDUCED = "reduced"  # Reduced: -X%

    # Multiplicative modifiers (stack multiplicatively)
    MORE = "more"  # More: X% more
    LESS = "less"  # Less: X% less

    # Special modifiers
    BASE = "base"  # Base value override
    FLAG = "flag"  # Boolean flag
    MULTIPLIER = "multiplier"  # Multiplier: Xx


@dataclass
class Modifier:
    """Represents a single modifier.

    :param stat: Stat name (e.g., "Life", "PhysicalDamage", "CritChance").
    :param value: Modifier value.
    :param mod_type: Type of modifier (flat, increased, more, etc.).
    :param source: Source of modifier (item, passive, skill, config).
    :param conditions: Conditions that must be met for modifier to apply.
    """

    stat: str
    value: float
    mod_type: ModifierType
    source: str
    conditions: dict[str, Any] = field(default_factory=dict)

    def applies(self, context: dict[str, Any]) -> bool:
        """Check if modifier applies in given context.

        :param context: Current calculation context.
        :return: True if modifier applies.
        """
        if not self.conditions:
            return True

        # Use ConditionEvaluator for complex condition evaluation
        from pobapi.calculator.conditional import ConditionEvaluator

        return ConditionEvaluator.evaluate_all_conditions(self.conditions, context)


class ModifierSystem:
    """System for managing and applying modifiers.

    This class replicates Path of Building's modifier system,
    handling the collection and application of all modifiers
    from various sources.
    """

    def __init__(self):
        """Initialize modifier system."""
        self._modifiers: list[Modifier] = []

    def add_modifier(self, modifier: Modifier) -> None:
        """Add a modifier to the system.

        :param modifier: Modifier to add.
        """
        self._modifiers.append(modifier)

    def add_modifiers(self, modifiers: list[Modifier]) -> None:
        """Add multiple modifiers.

        :param modifiers: List of modifiers to add.
        """
        self._modifiers.extend(modifiers)

    def _applies_excluding_requires_attribute(
        self, modifier: Modifier, context: dict[str, Any]
    ) -> bool:
        """Check if modifier applies, excluding requires_attribute from conditions.

        :param modifier: Modifier to check.
        :param context: Current calculation context.
        :return: True if modifier applies.
        """
        if not modifier.conditions:
            return True

        # Create conditions dict without requires_attribute
        conditions_without_attr = {
            k: v for k, v in modifier.conditions.items() if k != "requires_attribute"
        }

        if not conditions_without_attr:
            return True

        # Use ConditionEvaluator for remaining conditions
        from pobapi.calculator.conditional import ConditionEvaluator

        return ConditionEvaluator.evaluate_all_conditions(
            conditions_without_attr, context
        )

    def get_modifiers(
        self, stat: str, context: dict[str, Any] | None = None
    ) -> list[Modifier]:
        """Get all modifiers for a specific stat.

        :param stat: Stat name to get modifiers for.
        :param context: Current calculation context.
        :return: List of applicable modifiers.
        """
        if context is None:
            context = {}

        return [
            mod for mod in self._modifiers if mod.stat == stat and mod.applies(context)
        ]

    def calculate_stat(
        self, stat: str, base_value: float = 0.0, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate final value of a stat after applying all modifiers.

        This replicates Path of Building's modifier application order:
        1. Base value
        2. Flat modifiers (additive)
        3. Increased/Reduced modifiers (additive, then multiplicative)
        4. More/Less modifiers (multiplicative)

        :param stat: Stat name to calculate.
        :param base_value: Base value of the stat.
        :param context: Current calculation context.
        :return: Final calculated value.
        """
        if context is None:
            context = {}

        applicable_mods = self.get_modifiers(stat, context)

        # Handle "per attribute" modifiers first
        # These need to be calculated based on current attribute values
        # Also search for modifiers that start with the stat name and contain "Per"
        # (e.g., "LifePerStrength" when calculating "Life")
        # Note: requires_attribute is metadata, not a blocking condition
        per_attribute_mods = [
            m
            for m in self._modifiers
            if m.stat.startswith(stat)
            and "Per" in m.stat
            and m.conditions.get("requires_attribute")
        ]
        # Filter by applies, but exclude requires_attribute from condition check
        per_attribute_mods = [
            m
            for m in per_attribute_mods
            if self._applies_excluding_requires_attribute(m, context)
        ]
        for mod in per_attribute_mods:
            attribute_name = mod.conditions.get("requires_attribute", "").lower()
            attribute_value = 0.0

            # Get attribute value from context
            if attribute_name in ("strength", "str"):
                attribute_value = context.get("strength", 0.0)
            elif attribute_name in ("dexterity", "dex"):
                attribute_value = context.get("dexterity", 0.0)
            elif attribute_name in ("intelligence", "int"):
                attribute_value = context.get("intelligence", 0.0)

            # Calculate bonus from attribute
            if attribute_value > 0:
                # The modifier value is percentage per attribute point
                # So 0.5% per Strength means: 0.5 * strength = total percentage
                bonus = mod.value * attribute_value
                # Create a temporary increased modifier
                temp_mod = Modifier(
                    stat=stat,
                    value=bonus,
                    mod_type=ModifierType.INCREASED,
                    source=mod.source,
                )
                applicable_mods.append(temp_mod)
                # Don't remove the original per-attribute modifier if it's for
                # a different stat (e.g., "LifePerStrength" when calculating
                # "LifePerStrength" directly)
                # Only remove if it's for the base stat
                # (e.g., "LifePerStrength" when calculating "Life")
                # Note: This condition is currently unreachable because per-attribute
                # modifiers have different stat names and won't be in applicable_mods
                # (which only contains modifiers with stat == stat_name)
                if mod.stat != stat and mod in applicable_mods:  # pragma: no cover
                    applicable_mods.remove(mod)

        # Separate modifiers by type
        flat_mods = [m for m in applicable_mods if m.mod_type == ModifierType.FLAT]
        increased_mods = [
            m for m in applicable_mods if m.mod_type == ModifierType.INCREASED
        ]
        reduced_mods = [
            m for m in applicable_mods if m.mod_type == ModifierType.REDUCED
        ]
        more_mods = [m for m in applicable_mods if m.mod_type == ModifierType.MORE]
        less_mods = [m for m in applicable_mods if m.mod_type == ModifierType.LESS]
        base_mods = [m for m in applicable_mods if m.mod_type == ModifierType.BASE]
        multiplier_mods = [
            m for m in applicable_mods if m.mod_type == ModifierType.MULTIPLIER
        ]

        # Start with base value (or override if base modifier exists)
        if base_mods:
            result = base_mods[-1].value  # Last base modifier wins
        else:
            result = base_value

        # Apply flat modifiers (additive)
        for mod in flat_mods:
            result += mod.value

        # Apply increased/reduced modifiers (additive, then multiplicative)
        total_increased = sum(m.value for m in increased_mods)
        total_reduced = sum(m.value for m in reduced_mods)
        net_increase = total_increased - total_reduced
        if net_increase != 0:
            result *= 1.0 + (net_increase / 100.0)

        # Apply more/less modifiers (multiplicative)
        for mod in more_mods:
            result *= 1.0 + (mod.value / 100.0)
        for mod in less_mods:
            result *= 1.0 - (mod.value / 100.0)

        # Apply multipliers
        for mod in multiplier_mods:
            result *= mod.value

        return result

    def count(self) -> int:
        """Get the total number of modifiers in the system.

        :return: Total count of modifiers.
        """
        return len(self._modifiers)

    def clear(self) -> None:
        """Clear all modifiers."""
        self._modifiers.clear()

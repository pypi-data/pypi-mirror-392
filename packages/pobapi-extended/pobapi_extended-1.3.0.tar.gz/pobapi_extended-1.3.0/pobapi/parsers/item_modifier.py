"""Parser for extracting modifiers from item text.

This module parses item text (as shown in-game) and extracts modifiers,
replicating Path of Building's item modifier parsing system.
"""

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

__all__ = ["ItemModifierParser"]


def _get_modifier_types():
    """Lazy import of Modifier and ModifierType to avoid circular dependencies."""
    from pobapi.calculator.modifiers import Modifier, ModifierType

    return Modifier, ModifierType


class ItemModifierParser:
    """Parser for extracting modifiers from item text.

    This class parses item text lines and converts them to Modifier objects,
    matching Path of Building's modifier parsing logic.
    """

    # Common effect mappings for chance patterns
    # Supports both "freeze" and "to freeze" formats
    _EFFECT_MAPPINGS = {
        "critical strike": "CritChance",
        "to freeze": "FreezeChance",
        "freeze": "FreezeChance",
        "to ignite": "IgniteChance",
        "ignite": "IgniteChance",
        "to shock": "ShockChance",
        "shock": "ShockChance",
        "to poison": "PoisonChance",
        "poison": "PoisonChance",
        "to bleed": "BleedChance",
        "bleed": "BleedChance",
    }

    # Recently condition mappings for "recently" modifiers
    _RECENTLY_MAPPINGS = {
        "used a skill": "used_skill_recently",  # Past tense variant
        "use a skill": "used_skill_recently",
        "taken damage": "been_hit_recently",  # Past tense variant
        "took damage": "been_hit_recently",  # Past tense variant (alternative)
        "take damage": "been_hit_recently",
        "killed": "killed_recently",  # Past tense variant
        "kill": "killed_recently",
        "crit": "crit_recently",
        "hit": "hit_recently",
        "blocked": "blocked_recently",  # Past tense variant
        "block": "blocked_recently",
    }

    # Patterns for different modifier types
    # These patterns match Path of Exile's modifier text format

    # Flat modifiers: "+X to Y"
    FLAT_PATTERN = re.compile(r"^\+(\d+(?:\.\d+)?)\s+to\s+(.+)$", re.IGNORECASE)

    # Increased modifiers: "X% increased Y"
    INCREASED_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)?)%\s+increased\s+(.+)$", re.IGNORECASE
    )

    # More modifiers: "X% more Y"
    MORE_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)%\s+more\s+(.+)$", re.IGNORECASE)

    # Reduced modifiers: "X% reduced Y"
    REDUCED_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)%\s+reduced\s+(.+)$", re.IGNORECASE)

    # Less modifiers: "X% less Y"
    LESS_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)%\s+less\s+(.+)$", re.IGNORECASE)

    # Adds X to Y damage: "Adds X to Y Z Damage"
    ADDS_DAMAGE_PATTERN = re.compile(
        r"^Adds\s+(\d+(?:\.\d+)?)\s+to\s+(\d+(?:\.\d+)?)\s+(.+?)\s+Damage$",
        re.IGNORECASE,
    )

    # Base stat: "X to Y" (for base damage on weapons)
    BASE_DAMAGE_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)?)\s+to\s+(\d+(?:\.\d+)?)\s+(.+?)\s+Damage$", re.IGNORECASE
    )

    # "X to maximum Y" pattern
    TO_MAXIMUM_PATTERN = re.compile(
        r"^\+(\d+(?:\.\d+)?)\s+to\s+maximum\s+(.+)$", re.IGNORECASE
    )

    # "X% of Y converted to Z" pattern (damage conversion)
    CONVERSION_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)?)%\s+of\s+(.+?)\s+converted\s+to\s+(.+)$", re.IGNORECASE
    )

    # "X per Y" pattern (e.g., "X per level", "X per charge")
    PER_PATTERN = re.compile(
        r"^\+(\d+(?:\.\d+)?)\s+to\s+(.+?)\s+per\s+(.+)$", re.IGNORECASE
    )

    # "X% chance to Y" pattern
    CHANCE_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)?)%\s+chance\s+to\s+(.+)$", re.IGNORECASE
    )

    # "Socketed gems have X" pattern
    SOCKETED_PATTERN = re.compile(r"^Socketed\s+gems\s+have\s+(.+)$", re.IGNORECASE)

    # "X% increased Y per Y" pattern (e.g., "1% increased Damage per 10 Strength")
    PER_STAT_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)?)%\s+increased\s+(.+?)\s+per\s+(\d+(?:\.\d+)?)\s+(.+)$",
        re.IGNORECASE,
    )

    # "X% chance to Y when Z" pattern (conditional chance modifiers)
    CHANCE_WHEN_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)?)%\s+chance\s+to\s+(.+?)\s+when\s+(.+)$", re.IGNORECASE
    )

    # "X% chance to Y on Z" pattern
    CHANCE_ON_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)?)%\s+chance\s+to\s+(.+?)\s+on\s+(.+)$", re.IGNORECASE
    )

    # "X% chance to Y if Z" pattern
    CHANCE_IF_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)?)%\s+chance\s+to\s+(.+?)\s+if\s+(.+)$", re.IGNORECASE
    )

    # "X to all Y" pattern (e.g., "X to all Elemental Resistances")
    TO_ALL_PATTERN = re.compile(r"^\+(\d+(?:\.\d+)?)\s+to\s+all\s+(.+)$", re.IGNORECASE)

    # "X% to all Y" pattern
    PERCENT_TO_ALL_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)?)%\s+to\s+all\s+(.+)$", re.IGNORECASE
    )

    # "X% chance to Y if you've Z recently" pattern (recently modifiers)
    CHANCE_IF_RECENTLY_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)?)%\s+chance\s+to\s+(.+?)\s+if\s+you['']?ve\s+(.+?)\s+recently$",
        re.IGNORECASE,
    )

    # "X% chance to Y if you Z recently" pattern (alternative recently format)
    CHANCE_IF_RECENTLY_ALT_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)?)%\s+chance\s+to\s+(.+?)\s+if\s+you\s+(.+?)\s+recently$",
        re.IGNORECASE,
    )

    # "X% chance to Y on kill" pattern
    CHANCE_ON_KILL_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)?)%\s+chance\s+to\s+(.+?)\s+on\s+kill$", re.IGNORECASE
    )

    # "X% chance to Y on hit" pattern
    CHANCE_ON_HIT_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)?)%\s+chance\s+to\s+(.+?)\s+on\s+hit$", re.IGNORECASE
    )

    # "X% chance to Y on crit" pattern
    CHANCE_ON_CRIT_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)?)%\s+chance\s+to\s+(.+?)\s+on\s+crit$", re.IGNORECASE
    )

    # "X% chance to Y on block" pattern
    CHANCE_ON_BLOCK_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)?)%\s+chance\s+to\s+(.+?)\s+on\s+block$", re.IGNORECASE
    )

    # "X% chance to Y when hit" pattern
    CHANCE_WHEN_HIT_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)?)%\s+chance\s+to\s+(.+?)\s+when\s+hit$", re.IGNORECASE
    )

    # "X% chance to Y when you kill" pattern
    CHANCE_WHEN_KILL_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)?)%\s+chance\s+to\s+(.+?)\s+when\s+you\s+kill$", re.IGNORECASE
    )

    # "X% chance to Y when you use a skill" pattern
    CHANCE_WHEN_USE_SKILL_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)?)%\s+chance\s+to\s+(.+?)\s+when\s+you\s+use\s+a\s+skill$",
        re.IGNORECASE,
    )

    # "X% chance to Y when you take damage" pattern
    CHANCE_WHEN_TAKE_DAMAGE_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)?)%\s+chance\s+to\s+(.+?)\s+when\s+you\s+take\s+damage$",
        re.IGNORECASE,
    )

    # "X% chance to Y when you block" pattern
    CHANCE_WHEN_BLOCK_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)?)%\s+chance\s+to\s+(.+?)\s+when\s+you\s+block$", re.IGNORECASE
    )

    # Veiled modifier pattern: "Veiled" prefix or "(Veiled)" suffix
    VEILED_PATTERN = re.compile(r"^(?:Veiled|\(Veiled\))\s*(.+)$", re.IGNORECASE)

    # Corrupted modifier pattern: "Corrupted" prefix or "(Corrupted)" suffix
    CORRUPTED_PATTERN = re.compile(
        r"^(?:Corrupted|\(Corrupted\))\s*(.+)$", re.IGNORECASE
    )

    # "X to Y" pattern (without +) - for some modifiers
    FLAT_NO_PLUS_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)\s+to\s+(.+)$", re.IGNORECASE)

    @staticmethod
    def parse_line(line: str, source: str = "item") -> list:
        """Parse a single line of item text and extract modifiers.

        :param line: Line of item text.
        :param source: Source identifier for the modifier.
        :return: List of Modifier objects extracted from the line.
        """
        line = line.strip()
        if not line:
            return []

        modifier_class, modifier_type = _get_modifier_types()
        modifiers: list = []

        # Try different patterns
        # Check more specific patterns first

        # "X per Y" pattern (must be checked before FLAT_PATTERN to avoid false matches)
        match = ItemModifierParser.PER_PATTERN.match(line)
        if match:
            # This is complex - would need character level, charges, etc.
            # For now, we'll extract the base value and stat name
            # Full implementation would need to calculate based on context
            value = float(match.group(1))
            stat_base = match.group(2).strip()
            per_stat = match.group(3).strip().lower()

            # Common "per" patterns
            if "level" in per_stat:
                # Would need character level from context
                # For now, assume level 90 for calculation
                assumed_level = 90.0
                total_value = value * assumed_level
                stat_name = ItemModifierParser._normalize_stat_name(stat_base)
                modifiers.append(
                    modifier_class(
                        stat=stat_name,
                        value=total_value,
                        mod_type=modifier_type.FLAT,
                        source=source,
                    )
                )
                return modifiers
            elif "charge" in per_stat:
                # Would need charge count from context
                # For now, skip (charges are handled separately)
                pass
            else:
                # Unknown "per" pattern - skip for now
                pass

        # "X to maximum Y" pattern (must be checked before FLAT_PATTERN
        # as it's more specific)
        match = ItemModifierParser.TO_MAXIMUM_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            stat_name = ItemModifierParser._normalize_stat_name(match.group(2))
            modifiers.append(
                modifier_class(
                    stat=stat_name,
                    value=value,
                    mod_type=modifier_type.FLAT,
                    source=source,
                )
            )
            return modifiers

        # Flat modifier: "+X to Y"
        match = ItemModifierParser.FLAT_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            stat_name = ItemModifierParser._normalize_stat_name(match.group(2))
            modifiers.append(
                modifier_class(
                    stat=stat_name,
                    value=value,
                    mod_type=modifier_type.FLAT,
                    source=source,
                )
            )
            return modifiers

        # "X% increased Y per Y" pattern (must be checked before
        # INCREASED_PATTERN as it's more specific)
        match = ItemModifierParser.PER_STAT_PATTERN.match(line)
        if match:
            # This requires attribute values from context
            # For now, we'll create a modifier that needs special handling
            value_per_unit = float(match.group(1))
            stat_name = ItemModifierParser._normalize_stat_name(match.group(2))
            units_per_bonus = float(match.group(3))
            attribute_name = match.group(4).strip().lower()

            # Create a special modifier that will be calculated based on attributes
            # This would need special handling in the calculation engine
            modifiers.append(
                modifier_class(
                    stat=f"{stat_name}Per{attribute_name.capitalize()}",
                    value=value_per_unit / units_per_bonus,
                    mod_type=modifier_type.INCREASED,
                    source=source,
                    conditions={"requires_attribute": attribute_name},
                )
            )
            return modifiers

        # Increased modifier: "X% increased Y"
        match = ItemModifierParser.INCREASED_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            stat_name = ItemModifierParser._normalize_stat_name(match.group(2))
            modifiers.append(
                modifier_class(
                    stat=stat_name,
                    value=value,
                    mod_type=modifier_type.INCREASED,
                    source=source,
                )
            )
            return modifiers

        # More modifier: "X% more Y"
        match = ItemModifierParser.MORE_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            stat_name = ItemModifierParser._normalize_stat_name(match.group(2))
            modifiers.append(
                modifier_class(
                    stat=stat_name,
                    value=value,
                    mod_type=modifier_type.MORE,
                    source=source,
                )
            )
            return modifiers

        # Reduced modifier: "X% reduced Y"
        match = ItemModifierParser.REDUCED_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            stat_name = ItemModifierParser._normalize_stat_name(match.group(2))
            modifiers.append(
                modifier_class(
                    stat=stat_name,
                    value=value,
                    mod_type=modifier_type.REDUCED,
                    source=source,
                )
            )
            return modifiers

        # Less modifier: "X% less Y"
        match = ItemModifierParser.LESS_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            stat_name = ItemModifierParser._normalize_stat_name(match.group(2))
            modifiers.append(
                modifier_class(
                    stat=stat_name,
                    value=value,
                    mod_type=modifier_type.LESS,
                    source=source,
                )
            )
            return modifiers

        # Adds damage: "Adds X to Y Z Damage"
        match = ItemModifierParser.ADDS_DAMAGE_PATTERN.match(line)
        if match:
            min_val = float(match.group(1))
            max_val = float(match.group(2))
            damage_type = match.group(3).strip()
            avg_val = (min_val + max_val) / 2.0

            stat_name = ItemModifierParser._normalize_damage_stat(damage_type, "Added")
            modifiers.append(
                modifier_class(
                    stat=stat_name,
                    value=avg_val,
                    mod_type=modifier_type.FLAT,
                    source=source,
                )
            )
            return modifiers

        # Base damage: "X to Y Z Damage" (on weapons)
        match = ItemModifierParser.BASE_DAMAGE_PATTERN.match(line)
        if match:
            min_val = float(match.group(1))
            max_val = float(match.group(2))
            damage_type = match.group(3).strip()
            avg_val = (min_val + max_val) / 2.0

            stat_name = ItemModifierParser._normalize_damage_stat(damage_type, "Base")
            modifiers.append(
                modifier_class(
                    stat=stat_name,
                    value=avg_val,
                    mod_type=modifier_type.BASE,
                    source=source,
                )
            )
            return modifiers

        # "X% of Y converted to Z" pattern
        match = ItemModifierParser.CONVERSION_PATTERN.match(line)
        if match:
            percent = float(match.group(1))
            from_type = match.group(2).strip()
            to_type = match.group(3).strip()

            # Create conversion modifier
            from_stat = ItemModifierParser._normalize_damage_stat(from_type, "")
            to_stat = ItemModifierParser._normalize_damage_stat(to_type, "")
            conversion_stat = f"{from_stat}To{to_stat}"

            modifiers.append(
                modifier_class(
                    stat=conversion_stat,
                    value=percent,
                    mod_type=modifier_type.FLAT,
                    source=source,
                )
            )
            return modifiers

        # "X to all Y" pattern
        match = ItemModifierParser.TO_ALL_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            stat_base = match.group(2).strip().lower()

            # Apply to all related stats
            if "resistance" in stat_base or "resist" in stat_base:
                # Apply to all resistances
                for res_type in ["Fire", "Cold", "Lightning", "Chaos"]:
                    modifiers.append(
                        modifier_class(
                            stat=f"{res_type}Resistance",
                            value=value,
                            mod_type=modifier_type.FLAT,
                            source=source,
                        )
                    )
            else:
                # Try to normalize and apply
                stat_name = ItemModifierParser._normalize_stat_name(
                    stat_base
                )  # pragma: no cover
                modifiers.append(  # pragma: no cover
                    modifier_class(
                        stat=stat_name,
                        value=value,
                        mod_type=modifier_type.FLAT,
                        source=source,
                    )
                )
            return modifiers

        # "X% to all Y" pattern
        match = ItemModifierParser.PERCENT_TO_ALL_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            stat_base = match.group(2).strip().lower()

            # Apply to all related stats
            if "resistance" in stat_base or "resist" in stat_base:
                # Apply to all resistances
                for res_type in ["Fire", "Cold", "Lightning", "Chaos"]:
                    modifiers.append(
                        modifier_class(
                            stat=f"{res_type}Resistance",
                            value=value,
                            mod_type=modifier_type.INCREASED,
                            source=source,
                        )
                    )
            else:
                # Try to normalize and apply
                stat_name = ItemModifierParser._normalize_stat_name(stat_base)
                modifiers.append(
                    modifier_class(
                        stat=stat_name,
                        value=value,
                        mod_type=modifier_type.INCREASED,
                        source=source,
                    )
                )
            return modifiers

        # "X% chance to Y" pattern
        match = ItemModifierParser.CHANCE_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            effect = match.group(2).strip().lower()

            # Map common chance effects to stats
            chance_mappings = {
                "critical strike": "CritChance",
                "to freeze": "FreezeChance",
                "to ignite": "IgniteChance",
                "to shock": "ShockChance",
                "to poison": "PoisonChance",
                "to bleed": "BleedChance",
                "to block": "BlockChance",
            }

            for key, stat in chance_mappings.items():
                if key in effect:
                    modifiers.append(
                        modifier_class(
                            stat=stat,
                            value=value,
                            mod_type=modifier_type.FLAT,
                            source=source,
                        )
                    )
                    return modifiers

        # "Socketed gems have X" pattern
        match = ItemModifierParser.SOCKETED_PATTERN.match(line)
        if match:
            # Parse the modifier inside "Socketed gems have X"
            inner_mod = match.group(1).strip()
            # Recursively parse the inner modifier
            inner_modifiers = ItemModifierParser.parse_line(
                inner_mod, source=f"{source}:socketed"
            )
            modifiers.extend(inner_modifiers)
            return modifiers

        # "X% chance to Y when Z" pattern
        match = ItemModifierParser.CHANCE_WHEN_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            effect = match.group(2).strip().lower()
            condition = match.group(3).strip().lower()

            # Map effects to stats
            matched_stat = ItemModifierParser._match_effect(
                effect, ItemModifierParser._EFFECT_MAPPINGS
            )
            if matched_stat:
                modifiers.append(
                    modifier_class(
                        stat=matched_stat,
                        value=value,
                        mod_type=modifier_type.FLAT,
                        source=source,
                        conditions={"when": condition},
                    )
                )
                return modifiers

        # "X% chance to Y on Z" pattern (similar to "when")
        match = ItemModifierParser.CHANCE_ON_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            effect = match.group(2).strip().lower()
            condition = match.group(3).strip().lower()

            matched_stat = ItemModifierParser._match_effect(
                effect, ItemModifierParser._EFFECT_MAPPINGS
            )
            if matched_stat:
                modifiers.append(
                    modifier_class(
                        stat=matched_stat,
                        value=value,
                        mod_type=modifier_type.FLAT,
                        source=source,
                        conditions={"on": condition},
                    )
                )
                return modifiers

        # "X% chance to Y if you've Z recently" pattern (must be checked
        # before CHANCE_IF_PATTERN as it's more specific)
        match = ItemModifierParser.CHANCE_IF_RECENTLY_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            effect = match.group(2).strip().lower()
            condition = match.group(3).strip().lower()

            recently_condition = None
            # Sort by key length (longest first) to check more specific matches first
            # This prevents "kill" from matching in "used a skill"
            sorted_mappings = sorted(
                ItemModifierParser._RECENTLY_MAPPINGS.items(),
                key=lambda x: len(x[0]),
                reverse=True,
            )
            for key, context_key in sorted_mappings:
                if key in condition:
                    recently_condition = context_key
                    break

            matched_stat = ItemModifierParser._match_effect(
                effect, ItemModifierParser._EFFECT_MAPPINGS
            )
            if matched_stat:
                modifiers.append(  # pragma: no cover
                    modifier_class(
                        stat=matched_stat,
                        value=value,
                        mod_type=modifier_type.FLAT,
                        source=source,
                        conditions={"recently": recently_condition}
                        if recently_condition
                        else {},
                    )
                )
                return modifiers  # pragma: no cover

        # "X% chance to Y if you Z recently" pattern (alternative)
        match = ItemModifierParser.CHANCE_IF_RECENTLY_ALT_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            effect = match.group(2).strip().lower()
            condition = match.group(3).strip().lower()

            recently_condition = None
            # Sort by key length (longest first) to check more specific matches first
            # This prevents "kill" from matching in "used a skill"
            sorted_mappings = sorted(
                ItemModifierParser._RECENTLY_MAPPINGS.items(),
                key=lambda x: len(x[0]),
                reverse=True,
            )
            for key, context_key in sorted_mappings:
                if key in condition:
                    recently_condition = context_key
                    break

            matched_stat = ItemModifierParser._match_effect(
                effect, ItemModifierParser._EFFECT_MAPPINGS
            )
            if matched_stat:
                modifiers.append(  # pragma: no cover
                    modifier_class(
                        stat=matched_stat,
                        value=value,
                        mod_type=modifier_type.FLAT,
                        source=source,
                        conditions={"recently": recently_condition}
                        if recently_condition
                        else {},
                    )
                )
                return modifiers

        # "X% chance to Y on kill" pattern
        match = ItemModifierParser.CHANCE_ON_KILL_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            effect = match.group(2).strip().lower()

            matched_stat = ItemModifierParser._match_effect(
                effect, ItemModifierParser._EFFECT_MAPPINGS
            )
            if matched_stat:
                modifiers.append(  # pragma: no cover
                    modifier_class(
                        stat=matched_stat,
                        value=value,
                        mod_type=modifier_type.FLAT,
                        source=source,
                        conditions={"on": "kill"},
                    )
                )
                return modifiers  # pragma: no cover

        # "X% chance to Y on hit" pattern
        match = ItemModifierParser.CHANCE_ON_HIT_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            effect = match.group(2).strip().lower()

            matched_stat = ItemModifierParser._match_effect(
                effect, ItemModifierParser._EFFECT_MAPPINGS
            )
            if matched_stat:
                modifiers.append(  # pragma: no cover
                    modifier_class(
                        stat=matched_stat,
                        value=value,
                        mod_type=modifier_type.FLAT,
                        source=source,
                        conditions={"on": "hit"},
                    )
                )
                return modifiers  # pragma: no cover

        # "X% chance to Y on crit" pattern
        match = ItemModifierParser.CHANCE_ON_CRIT_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            effect = match.group(2).strip().lower()

            matched_stat = ItemModifierParser._match_effect(
                effect, ItemModifierParser._EFFECT_MAPPINGS
            )
            if matched_stat:
                modifiers.append(  # pragma: no cover
                    modifier_class(
                        stat=matched_stat,
                        value=value,
                        mod_type=modifier_type.FLAT,
                        source=source,
                        conditions={"on": "crit"},
                    )
                )
                return modifiers  # pragma: no cover

        # "X% chance to Y on block" pattern
        match = ItemModifierParser.CHANCE_ON_BLOCK_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            effect = match.group(2).strip().lower()

            matched_stat = ItemModifierParser._match_effect(
                effect, ItemModifierParser._EFFECT_MAPPINGS
            )
            if matched_stat:
                modifiers.append(  # pragma: no cover
                    modifier_class(
                        stat=matched_stat,
                        value=value,
                        mod_type=modifier_type.FLAT,
                        source=source,
                        conditions={"on": "block"},
                    )
                )
                return modifiers  # pragma: no cover

        # "X% chance to Y when hit" pattern
        match = ItemModifierParser.CHANCE_WHEN_HIT_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            effect = match.group(2).strip().lower()

            matched_stat = ItemModifierParser._match_effect(
                effect, ItemModifierParser._EFFECT_MAPPINGS
            )
            if matched_stat:
                modifiers.append(  # pragma: no cover
                    modifier_class(
                        stat=matched_stat,
                        value=value,
                        mod_type=modifier_type.FLAT,
                        source=source,
                        conditions={"when": "hit"},
                    )
                )
                return modifiers  # pragma: no cover

        # "X% chance to Y when you kill" pattern
        match = ItemModifierParser.CHANCE_WHEN_KILL_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            effect = match.group(2).strip().lower()

            matched_stat = ItemModifierParser._match_effect(
                effect, ItemModifierParser._EFFECT_MAPPINGS
            )
            if matched_stat:
                modifiers.append(  # pragma: no cover
                    modifier_class(
                        stat=matched_stat,
                        value=value,
                        mod_type=modifier_type.FLAT,
                        source=source,
                        conditions={"when": "kill"},
                    )
                )
                return modifiers  # pragma: no cover

        # "X% chance to Y when you use a skill" pattern
        match = ItemModifierParser.CHANCE_WHEN_USE_SKILL_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            effect = match.group(2).strip().lower()

            matched_stat = ItemModifierParser._match_effect(
                effect, ItemModifierParser._EFFECT_MAPPINGS
            )
            if matched_stat:
                modifiers.append(  # pragma: no cover
                    modifier_class(
                        stat=matched_stat,
                        value=value,
                        mod_type=modifier_type.FLAT,
                        source=source,
                        conditions={"when": "use_skill"},
                    )
                )
                return modifiers  # pragma: no cover

        # "X% chance to Y when you take damage" pattern
        match = ItemModifierParser.CHANCE_WHEN_TAKE_DAMAGE_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            effect = match.group(2).strip().lower()

            matched_stat = ItemModifierParser._match_effect(
                effect, ItemModifierParser._EFFECT_MAPPINGS
            )
            if matched_stat:
                modifiers.append(  # pragma: no cover
                    modifier_class(
                        stat=matched_stat,
                        value=value,
                        mod_type=modifier_type.FLAT,
                        source=source,
                        conditions={"when": "take_damage"},
                    )
                )
                return modifiers  # pragma: no cover

        # "X% chance to Y when you block" pattern
        match = ItemModifierParser.CHANCE_WHEN_BLOCK_PATTERN.match(line)
        if match:
            value = float(match.group(1))
            effect = match.group(2).strip().lower()

            matched_stat = ItemModifierParser._match_effect(
                effect, ItemModifierParser._EFFECT_MAPPINGS
            )
            if matched_stat:
                modifiers.append(  # pragma: no cover
                    modifier_class(
                        stat=matched_stat,
                        value=value,
                        mod_type=modifier_type.FLAT,
                        source=source,
                        conditions={"when": "block"},
                    )
                )
                return modifiers  # pragma: no cover

        # Veiled modifier pattern - extract the actual modifier
        match = ItemModifierParser.VEILED_PATTERN.match(line)
        if match:
            # Parse the inner modifier (remove veiled prefix)
            inner_mod = match.group(1).strip()
            inner_modifiers = ItemModifierParser.parse_line(
                inner_mod, source=f"{source}:veiled"
            )
            modifiers.extend(inner_modifiers)
            return modifiers

        # Corrupted modifier pattern - extract the actual modifier
        match = ItemModifierParser.CORRUPTED_PATTERN.match(line)
        if match:
            # Parse the inner modifier (remove corrupted prefix)
            inner_mod = match.group(1).strip()
            inner_modifiers = ItemModifierParser.parse_line(
                inner_mod, source=f"{source}:corrupted"
            )
            modifiers.extend(inner_modifiers)
            return modifiers

        # "X to Y" pattern (without +) - try as flat modifier
        match = ItemModifierParser.FLAT_NO_PLUS_PATTERN.match(line)
        if match:
            # Only match if it's not already matched by BASE_DAMAGE_PATTERN
            if not ItemModifierParser.BASE_DAMAGE_PATTERN.match(line):
                value = float(match.group(1))
                stat_name = ItemModifierParser._normalize_stat_name(match.group(2))
                modifiers.append(
                    modifier_class(
                        stat=stat_name,
                        value=value,
                        mod_type=modifier_type.FLAT,
                        source=source,
                    )
                )
                return modifiers

        # If no pattern matches, return empty list
        # (line might be flavor text, item name, etc.)
        return modifiers

    @staticmethod
    def parse_item_text(
        item_text: str, source: str = "item", skip_unique_parsing: bool = False
    ) -> list:
        """Parse full item text and extract all modifiers.

        :param item_text: Full item text (multiline string).
        :param source: Source identifier for modifiers.
        :param skip_unique_parsing: If True, skip parsing unique item effects
            to avoid recursion.
        :return: List of all Modifier objects found in the text.
        """
        modifier_class, modifier_type = _get_modifier_types()
        modifiers: list = []

        # Check if this is a unique item
        is_unique = "RARITY: UNIQUE" in item_text.upper()

        # Extract item name for unique items
        item_name = None
        if is_unique:
            lines = item_text.split("\n")
            # Try to extract unique item name (usually on line 1 or 2)
            for i, line in enumerate(lines[:3]):
                line_stripped = line.strip()
                if line_stripped and "Rarity:" not in line_stripped:
                    item_name = line_stripped
                    break

        # Parse each line for modifiers
        lines = item_text.split("\n")
        for line in lines:
            line_mods = ItemModifierParser.parse_line(line, source)
            modifiers.extend(line_mods)

        # If unique item, also parse unique effects
        # But only if not skipping to avoid recursion
        if is_unique and item_name and not skip_unique_parsing:
            from pobapi.calculator.unique_item_parser import UniqueItemParser

            # Pass skip_regular_parsing=True to avoid recursion
            # Regular modifiers are already parsed above, so we only need unique effects
            unique_modifiers = UniqueItemParser.parse_unique_item(
                item_name, item_text, skip_regular_parsing=True
            )
            modifiers.extend(unique_modifiers)

        return modifiers

    @staticmethod
    def _match_effect(effect: str, effect_mappings: dict[str, str]) -> str | None:
        """Match effect against mappings, handling both 'freeze' and
        'to freeze' formats.

        :param effect: Effect string to match (e.g., 'freeze' or 'to freeze').
        :param effect_mappings: Dictionary mapping effect keys to stat names.
        :return: Stat name if match found, None otherwise.
        """
        # First try direct match
        if effect in effect_mappings:
            return effect_mappings[effect]

        # Try with 'to ' prefix
        effect_with_to = f"to {effect}"
        if effect_with_to in effect_mappings:
            return effect_mappings[effect_with_to]  # pragma: no cover

        # Try checking if any mapping key is in the effect
        for key, stat in effect_mappings.items():
            if key in effect or effect in key:
                return stat

        return None

    @staticmethod
    def _normalize_stat_name(stat_text: str) -> str:
        """Normalize stat name from item text to internal stat name.

        :param stat_text: Stat name from item text.
        :return: Normalized stat name.
        """
        # Convert to lowercase and replace spaces with underscores
        normalized = stat_text.lower().strip()

        # Common mappings
        mappings = {
            "maximum life": "Life",
            "maximum mana": "Mana",
            "maximum energy shield": "EnergyShield",
            "armour": "Armour",
            "evasion rating": "Evasion",
            "fire resistance": "FireResistance",
            "cold resistance": "ColdResistance",
            "lightning resistance": "LightningResistance",
            "chaos resistance": "ChaosResistance",
            "attack speed": "AttackSpeed",
            "cast speed": "CastSpeed",
            "critical strike chance": "CritChance",
            "critical strike multiplier": "CritMultiplier",
            "accuracy rating": "Accuracy",
            "chance to hit": "HitChance",
            "physical damage": "PhysicalDamage",
            "fire damage": "FireDamage",
            "cold damage": "ColdDamage",
            "lightning damage": "LightningDamage",
            "chaos damage": "ChaosDamage",
            "block chance": "BlockChance",
            "spell block chance": "SpellBlockChance",
            "spell suppression chance": "SpellSuppressionChance",
            "strength": "Strength",
            "dexterity": "Dexterity",
            "intelligence": "Intelligence",
        }

        # Check for exact match
        if normalized in mappings:
            return mappings[normalized]

        # Try partial matching
        for key, value in mappings.items():
            if key in normalized or normalized in key:
                return value

        # Default: capitalize and remove spaces
        return "".join(word.capitalize() for word in normalized.split())

    @staticmethod
    def _normalize_damage_stat(damage_type: str, prefix: str = "") -> str:
        """Normalize damage type to stat name.

        :param damage_type: Damage type (e.g., "Physical", "Fire").
        :param prefix: Prefix for stat name (e.g., "Added", "Base").
        :return: Normalized stat name.
        """
        damage_type = damage_type.strip().lower()

        type_mapping = {
            "physical": "Physical",
            "fire": "Fire",
            "cold": "Cold",
            "lightning": "Lightning",
            "chaos": "Chaos",
        }

        normalized_type = type_mapping.get(damage_type, damage_type.capitalize())

        if prefix:
            return f"{prefix}{normalized_type}Damage"
        return f"{normalized_type}Damage"

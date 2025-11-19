"""Parser for extracting modifiers from skills and support gems.

This module parses skill gems and their support interactions,
replicating Path of Building's skill modifier parsing system.
"""

from typing import Any

from pobapi.calculator.modifiers import Modifier, ModifierType

__all__ = ["SkillModifierParser"]


class SkillModifierParser:
    """Parser for extracting modifiers from skills and support gems.

    This class processes skill gems and converts them to Modifier objects.
    Skills can have base damage, support gems can modify skills, etc.
    """

    @staticmethod
    def parse_skill_gem(
        gem_name: str, gem_level: int, gem_quality: int = 0
    ) -> list[Modifier]:
        """Parse a skill gem and extract its modifiers.

        :param gem_name: Name of the skill gem.
        :param gem_level: Level of the skill gem.
        :param gem_quality: Quality of the skill gem.
        :return: List of Modifier objects from the skill gem.
        """
        modifiers: list[Modifier] = []

        # This is a placeholder - full implementation would:
        # 1. Load skill gem data from game files
        # 2. Calculate base damage based on gem level
        # 3. Apply quality bonuses
        # 4. Extract skill-specific modifiers

        # Example structure (would come from game data):
        # skill_data = {
        #     "baseDamage": {"physical": [10, 15], "fire": [5, 10]},
        #     "damageEffectiveness": 100,
        #     "castTime": 0.75,
        #     "qualityStats": ["+1% increased Area of Effect"]
        # }

        # For now, return empty list
        # Full implementation would parse skill data and create modifiers

        return modifiers

    @staticmethod
    def parse_support_gem(
        gem_name: str,
        gem_level: int,
        gem_quality: int = 0,
        supported_skill: str | None = None,
    ) -> list[Modifier]:
        """Parse a support gem and extract its modifiers.

        :param gem_name: Name of the support gem.
        :param gem_level: Level of the support gem.
        :param gem_quality: Quality of the support gem.
        :param supported_skill: Name of the skill being supported.
        :return: List of Modifier objects from the support gem.
        """
        modifiers: list[Modifier] = []

        # This is a placeholder - full implementation would:
        # 1. Load support gem data from game files
        # 2. Calculate support multipliers based on gem level
        # 3. Apply quality bonuses
        # 4. Create modifiers that affect the supported skill

        # Support gem effects (simplified -
        # full implementation would load from game data)
        # Values are approximate for level 20 gems
        support_effects: dict[str, dict[str, Any]] = {
            "Added Fire Damage Support": {
                "moreFireDamage": 39.0 + (gem_level - 1) * 1.5,
                "physicalToFire": 50.0,
            },
            "Increased Area of Effect Support": {
                "moreAreaOfEffect": 49.0 + (gem_level - 1) * 1.5,
            },
            "Elemental Focus Support": {
                "moreElementalDamage": 49.0 + (gem_level - 1) * 1.5,
                "cannotIgnite": True,
                "cannotFreeze": True,
                "cannotShock": True,
            },
            "Controlled Destruction Support": {
                "moreSpellDamage": 39.0 + (gem_level - 1) * 1.5,
                "critChance": -100.0,
            },
            "Elemental Damage with Attacks Support": {
                "moreElementalDamage": 39.0 + (gem_level - 1) * 1.5,
            },
            "Melee Physical Damage Support": {
                "morePhysicalDamage": 49.0 + (gem_level - 1) * 1.5,
            },
            "Physical Projectile Attack Damage Support": {
                "morePhysicalDamage": 49.0 + (gem_level - 1) * 1.5,
            },
            "Brutality Support": {
                "morePhysicalDamage": 49.0 + (gem_level - 1) * 1.5,
                "elementalDamage": 0.0,  # No elemental damage
                "chaosDamage": 0.0,  # No chaos damage
            },
            "Ruthless Support": {
                "moreMeleeDamage": 39.0 + (gem_level - 1) * 1.5,
                "ruthlessChance": 30.0,
            },
            "Multistrike Support": {
                "moreAttackSpeed": 44.0 + (gem_level - 1) * 1.5,
                "lessDamage": -36.0 - (gem_level - 1) * 1.0,
            },
            "Spell Echo Support": {
                "moreCastSpeed": 70.0 + (gem_level - 1) * 2.0,
                "lessDamage": -10.0,
            },
            "Greater Multiple Projectiles Support": {
                "moreProjectiles": 4.0,
                "lessDamage": -26.0 - (gem_level - 1) * 1.0,
            },
            "Lesser Multiple Projectiles Support": {
                "moreProjectiles": 2.0,
                "lessDamage": -21.0 - (gem_level - 1) * 1.0,
            },
            "Faster Attacks Support": {
                "moreAttackSpeed": 44.0 + (gem_level - 1) * 1.5,
            },
            "Faster Casting Support": {
                "moreCastSpeed": 49.0 + (gem_level - 1) * 1.5,
            },
            "Increased Critical Strikes Support": {
                "critChance": 100.0 + (gem_level - 1) * 5.0,
            },
            "Increased Critical Damage Support": {
                "critMultiplier": 30.0 + (gem_level - 1) * 1.5,
            },
            "Deadly Ailments Support": {
                "moreAilmentDamage": 39.0 + (gem_level - 1) * 1.5,
                "lessHitDamage": -30.0 - (gem_level - 1) * 1.0,
            },
            "Unbound Ailments Support": {
                "moreAilmentDuration": 49.0 + (gem_level - 1) * 1.5,
            },
            "Vicious Projectiles Support": {
                "morePhysicalDamage": 39.0 + (gem_level - 1) * 1.5,
                "moreProjectileDamage": 39.0 + (gem_level - 1) * 1.5,
            },
            "Maim Support": {
                "morePhysicalDamage": 30.0 + (gem_level - 1) * 1.0,
                "maimChance": 30.0,
            },
            "Hypothermia Support": {
                "moreColdDamage": 39.0 + (gem_level - 1) * 1.5,
                "moreDamageAgainstChilled": 30.0 + (gem_level - 1) * 1.0,
            },
            "Immolate Support": {
                "moreFireDamage": 39.0 + (gem_level - 1) * 1.5,
                "moreDamageAgainstBurning": 30.0 + (gem_level - 1) * 1.0,
            },
            "Shock Support": {
                "moreLightningDamage": 39.0 + (gem_level - 1) * 1.5,
                "moreDamageAgainstShocked": 30.0 + (gem_level - 1) * 1.0,
            },
            "Inspiration Support": {
                "moreElementalDamage": 30.0 + (gem_level - 1) * 1.0,
                "lessManaCost": -25.0 - (gem_level - 1) * 1.0,
            },
            "Infused Channelling Support": {
                "moreDamage": 39.0 + (gem_level - 1) * 1.5,
                "lessDamageTaken": 8.0 + (gem_level - 1) * 0.2,
            },
            "Concentrated Effect Support": {
                "moreAreaDamage": 59.0 + (gem_level - 1) * 1.5,
                "lessAreaOfEffect": -30.0 - (gem_level - 1) * 1.0,
            },
            "Intensify Support": {
                "moreSpellDamage": 30.0 + (gem_level - 1) * 1.0,
                "lessAreaOfEffect": -10.0 - (gem_level - 1) * 0.5,
            },
            "Awakened Added Fire Damage Support": {
                "moreFireDamage": 44.0 + (gem_level - 1) * 1.5,
                "physicalToFire": 50.0,
            },
            "Awakened Elemental Focus Support": {
                "moreElementalDamage": 54.0 + (gem_level - 1) * 1.5,
                "cannotIgnite": True,
                "cannotFreeze": True,
                "cannotShock": True,
            },
        }

        if gem_name in support_effects:
            effects = support_effects[gem_name]
            for stat, value in effects.items():
                if isinstance(value, bool):
                    # Boolean flag
                    modifiers.append(
                        Modifier(
                            stat=stat,
                            value=1.0 if value else 0.0,
                            mod_type=ModifierType.FLAG,
                            source=f"support:{gem_name}",
                        )
                    )
                elif isinstance(value, int | float):
                    # Determine modifier type based on stat name
                    if "more" in stat.lower() or "less" in stat.lower():
                        mod_type = (
                            ModifierType.MORE
                            if "more" in stat.lower()
                            else ModifierType.LESS
                        )
                    elif "increased" in stat.lower() or "reduced" in stat.lower():
                        mod_type = (  # pragma: no cover
                            ModifierType.INCREASED
                            if "increased" in stat.lower()
                            else ModifierType.REDUCED
                        )
                    elif stat.startswith("crit") or stat.startswith("Crit"):
                        mod_type = ModifierType.INCREASED
                    elif stat.endswith("Chance") or stat.endswith("Chance"):
                        mod_type = ModifierType.FLAT
                    else:
                        # Default to MORE for damage multipliers
                        mod_type = ModifierType.MORE

                    modifiers.append(
                        Modifier(
                            stat=stat,
                            value=value,
                            mod_type=mod_type,
                            source=f"support:{gem_name}",
                        )
                    )

        # Apply quality bonuses (simplified - 1% per quality)
        if gem_quality > 0:
            # Quality bonuses vary by gem, but many give 1% per quality
            # This is a simplified implementation
            pass

        return modifiers

    @staticmethod
    def parse_skill_group(skill_group: Any) -> list[Modifier]:
        """Parse a skill group (socket group) and extract all modifiers.

        :param skill_group: SkillGroup object containing gems.
        :return: List of all Modifier objects from the skill group.
        """
        modifiers: list[Modifier] = []

        try:
            # Get active skill (main skill)
            active_skill_index = skill_group.active
            if active_skill_index is not None and skill_group.abilities:
                active_skill = skill_group.abilities[active_skill_index - 1]
                if active_skill:
                    # Parse active skill gem
                    skill_mods = SkillModifierParser.parse_skill_gem(
                        active_skill.name,
                        active_skill.level,
                        getattr(active_skill, "quality", 0),
                    )
                    modifiers.extend(skill_mods)

            # Parse support gems
            for ability in skill_group.abilities:
                if hasattr(ability, "support") and ability.support:
                    support_mods = SkillModifierParser.parse_support_gem(
                        ability.name,
                        ability.level,
                        getattr(ability, "quality", 0),
                    )
                    modifiers.extend(support_mods)
        except (AttributeError, IndexError):
            # If skill_group doesn't have expected structure, skip
            pass

        return modifiers

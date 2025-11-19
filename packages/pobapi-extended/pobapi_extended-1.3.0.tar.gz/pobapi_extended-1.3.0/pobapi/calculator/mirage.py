"""Mirage calculations for Path of Building.

This module handles mirage skills that use player skills:
- Mirage Archer
- The Saviour (Mirage Warriors)
- Tawhoa's Chosen
- Sacred Wisps
- General's Cry
"""

from dataclasses import dataclass
from typing import Any

from pobapi.calculator.damage import DamageBreakdown, DamageCalculator
from pobapi.calculator.modifiers import ModifierSystem

__all__ = ["MirageStats", "MirageCalculator"]


@dataclass
class MirageStats:
    """Stats for a mirage skill.

    :param name: Mirage skill name.
    :param count: Number of mirages.
    :param damage_multiplier: Damage multiplier for mirages.
    :param speed_multiplier: Speed multiplier for mirages.
    :param dps: DPS from mirages.
    :param breakdown: Damage breakdown from mirages.
    """

    name: str
    count: int = 1
    damage_multiplier: float = 1.0
    speed_multiplier: float = 1.0
    dps: float = 0.0
    breakdown: DamageBreakdown | None = None


class MirageCalculator:
    """Calculator for mirage skills.

    Handles calculations for skills that create mirages:
    - Mirage Archer
    - The Saviour
    - Tawhoa's Chosen
    - Sacred Wisps
    - General's Cry
    """

    def __init__(self, modifiers: ModifierSystem, damage_calc: DamageCalculator):
        """Initialize mirage calculator.

        :param modifiers: Modifier system.
        :param damage_calc: Damage calculator.
        """
        self.modifiers = modifiers
        self.damage_calc = damage_calc

    def calculate_mirage_archer(
        self, skill_name: str, context: dict[str, Any] | None = None
    ) -> MirageStats | None:
        """Calculate Mirage Archer stats.

        Mirage Archer creates mirages that use the player's active skill.
        - Less damage modifier
        - Less attack speed modifier
        - Max count modifier

        :param skill_name: Active skill name.
        :param context: Calculation context.
        :return: MirageStats or None if not applicable.
        """
        if context is None:
            context = {}

        # Check if skill is triggered by Mirage Archer
        triggered_by_mirage_archer = context.get("triggeredByMirageArcher", False)
        if not triggered_by_mirage_archer:
            return None

        # Get Mirage Archer modifiers
        less_damage = self.modifiers.calculate_stat(
            "MirageArcherLessDamage", 0.0, context
        )
        less_attack_speed = self.modifiers.calculate_stat(
            "MirageArcherLessAttackSpeed", 0.0, context
        )
        max_count = self.modifiers.calculate_stat("MirageArcherMaxCount", 1.0, context)

        # Calculate multipliers (less = negative more)
        damage_multiplier = 1.0 + (less_damage / 100.0)
        speed_multiplier = 1.0 + (less_attack_speed / 100.0)

        # Calculate mirage DPS
        base_dps, _, _ = self.damage_calc.calculate_total_dps_with_dot(
            skill_name, context
        )
        mirage_dps = base_dps * damage_multiplier * speed_multiplier * max_count

        # Get damage breakdown
        breakdown = self.damage_calc.calculate_damage_against_enemy(skill_name, context)
        if breakdown:
            breakdown.physical *= damage_multiplier
            breakdown.fire *= damage_multiplier
            breakdown.cold *= damage_multiplier
            breakdown.lightning *= damage_multiplier
            breakdown.chaos *= damage_multiplier

        return MirageStats(
            name=f"{max_count:.0f} Mirage Archers using {skill_name}",
            count=int(max_count),
            damage_multiplier=damage_multiplier,
            speed_multiplier=speed_multiplier,
            dps=mirage_dps,
            breakdown=breakdown,
        )

    def calculate_saviour(
        self, skill_name: str, context: dict[str, Any] | None = None
    ) -> MirageStats | None:
        """Calculate The Saviour (Mirage Warriors) stats.

        The Saviour creates mirage warriors that use the best sword attack skill.
        - Less damage modifier
        - Max count modifier (halved if dual wielding same weapon)

        :param skill_name: Active skill name (should be "Reflection").
        :param context: Calculation context.
        :return: MirageStats or None if not applicable.
        """
        if context is None:
            context = {}

        # Check if skill is Reflection (The Saviour)
        if skill_name != "Reflection":
            return None

        # Get Saviour modifiers
        less_damage = self.modifiers.calculate_stat(
            "SaviourMirageWarriorLessDamage", 0.0, context
        )
        max_count = self.modifiers.calculate_stat(
            "SaviourMirageWarriorMaxCount", 2.0, context
        )

        # Check if dual wielding same weapon (halves count)
        dual_wield_same = context.get("dualWieldSameWeapon", False)
        if dual_wield_same:
            max_count = max_count / 2.0

        # Calculate multipliers
        damage_multiplier = 1.0 + (less_damage / 100.0)

        # Find best sword attack skill (simplified - would need to check all skills)
        # For now, use the provided skill_name or find best DPS sword attack
        best_skill = context.get("bestSwordAttackSkill", skill_name)

        # Calculate mirage DPS
        base_dps, _, _ = self.damage_calc.calculate_total_dps_with_dot(
            best_skill, context
        )
        mirage_dps = base_dps * damage_multiplier * max_count

        # Get damage breakdown
        breakdown = self.damage_calc.calculate_damage_against_enemy(best_skill, context)
        if breakdown:
            breakdown.physical *= damage_multiplier
            breakdown.fire *= damage_multiplier
            breakdown.cold *= damage_multiplier
            breakdown.lightning *= damage_multiplier
            breakdown.chaos *= damage_multiplier

        return MirageStats(
            name=f"{max_count:.0f} Mirage Warriors using {best_skill}",
            count=int(max_count),
            damage_multiplier=damage_multiplier,
            speed_multiplier=1.0,
            dps=mirage_dps,
            breakdown=breakdown,
        )

    def calculate_tawhoas_chosen(
        self, skill_name: str, context: dict[str, Any] | None = None
    ) -> MirageStats | None:
        """Calculate Tawhoa's Chosen stats.

        Tawhoa's Chosen creates a mirage that uses the best slam/melee attack.
        - More damage modifier
        - Cooldown-based trigger rate

        :param skill_name: Active skill name (should be "Tawhoa's Chosen").
        :param context: Calculation context.
        :return: MirageStats or None if not applicable.
        """
        if context is None:
            context = {}

        # Check if skill is Tawhoa's Chosen
        if skill_name != "Tawhoa's Chosen":
            return None

        # Get Tawhoa's Chosen modifiers
        more_damage = self.modifiers.calculate_stat(
            "ChieftainMirageChieftainMoreDamage", 0.0, context
        )

        # Calculate multipliers
        damage_multiplier = 1.0 + (more_damage / 100.0)

        # Find best slam/melee attack skill (simplified)
        best_skill = context.get("bestSlamMeleeAttackSkill", skill_name)

        # Calculate trigger rate from cooldowns
        trigger_cooldown = context.get("tawhoasChosenCooldown", 4.0)
        skill_cooldown = context.get("triggeredSkillCooldown", 0.0)
        cooldown_recovery = (
            self.modifiers.calculate_stat("CooldownRecovery", 100.0, context) / 100.0
        )

        # Calculate effective cooldown
        trigger_cd_adjusted = trigger_cooldown / cooldown_recovery
        skill_cd_adjusted = (
            skill_cooldown / cooldown_recovery if skill_cooldown > 0 else 0.0
        )
        action_cooldown = max(trigger_cd_adjusted, skill_cd_adjusted)

        # Calculate trigger rate
        trigger_rate = 1.0 / action_cooldown if action_cooldown > 0 else 0.0

        # Calculate mirage DPS
        base_dps, _, _ = self.damage_calc.calculate_total_dps_with_dot(
            best_skill, context
        )
        # Use trigger rate instead of attack speed
        mirage_dps = base_dps * damage_multiplier * trigger_rate

        # Get damage breakdown
        breakdown = self.damage_calc.calculate_damage_against_enemy(best_skill, context)
        if breakdown:
            breakdown.physical *= damage_multiplier
            breakdown.fire *= damage_multiplier
            breakdown.cold *= damage_multiplier
            breakdown.lightning *= damage_multiplier
            breakdown.chaos *= damage_multiplier

        return MirageStats(
            name=f"Tawhoa's Chosen using {best_skill}",
            count=1,
            damage_multiplier=damage_multiplier,
            speed_multiplier=trigger_rate,
            dps=mirage_dps,
            breakdown=breakdown,
        )

    def calculate_sacred_wisps(
        self, skill_name: str, context: dict[str, Any] | None = None
    ) -> MirageStats | None:
        """Calculate Sacred Wisps stats.

        Sacred Wisps create wisps that use the player's active skill.
        - Less damage modifier
        - Cast chance modifier (affects speed)
        - Max count modifier

        :param skill_name: Active skill name.
        :param context: Calculation context.
        :return: MirageStats or None if not applicable.
        """
        if context is None:
            context = {}

        # Check if skill is triggered by Sacred Wisps
        triggered_by_wisps = context.get("triggeredBySacredWisps", False)
        if not triggered_by_wisps:
            return None

        # Get Sacred Wisps modifiers
        less_damage = self.modifiers.calculate_stat(
            "SacredWispsLessDamage", 0.0, context
        )
        cast_chance = self.modifiers.calculate_stat("SacredWispsChance", 100.0, context)
        max_count = self.modifiers.calculate_stat("SacredWispsMaxCount", 1.0, context)

        # Calculate multipliers
        damage_multiplier = 1.0 + (less_damage / 100.0)
        speed_multiplier = cast_chance / 100.0  # Cast chance affects speed

        # Calculate mirage DPS
        base_dps, _, _ = self.damage_calc.calculate_total_dps_with_dot(
            skill_name, context
        )
        mirage_dps = base_dps * damage_multiplier * speed_multiplier * max_count

        # Get damage breakdown
        breakdown = self.damage_calc.calculate_damage_against_enemy(skill_name, context)
        if breakdown:
            breakdown.physical *= damage_multiplier
            breakdown.fire *= damage_multiplier
            breakdown.cold *= damage_multiplier
            breakdown.lightning *= damage_multiplier
            breakdown.chaos *= damage_multiplier

        return MirageStats(
            name=f"{max_count:.0f} Sacred Wisps using {skill_name}",
            count=int(max_count),
            damage_multiplier=damage_multiplier,
            speed_multiplier=speed_multiplier,
            dps=mirage_dps,
            breakdown=breakdown,
        )

    def calculate_generals_cry(
        self, skill_name: str, context: dict[str, Any] | None = None
    ) -> MirageStats | None:
        """Calculate General's Cry stats.

        General's Cry creates mirages that use exerted attacks.
        - Cooldown-based spawn rate
        - Max count modifier
        - Exert modifiers apply

        :param skill_name: Active skill name.
        :param context: Calculation context.
        :return: MirageStats or None if not applicable.
        """
        if context is None:
            context = {}

        # Check if skill is triggered by General's Cry
        triggered_by_gc = context.get("triggeredByGeneralsCry", False)
        if not triggered_by_gc:
            return None

        # Get General's Cry modifiers
        max_count = self.modifiers.calculate_stat(
            "GeneralsCryDoubleMaxCount", 0.0, context
        )
        cooldown = context.get("generalsCryCooldown", 1.0)

        # Calculate spawn time (0.3s for first, 0.2s for each extra)
        spawn_time = 0.3 + 0.2 * max_count

        # Add skill hit time if not channeling
        is_channeling = context.get("isChanneling", False)
        if not is_channeling:
            hit_time = context.get("hitTime", 0.0) or context.get("time", 0.0)
            spawn_time += hit_time

        # Scale cooldown to have maximum mirages at once
        effective_cooldown = max(cooldown, spawn_time)

        # Calculate DPS multiplier from cooldown
        dps_multiplier = 1.0 / effective_cooldown if effective_cooldown > 0 else 0.0

        # Calculate mirage DPS
        base_dps, _, _ = self.damage_calc.calculate_total_dps_with_dot(
            skill_name, context
        )
        mirage_dps = base_dps * dps_multiplier * max_count

        # Get damage breakdown
        breakdown = self.damage_calc.calculate_damage_against_enemy(skill_name, context)
        # Exert modifiers are already applied in context

        return MirageStats(
            name=f"{max_count:.0f} GC Mirages using {skill_name}",
            count=int(max_count),
            damage_multiplier=1.0,
            speed_multiplier=dps_multiplier,
            dps=mirage_dps,
            breakdown=breakdown,
        )

    def calculate_all_mirages(
        self, skill_name: str, context: dict[str, Any] | None = None
    ) -> list[MirageStats]:
        """Calculate all applicable mirage stats.

        :param skill_name: Active skill name.
        :param context: Calculation context.
        :return: List of MirageStats.
        """
        if context is None:
            context = {}

        mirages: list[MirageStats] = []

        # Check each mirage type
        mirage_archer = self.calculate_mirage_archer(skill_name, context)
        if mirage_archer:
            mirages.append(mirage_archer)

        saviour = self.calculate_saviour(skill_name, context)
        if saviour:
            mirages.append(saviour)

        tawhoas = self.calculate_tawhoas_chosen(skill_name, context)
        if tawhoas:
            mirages.append(tawhoas)

        wisps = self.calculate_sacred_wisps(skill_name, context)
        if wisps:
            mirages.append(wisps)

        generals_cry = self.calculate_generals_cry(skill_name, context)
        if generals_cry:
            mirages.append(generals_cry)

        return mirages

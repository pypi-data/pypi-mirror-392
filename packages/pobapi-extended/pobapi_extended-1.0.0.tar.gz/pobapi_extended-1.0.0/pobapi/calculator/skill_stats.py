"""Skill-specific stat calculations for Path of Building.

This module handles skill-specific calculations including:
- Area of Effect (AoE)
- Projectile count and speed
- Cooldown calculations
- Skill-specific modifiers
"""

from typing import Any

from pobapi.calculator.modifiers import ModifierSystem

__all__ = ["SkillStatsCalculator"]


class SkillStatsCalculator:
    """Calculator for skill-specific stats.

    This class replicates Path of Building's skill stat calculation system.
    """

    def __init__(self, modifier_system: ModifierSystem):
        """Initialize skill stats calculator.

        :param modifier_system: Modifier system to use for calculations.
        """
        self.modifiers = modifier_system

    def calculate_area_of_effect_radius(
        self,
        skill_name: str,
        base_radius: float = 0.0,
        context: dict[str, Any] | None = None,
    ) -> float:
        """Calculate area of effect radius.

        :param skill_name: Name of the skill.
        :param base_radius: Base AoE radius.
        :param context: Current calculation context.
        :return: Area of effect radius.
        """
        if context is None:
            context = {}

        # Get AoE modifiers
        aoe_mult = self.modifiers.calculate_stat("AreaOfEffect", 100.0, context) / 100.0

        # AoE radius scales with square root of AoE multiplier
        # If AoE is doubled (200%), radius increases by sqrt(2) ≈ 1.414
        radius_mult = aoe_mult**0.5

        return float(base_radius * radius_mult)

    def calculate_projectile_count(
        self,
        skill_name: str,
        base_count: int = 1,
        context: dict[str, Any] | None = None,
    ) -> int:
        """Calculate projectile count.

        :param skill_name: Name of the skill.
        :param base_count: Base projectile count.
        :param context: Current calculation context.
        :return: Total projectile count.
        """
        if context is None:
            context = {}

        # Get additional projectiles
        additional_projectiles = self.modifiers.calculate_stat(
            "AdditionalProjectiles", 0.0, context
        )

        return base_count + int(additional_projectiles)

    def calculate_projectile_speed(
        self,
        skill_name: str,
        base_speed: float = 1.0,
        context: dict[str, Any] | None = None,
    ) -> float:
        """Calculate projectile speed.

        :param skill_name: Name of the skill.
        :param base_speed: Base projectile speed.
        :param context: Current calculation context.
        :return: Projectile speed.
        """
        if context is None:
            context = {}

        # Get projectile speed modifiers
        speed_mult = (
            self.modifiers.calculate_stat("ProjectileSpeed", 100.0, context) / 100.0
        )

        return base_speed * speed_mult

    def calculate_skill_cooldown(
        self,
        skill_name: str,
        base_cooldown: float = 0.0,
        context: dict[str, Any] | None = None,
    ) -> float:
        """Calculate skill cooldown.

        :param skill_name: Name of the skill.
        :param base_cooldown: Base cooldown time.
        :param context: Current calculation context.
        :return: Skill cooldown time.
        """
        if context is None:
            context = {}

        # Get cooldown recovery modifiers
        cooldown_recovery = (
            self.modifiers.calculate_stat("CooldownRecovery", 100.0, context) / 100.0
        )

        # Cooldown recovery is inverse of cooldown
        # 100% recovery = 50% cooldown time
        if cooldown_recovery > 0:
            cooldown = base_cooldown / cooldown_recovery
        else:
            cooldown = base_cooldown

        return cooldown

    def calculate_trap_cooldown(self, context: dict[str, Any] | None = None) -> float:
        """Calculate trap cooldown.

        :param context: Current calculation context.
        :return: Trap cooldown time.
        """
        if context is None:
            context = {}

        base_cooldown = 4.0  # Default trap cooldown
        return self.calculate_skill_cooldown("Trap", base_cooldown, context)

    def calculate_mine_cooldown(self, context: dict[str, Any] | None = None) -> float:
        """Calculate mine cooldown (laying time).

        :param context: Current calculation context.
        :return: Mine laying time.
        """
        if context is None:
            context = {}

        base_time = 0.3  # Default mine laying time
        speed_mult = (
            self.modifiers.calculate_stat("MineLayingSpeed", 100.0, context) / 100.0
        )

        return base_time / speed_mult

    def calculate_totem_placement_time(
        self, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate totem placement time.

        :param context: Current calculation context.
        :return: Totem placement time.
        """
        if context is None:
            context = {}

        base_time = 0.6  # Default totem placement time
        speed_mult = (
            self.modifiers.calculate_stat("TotemPlacementSpeed", 100.0, context) / 100.0
        )

        return base_time / speed_mult

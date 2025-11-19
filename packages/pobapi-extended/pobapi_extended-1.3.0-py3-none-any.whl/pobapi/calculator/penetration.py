"""Penetration and resistance reduction calculations.

This module handles penetration and resistance reduction mechanics,
which are important for damage calculations against enemies.
"""

from typing import Any

from pobapi.calculator.modifiers import ModifierSystem

__all__ = ["PenetrationCalculator"]


class PenetrationCalculator:
    """Calculator for penetration and resistance reduction.

    Penetration reduces enemy resistances, while resistance reduction
    is applied before penetration. Both affect final damage calculations.
    """

    def __init__(self, modifier_system: ModifierSystem):
        """Initialize penetration calculator.

        :param modifier_system: Modifier system to use for calculations.
        """
        self.modifiers = modifier_system

    def calculate_effective_resistance(
        self,
        base_resistance: float,
        resistance_reduction: float,
        penetration: float,
        context: dict[str, Any] | None = None,
    ) -> float:
        """Calculate effective enemy resistance after reduction and penetration.

        Order of operations:
        1. Apply resistance reduction (e.g., from curses)
        2. Apply penetration (e.g., from support gems, passives)

        :param base_resistance: Base enemy resistance (e.g., 75%).
        :param resistance_reduction: Resistance reduction (e.g., -44% from curse).
        :param penetration: Penetration (e.g., 37% from support gem).
        :param context: Current calculation context.
        :return: Effective resistance (0.0 to 1.0).
        """
        # Start with base resistance
        effective_res = base_resistance

        # Apply resistance reduction first
        effective_res += resistance_reduction

        # Apply penetration (penetration is subtracted)
        effective_res -= penetration

        # Resistance cannot go below -200% (hard cap in PoE)
        effective_res = max(effective_res, -200.0)

        # Convert to 0.0-1.0 range
        return effective_res / 100.0

    def calculate_fire_resistance(
        self, base_resistance: float, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate effective fire resistance.

        :param base_resistance: Base enemy fire resistance.
        :param context: Current calculation context.
        :return: Effective fire resistance (0.0 to 1.0).
        """
        if context is None:
            context = {}

        # Get resistance reduction (from curses, etc.)
        fire_res_reduction = self.modifiers.calculate_stat(
            "EnemyFireResistance", 0.0, context
        )

        # Get penetration
        fire_pen = self.modifiers.calculate_stat("FirePenetration", 0.0, context)

        return self.calculate_effective_resistance(
            base_resistance, fire_res_reduction, fire_pen, context
        )

    def calculate_cold_resistance(
        self, base_resistance: float, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate effective cold resistance.

        :param base_resistance: Base enemy cold resistance.
        :param context: Current calculation context.
        :return: Effective cold resistance (0.0 to 1.0).
        """
        if context is None:
            context = {}

        cold_res_reduction = self.modifiers.calculate_stat(
            "EnemyColdResistance", 0.0, context
        )
        cold_pen = self.modifiers.calculate_stat("ColdPenetration", 0.0, context)

        return self.calculate_effective_resistance(
            base_resistance, cold_res_reduction, cold_pen, context
        )

    def calculate_lightning_resistance(
        self, base_resistance: float, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate effective lightning resistance.

        :param base_resistance: Base enemy lightning resistance.
        :param context: Current calculation context.
        :return: Effective lightning resistance (0.0 to 1.0).
        """
        if context is None:
            context = {}

        lightning_res_reduction = self.modifiers.calculate_stat(
            "EnemyLightningResistance", 0.0, context
        )
        lightning_pen = self.modifiers.calculate_stat(
            "LightningPenetration", 0.0, context
        )

        return self.calculate_effective_resistance(
            base_resistance, lightning_res_reduction, lightning_pen, context
        )

    def calculate_chaos_resistance(
        self, base_resistance: float, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate effective chaos resistance.

        :param base_resistance: Base enemy chaos resistance.
        :param context: Current calculation context.
        :return: Effective chaos resistance (0.0 to 1.0).
        """
        if context is None:
            context = {}

        chaos_res_reduction = self.modifiers.calculate_stat(
            "EnemyChaosResistance", 0.0, context
        )
        chaos_pen = self.modifiers.calculate_stat("ChaosPenetration", 0.0, context)

        return self.calculate_effective_resistance(
            base_resistance, chaos_res_reduction, chaos_pen, context
        )

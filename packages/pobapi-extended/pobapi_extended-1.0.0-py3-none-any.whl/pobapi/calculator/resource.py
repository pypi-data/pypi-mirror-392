"""Resource calculation system for Path of Building.

This module handles resource-related calculations including:
- Mana cost and reservation
- Life/Mana/Energy Shield regeneration
- Leech calculations
- Net recovery calculations
"""

from typing import Any

from pobapi.calculator.modifiers import ModifierSystem

__all__ = ["ResourceCalculator"]


class ResourceCalculator:
    """Calculator for resource-related stats.

    This class replicates Path of Building's resource calculation system.
    """

    def __init__(self, modifier_system: ModifierSystem):
        """Initialize resource calculator.

        :param modifier_system: Modifier system to use for calculations.
        """
        self.modifiers = modifier_system

    def calculate_mana_cost(
        self, skill_name: str, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate mana cost for a skill.

        :param skill_name: Name of the skill.
        :param context: Current calculation context.
        :return: Mana cost per use.
        """
        if context is None:
            context = {}

        # Base mana cost from skill
        base_cost = self.modifiers.calculate_stat(f"{skill_name}ManaCost", 0.0, context)

        # Apply mana cost modifiers
        cost_mult = self.modifiers.calculate_stat("ManaCost", 100.0, context) / 100.0

        return base_cost * cost_mult

    def calculate_mana_cost_per_second(
        self, skill_name: str, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate mana cost per second for a skill.

        :param skill_name: Name of the skill.
        :param context: Current calculation context.
        :return: Mana cost per second.
        """
        if context is None:
            context = {}

        mana_cost = self.calculate_mana_cost(skill_name, context)

        # Get attack/cast speed
        if self.modifiers.get_modifiers(f"{skill_name}IsAttack", context):
            speed = self.modifiers.calculate_stat("AttackSpeed", 1.0, context)
        else:
            speed = self.modifiers.calculate_stat("CastSpeed", 1.0, context)

        return mana_cost * speed

    def calculate_life_reservation(
        self, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate total life reservation.

        :param context: Current calculation context.
        :return: Total life reserved.
        """
        if context is None:
            context = {}

        # Sum all life reservation modifiers
        total_reservation = self.modifiers.calculate_stat(
            "LifeReservation", 0.0, context
        )

        return total_reservation

    def calculate_mana_reservation(
        self, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate total mana reservation.

        :param context: Current calculation context.
        :return: Total mana reserved.
        """
        if context is None:
            context = {}

        # Sum all mana reservation modifiers
        total_reservation = self.modifiers.calculate_stat(
            "ManaReservation", 0.0, context
        )

        return total_reservation

    def calculate_unreserved_life(
        self, total_life: float, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate unreserved life.

        :param total_life: Total life.
        :param context: Current calculation context.
        :return: Unreserved life.
        """
        if context is None:
            context = {}

        reserved = self.calculate_life_reservation(context)
        unreserved = max(0.0, total_life - reserved)

        return unreserved

    def calculate_unreserved_mana(
        self, total_mana: float, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate unreserved mana.

        :param total_mana: Total mana.
        :param context: Current calculation context.
        :return: Unreserved mana.
        """
        if context is None:
            context = {}

        reserved = self.calculate_mana_reservation(context)
        unreserved = max(0.0, total_mana - reserved)

        return unreserved

    def calculate_net_life_recovery(
        self,
        life_regen: float,
        life_leech: float,
        total_degen: float,
        context: dict[str, Any] | None = None,
    ) -> float:
        """Calculate net life recovery (regen + leech - degen).

        :param life_regen: Life regeneration per second.
        :param life_leech: Life leech per second.
        :param total_degen: Total degeneration per second.
        :param context: Current calculation context.
        :return: Net life recovery per second.
        """
        return life_regen + life_leech - total_degen

    def calculate_net_mana_recovery(
        self,
        mana_regen: float,
        mana_leech: float,
        context: dict[str, Any] | None = None,
    ) -> float:
        """Calculate net mana recovery (regen + leech).

        :param mana_regen: Mana regeneration per second.
        :param mana_leech: Mana leech per second.
        :param context: Current calculation context.
        :return: Net mana recovery per second.
        """
        return mana_regen + mana_leech

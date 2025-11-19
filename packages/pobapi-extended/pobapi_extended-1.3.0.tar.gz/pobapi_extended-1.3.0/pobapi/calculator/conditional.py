"""Conditional modifier handling for Path of Building.

This module handles conditional modifiers that depend on game state,
such as "on full life", "on low life", "enemy is shocked", etc.
"""

from typing import Any

__all__ = ["ConditionEvaluator"]


class ConditionEvaluator:
    """Evaluates conditions for conditional modifiers.

    This class checks if conditions are met based on the current game state.
    """

    @staticmethod
    def evaluate_condition(condition: str, context: dict[str, Any]) -> bool:
        """
        Determine whether a named gameplay condition is satisfied using
        the provided context.

        Evaluates life, mana, and energy-shield thresholds (full = >=99%,
        low = <=35%) when current and max values are present; otherwise
        falls back to boolean flags in the context. Handles enemy status
        flags (e.g., "enemy_is_shocked") and the "projectile_distance"
        condition using context keys "projectile_distance" (default
        "medium") and "required_distance" (default "close"): required
        "close" matches "close" or "medium", "far" matches only "far",
        otherwise requires exact match. For any other condition name,
        returns the boolean value of the corresponding context entry.

        Parameters:
            condition (str): Name of the condition to evaluate (e.g.,
                "on_full_life", "enemy_is_frozen", "projectile_distance").
            context (dict[str, Any]): Runtime context containing current
                and maximum resource values and boolean flags used to
                evaluate conditions.

        Returns:
            bool: `True` if the specified condition is met, `False` otherwise.
        """
        # Get current life/mana/ES values
        current_life = context.get("current_life")
        max_life = context.get("max_life") or context.get("life")
        current_mana = context.get("current_mana")
        max_mana = context.get("max_mana") or context.get("mana")
        current_es = context.get("current_energy_shield")
        max_es = context.get("max_energy_shield") or context.get("energy_shield")

        # Life-based conditions
        if condition == "on_full_life" or condition == "OnFullLife":
            if max_life and current_life is not None:
                return bool(current_life >= max_life * 0.99)  # 99% threshold
            # If not specified, check flag
            return bool(context.get("on_full_life", False))

        if condition == "on_low_life" or condition == "OnLowLife":
            if max_life and current_life is not None:
                return bool(current_life <= max_life * 0.35)  # 35% threshold
            # If not specified, check flag
            return bool(context.get("on_low_life", False))

        # Mana-based conditions
        if condition == "on_full_mana" or condition == "OnFullMana":
            if max_mana and current_mana is not None:
                return bool(current_mana >= max_mana * 0.99)
            return bool(context.get("on_full_mana", False))

        if condition == "on_low_mana" or condition == "OnLowMana":
            if max_mana and current_mana is not None:
                return bool(current_mana <= max_mana * 0.35)
            return bool(context.get("on_low_mana", False))

        # Energy Shield conditions
        if condition == "on_full_energy_shield" or condition == "OnFullEnergyShield":
            if max_es and current_es is not None:
                return bool(current_es >= max_es * 0.99)
            return bool(context.get("on_full_energy_shield", False))

        if condition == "on_low_energy_shield" or condition == "OnLowEnergyShield":
            if max_es and current_es is not None:
                return bool(current_es <= max_es * 0.35)
            return bool(context.get("on_low_energy_shield", False))

        # Enemy conditions
        if condition == "enemy_is_shocked":
            return bool(context.get("enemy_is_shocked", False))

        if condition == "enemy_is_frozen":
            return bool(context.get("enemy_is_frozen", False))

        if condition == "enemy_is_ignited":
            return bool(context.get("enemy_is_ignited", False))

        if condition == "enemy_is_chilled":
            return bool(context.get("enemy_is_chilled", False))

        if condition == "enemy_is_poisoned":
            return bool(context.get("enemy_is_poisoned", False))

        # Distance conditions
        if condition == "projectile_distance":
            distance = context.get("projectile_distance", "medium")
            required = context.get("required_distance", "close")
            if required == "close":
                return bool(distance in ("close", "medium"))
            elif required == "far":
                return bool(distance == "far")
            return bool(distance == required)

        # Default: check if condition is set in context
        return bool(context.get(condition, False))

    @staticmethod
    def evaluate_all_conditions(
        conditions: dict[str, Any], context: dict[str, Any]
    ) -> bool:
        """
        Determine whether every condition in the provided mapping is
        satisfied by the given context.

        Parameters:
            conditions (dict[str, Any]): Mapping of condition names to
                required values. All conditions must evaluate to True for
                the function to return True.
            context (dict[str, Any]): Evaluation context containing
                current state (e.g., life, mana, energy shield, enemy
                flags, distance).

        Returns:
            bool: `True` if all conditions are satisfied, `False` otherwise.
        """
        for condition, required_value in conditions.items():
            if not ConditionEvaluator.evaluate_condition(condition, context):
                return False
        return True

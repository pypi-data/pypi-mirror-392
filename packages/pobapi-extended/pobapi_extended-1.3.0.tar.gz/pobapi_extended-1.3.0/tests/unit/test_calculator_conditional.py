"""Tests for ConditionEvaluator."""

from typing import Any

import pytest

from pobapi.calculator.conditional import ConditionEvaluator


class TestConditionEvaluator:
    """Tests for ConditionEvaluator."""

    @pytest.mark.parametrize(
        ("condition", "current_life", "max_life", "expected"),
        [
            ("on_full_life", 100.0, 100.0, True),
            ("on_full_life", 99.0, 100.0, True),  # 99% threshold
            ("on_full_life", 98.0, 100.0, False),
            ("OnFullLife", 100.0, 100.0, True),
            ("on_low_life", 35.0, 100.0, True),  # 35% threshold
            ("on_low_life", 34.0, 100.0, True),
            ("on_low_life", 36.0, 100.0, False),
            ("OnLowLife", 30.0, 100.0, True),
        ],
    )
    def test_life_conditions(
        self, condition: str, current_life: float, max_life: float, expected: bool
    ) -> None:
        """Test life-based conditions."""
        context = {"current_life": current_life, "max_life": max_life}
        result = ConditionEvaluator.evaluate_condition(condition, context)
        assert result == expected

    @pytest.mark.parametrize(
        ("condition", "current_mana", "max_mana", "expected"),
        [
            ("on_full_mana", 100.0, 100.0, True),
            ("on_full_mana", 99.0, 100.0, True),
            ("on_full_mana", 98.0, 100.0, False),
            ("OnFullMana", 100.0, 100.0, True),
            ("on_low_mana", 35.0, 100.0, True),
            ("on_low_mana", 34.0, 100.0, True),
            ("on_low_mana", 36.0, 100.0, False),
            ("OnLowMana", 30.0, 100.0, True),
        ],
    )
    def test_mana_conditions(
        self, condition: str, current_mana: float, max_mana: float, expected: bool
    ) -> None:
        """Test mana-based conditions."""
        context = {"current_mana": current_mana, "max_mana": max_mana}
        result = ConditionEvaluator.evaluate_condition(condition, context)
        assert result == expected

    @pytest.mark.parametrize(
        ("condition", "current_es", "max_es", "expected"),
        [
            ("on_full_energy_shield", 100.0, 100.0, True),
            ("on_full_energy_shield", 99.0, 100.0, True),
            ("on_full_energy_shield", 98.0, 100.0, False),
            ("OnFullEnergyShield", 100.0, 100.0, True),
            ("on_low_energy_shield", 35.0, 100.0, True),
            ("on_low_energy_shield", 34.0, 100.0, True),
            ("on_low_energy_shield", 36.0, 100.0, False),
            ("OnLowEnergyShield", 30.0, 100.0, True),
        ],
    )
    def test_energy_shield_conditions(
        self, condition: str, current_es: float, max_es: float, expected: bool
    ) -> None:
        """Test energy shield-based conditions."""
        context = {"current_energy_shield": current_es, "max_energy_shield": max_es}
        result = ConditionEvaluator.evaluate_condition(condition, context)
        assert result == expected

    @pytest.mark.parametrize(
        ("condition", "context_value", "expected"),
        [
            ("on_full_life", True, True),
            ("on_full_life", False, False),
            ("on_low_life", True, True),
            ("on_low_life", False, False),
            ("on_full_mana", True, True),
            ("on_full_mana", False, False),
            ("on_low_mana", True, True),
            ("on_low_mana", False, False),
        ],
    )
    def test_life_mana_conditions_with_flags(
        self, condition: str, context_value: bool, expected: bool
    ) -> None:
        """Test life/mana conditions using flags when values not provided."""
        context = {condition: context_value}
        result = ConditionEvaluator.evaluate_condition(condition, context)
        assert result == expected

    @pytest.mark.parametrize(
        ("condition", "context_value", "expected"),
        [
            ("enemy_is_shocked", True, True),
            ("enemy_is_shocked", False, False),
            ("enemy_is_frozen", True, True),
            ("enemy_is_frozen", False, False),
            ("enemy_is_ignited", True, True),
            ("enemy_is_ignited", False, False),
            ("enemy_is_chilled", True, True),
            ("enemy_is_chilled", False, False),
            ("enemy_is_poisoned", True, True),
            ("enemy_is_poisoned", False, False),
        ],
    )
    def test_enemy_conditions(
        self, condition: str, context_value: bool, expected: bool
    ) -> None:
        """Test enemy condition flags."""
        context = {condition: context_value}
        result = ConditionEvaluator.evaluate_condition(condition, context)
        assert result == expected

    @pytest.mark.parametrize(
        ("distance", "required", "expected"),
        [
            ("close", "close", True),
            ("medium", "close", True),
            ("far", "close", False),
            ("close", "far", False),
            ("medium", "far", False),
            ("far", "far", True),
            ("close", "medium", False),
            ("medium", "medium", True),
        ],
    )
    def test_projectile_distance_conditions(
        self, distance: str, required: str, expected: bool
    ) -> None:
        """Test projectile distance conditions."""
        context = {
            "projectile_distance": distance,
            "required_distance": required,
        }
        result = ConditionEvaluator.evaluate_condition("projectile_distance", context)
        assert result == expected

    def test_default_condition(self) -> None:
        """Test default condition evaluation."""
        context = {"custom_condition": True}
        result = ConditionEvaluator.evaluate_condition("custom_condition", context)
        assert result is True

        context = {"custom_condition": False}
        result = ConditionEvaluator.evaluate_condition("custom_condition", context)
        assert result is False

        empty_context: dict[str, Any] = {}
        result = ConditionEvaluator.evaluate_condition(
            "unknown_condition", empty_context
        )
        assert result is False

    def test_evaluate_all_conditions_all_true(self) -> None:
        """Test evaluate_all_conditions when all conditions are met."""
        conditions = {
            "on_full_life": True,
            "enemy_is_shocked": True,
        }
        context = {
            "current_life": 100.0,
            "max_life": 100.0,
            "enemy_is_shocked": True,
        }
        result = ConditionEvaluator.evaluate_all_conditions(conditions, context)
        assert result is True

    def test_evaluate_all_conditions_one_false(self) -> None:
        """Test evaluate_all_conditions when one condition is not met."""
        # Fixed: evaluate_all_conditions now correctly returns False when
        # any condition fails
        conditions = {
            "on_full_life": True,
            "enemy_is_shocked": True,
        }
        context = {
            "current_life": 50.0,
            "max_life": 100.0,
            "enemy_is_shocked": True,
        }
        result = ConditionEvaluator.evaluate_all_conditions(conditions, context)
        # on_full_life is False (50 < 99), so the function should return False
        assert result is False

    def test_evaluate_all_conditions_empty(self) -> None:
        """Test evaluate_all_conditions with empty conditions."""
        conditions: dict[str, Any] = {}
        context: dict[str, Any] = {}
        result = ConditionEvaluator.evaluate_all_conditions(conditions, context)
        assert result is True

    def test_energy_shield_conditions_without_values(self) -> None:
        """Test energy shield conditions when values not provided.

        Covers lines 62, 67.
        """
        # Test on_full_energy_shield without max_es/current_es (covers line 62)
        context = {"on_full_energy_shield": True}
        result = ConditionEvaluator.evaluate_condition("on_full_energy_shield", context)
        assert result is True

        context = {"on_full_energy_shield": False}
        result = ConditionEvaluator.evaluate_condition("on_full_energy_shield", context)
        assert result is False

        # Test on_low_energy_shield without max_es/current_es (covers line 67)
        context = {"on_low_energy_shield": True}
        result = ConditionEvaluator.evaluate_condition("on_low_energy_shield", context)
        assert result is True

        context = {"on_low_energy_shield": False}
        result = ConditionEvaluator.evaluate_condition("on_low_energy_shield", context)
        assert result is False

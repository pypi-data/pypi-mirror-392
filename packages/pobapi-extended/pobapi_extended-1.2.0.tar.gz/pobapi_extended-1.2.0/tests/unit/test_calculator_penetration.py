"""Tests for PenetrationCalculator."""

from typing import TYPE_CHECKING

import pytest

from pobapi.calculator.modifiers import Modifier, ModifierType

if TYPE_CHECKING:
    from pobapi.calculator.modifiers import ModifierSystem
    from pobapi.calculator.penetration import PenetrationCalculator


class TestPenetrationCalculator:
    """Tests for PenetrationCalculator."""

    def test_init(self, penetration_calculator: "PenetrationCalculator") -> None:
        """Test PenetrationCalculator initialization."""
        assert penetration_calculator.modifiers is not None

    @pytest.mark.parametrize(
        ("base_res", "reduction", "penetration", "expected"),
        [
            (75.0, 0.0, 0.0, 0.75),  # 75% res, no changes
            (75.0, -44.0, 0.0, 0.31),  # 75% - 44% = 31%
            (75.0, 0.0, 37.0, 0.38),  # 75% - 37% = 38%
            (75.0, -44.0, 37.0, -0.06),  # 75% - 44% - 37% = -6%
            (0.0, 0.0, 0.0, 0.0),  # 0% res
            (75.0, 0.0, 100.0, -0.25),  # Over-penetration
        ],
    )
    def test_calculate_effective_resistance(
        self,
        penetration_calculator: "PenetrationCalculator",
        base_res: float,
        reduction: float,
        penetration: float,
        expected: float,
    ) -> None:
        """Test calculating effective resistance."""
        result = penetration_calculator.calculate_effective_resistance(
            base_res, reduction, penetration
        )
        assert result == pytest.approx(expected, rel=1e-6)

    def test_calculate_effective_resistance_min_cap(
        self, penetration_calculator: "PenetrationCalculator"
    ) -> None:
        """Test that resistance cannot go below -200%."""
        result = penetration_calculator.calculate_effective_resistance(
            0.0, -100.0, 150.0
        )
        # Should cap at -200% = -2.0
        assert result == pytest.approx(-2.0, rel=1e-6)

    def test_calculate_fire_resistance(
        self,
        penetration_calculator: "PenetrationCalculator",
        modifier_system: "ModifierSystem",
    ) -> None:
        """Test calculating fire resistance."""
        modifier_system.add_modifier(
            Modifier(
                stat="EnemyFireResistance",
                value=-44.0,  # Flammability curse
                mod_type=ModifierType.FLAT,
                source="test",
            )
        )
        modifier_system.add_modifier(
            Modifier(
                stat="FirePenetration",
                value=37.0,  # Fire Penetration support
                mod_type=ModifierType.FLAT,
                source="test",
            )
        )
        result = penetration_calculator.calculate_fire_resistance(75.0)
        # 75% - 44% - 37% = -6% = -0.06
        assert result == pytest.approx(-0.06, rel=1e-6)

    def test_calculate_cold_resistance(
        self,
        penetration_calculator: "PenetrationCalculator",
        modifier_system: "ModifierSystem",
    ) -> None:
        """Test calculating cold resistance."""
        modifier_system.add_modifier(
            Modifier(
                stat="EnemyColdResistance",
                value=-44.0,
                mod_type=ModifierType.FLAT,
                source="test",
            )
        )
        modifier_system.add_modifier(
            Modifier(
                stat="ColdPenetration",
                value=37.0,
                mod_type=ModifierType.FLAT,
                source="test",
            )
        )
        result = penetration_calculator.calculate_cold_resistance(75.0)
        assert result == pytest.approx(-0.06, rel=1e-6)

    def test_calculate_lightning_resistance(
        self,
        penetration_calculator: "PenetrationCalculator",
        modifier_system: "ModifierSystem",
    ) -> None:
        """Test calculating lightning resistance."""
        modifier_system.add_modifier(
            Modifier(
                stat="EnemyLightningResistance",
                value=-44.0,
                mod_type=ModifierType.FLAT,
                source="test",
            )
        )
        modifier_system.add_modifier(
            Modifier(
                stat="LightningPenetration",
                value=37.0,
                mod_type=ModifierType.FLAT,
                source="test",
            )
        )
        result = penetration_calculator.calculate_lightning_resistance(75.0)
        assert result == pytest.approx(-0.06, rel=1e-6)

    def test_calculate_chaos_resistance(
        self,
        penetration_calculator: "PenetrationCalculator",
        modifier_system: "ModifierSystem",
    ) -> None:
        """Test calculating chaos resistance."""
        modifier_system.add_modifier(
            Modifier(
                stat="EnemyChaosResistance",
                value=-20.0,
                mod_type=ModifierType.FLAT,
                source="test",
            )
        )
        modifier_system.add_modifier(
            Modifier(
                stat="ChaosPenetration",
                value=10.0,
                mod_type=ModifierType.FLAT,
                source="test",
            )
        )
        result = penetration_calculator.calculate_chaos_resistance(0.0)
        # 0% - 20% - 10% = -30% = -0.3
        assert result == pytest.approx(-0.3, rel=1e-6)

    def test_calculate_fire_resistance_no_modifiers(
        self, penetration_calculator: "PenetrationCalculator"
    ) -> None:
        """Test calculating fire resistance with no modifiers."""
        result = penetration_calculator.calculate_fire_resistance(75.0)
        assert result == pytest.approx(0.75, rel=1e-6)

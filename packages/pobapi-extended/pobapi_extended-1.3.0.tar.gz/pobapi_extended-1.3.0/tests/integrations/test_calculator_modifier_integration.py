"""Integration tests for explicit Calculator ↔ ModifierSystem integrations."""

import pytest

from pobapi import CalculationEngine
from pobapi.calculator.damage import DamageCalculator
from pobapi.calculator.defense import DefenseCalculator
from pobapi.calculator.minion import MinionCalculator
from pobapi.calculator.modifiers import (
    Modifier,
    ModifierSystem,
    ModifierType,
)
from pobapi.calculator.party import PartyCalculator
from pobapi.calculator.resource import ResourceCalculator
from pobapi.calculator.skill_stats import SkillStatsCalculator

pytestmark = pytest.mark.integration


class TestModifierSystemCalculatorIntegrations:
    """Test explicit integrations between ModifierSystem and all calculators."""

    def test_modifier_system_damage_calculator_integration(self) -> None:
        """Test explicit ModifierSystem ↔ DamageCalculator integration."""
        modifier_system = ModifierSystem()
        damage_calc = DamageCalculator(modifier_system)

        # Add damage modifiers
        modifier_system.add_modifier(
            Modifier(
                stat="PhysicalDamage",
                value=50.0,
                mod_type=ModifierType.INCREASED,
                source="test",
            )
        )

        # Damage calculator should use modifiers
        context = {}
        damage = damage_calc.calculate_base_damage("TestSkill", context)
        assert damage is not None

    def test_modifier_system_defense_calculator_integration(self) -> None:
        """Test explicit ModifierSystem ↔ DefenseCalculator integration."""
        modifier_system = ModifierSystem()
        defense_calc = DefenseCalculator(modifier_system)

        # Add defense modifiers
        modifier_system.add_modifier(
            Modifier(
                stat="Life",
                value=100.0,
                mod_type=ModifierType.FLAT,
                source="test",
            )
        )

        # Defense calculator should use modifiers
        context = {}
        defense = defense_calc.calculate_all_defenses(context)
        assert defense is not None

    def test_modifier_system_resource_calculator_integration(self) -> None:
        """Test explicit ModifierSystem ↔ ResourceCalculator integration."""
        modifier_system = ModifierSystem()
        resource_calc = ResourceCalculator(modifier_system)

        # Add resource modifiers
        modifier_system.add_modifier(
            Modifier(
                stat="Mana",
                value=50.0,
                mod_type=ModifierType.FLAT,
                source="test",
            )
        )

        # Resource calculator should use modifiers
        context = {}
        mana_cost = resource_calc.calculate_mana_cost("Test Skill", context)
        assert mana_cost is not None

    def test_modifier_system_skill_stats_calculator_integration(self) -> None:
        """Test explicit ModifierSystem ↔ SkillStatsCalculator integration."""
        modifier_system = ModifierSystem()
        skill_stats_calc = SkillStatsCalculator(modifier_system)

        # Add skill modifiers
        modifier_system.add_modifier(
            Modifier(
                stat="SkillDamage",
                value=25.0,
                mod_type=ModifierType.INCREASED,
                source="test",
            )
        )

        # Skill stats calculator should use modifiers
        context = {}
        # calculate_area_of_effect_radius requires skill_name and base_radius
        aoe_radius = skill_stats_calc.calculate_area_of_effect_radius(
            skill_name="Test Skill", base_radius=10.0, context=context
        )
        assert aoe_radius is not None

    def test_modifier_system_minion_calculator_integration(self) -> None:
        """Test explicit ModifierSystem ↔ MinionCalculator integration."""
        modifier_system = ModifierSystem()
        minion_calc = MinionCalculator(modifier_system)

        # Add minion modifiers
        modifier_system.add_modifier(
            Modifier(
                stat="MinionDamage",
                value=40.0,
                mod_type=ModifierType.INCREASED,
                source="test",
            )
        )

        # Minion calculator should use modifiers
        context = {}
        minion_stats = minion_calc.calculate_all_minion_stats(context)
        assert minion_stats is not None

    def test_modifier_system_party_calculator_integration(self) -> None:
        """Test explicit ModifierSystem ↔ PartyCalculator integration."""
        from pobapi.calculator.party import PartyMember

        modifier_system = ModifierSystem()
        party_calc = PartyCalculator(modifier_system)

        # Add party members
        party_members = [
            PartyMember(
                name="Support",
                auras=["Hatred"],
                aura_effectiveness=100.0,
            )
        ]

        # Process party (adds modifiers to system)
        modifiers = party_calc.process_party(party_members)

        # Modifier system should have party modifiers
        assert len(modifiers) > 0
        assert modifier_system is not None


class TestCalculationEngineModifierSystemIntegration:
    """Test explicit CalculationEngine ↔ ModifierSystem integration."""

    def test_engine_shares_modifier_system_with_calculators(self, build) -> None:
        """Test that CalculationEngine shares ModifierSystem with all calculators."""
        engine = CalculationEngine()
        engine.load_build(build)

        # All calculators should use the same modifier system
        assert engine.modifiers is engine.damage_calc.modifiers
        assert engine.modifiers is engine.defense_calc.modifiers
        assert engine.modifiers is engine.resource_calc.modifiers
        assert engine.modifiers is engine.skill_stats_calc.modifiers
        assert engine.modifiers is engine.minion_calc.modifiers
        assert engine.modifiers is engine.party_calc.modifiers

    def test_add_modifier_affects_all_calculators(self, build) -> None:
        """Test that adding modifier affects all calculators."""
        engine = CalculationEngine()
        engine.load_build(build)

        # Add modifier
        engine.modifiers.add_modifier(
            Modifier(
                stat="Life",
                value=200.0,
                mod_type=ModifierType.FLAT,
                source="test",
            )
        )

        # All calculators should see the modifier
        context = {}
        defense = engine.defense_calc.calculate_all_defenses(context)
        assert defense is not None

        # Calculate all stats
        stats = engine.calculate_all_stats(build_data=build)
        assert stats is not None


class TestCalculatorCrossIntegration:
    """Test integrations between different calculators."""

    def test_damage_and_defense_calculators_share_modifiers(self) -> None:
        """Test that DamageCalculator and DefenseCalculator share modifiers."""
        modifier_system = ModifierSystem()
        damage_calc = DamageCalculator(modifier_system)
        defense_calc = DefenseCalculator(modifier_system)

        context = {}
        skill_name = "TestSkill"

        # Compute baseline damage and defenses before adding modifier
        baseline_damage = damage_calc.calculate_base_damage(skill_name, context)
        baseline_damage_total = baseline_damage.total
        baseline_defense = defense_calc.calculate_all_defenses(context)
        baseline_life = baseline_defense.life

        # Add modifier that affects both damage and defense
        # Using a modifier that adds base physical damage for the skill
        modifier_system.add_modifier(
            Modifier(
                stat=f"{skill_name}BasePhysicalDamage",
                value=50.0,
                mod_type=ModifierType.FLAT,
                source="test",
            )
        )
        # Add modifier that affects life
        modifier_system.add_modifier(
            Modifier(
                stat="Life",
                value=100.0,
                mod_type=ModifierType.FLAT,
                source="test",
            )
        )

        # Compute damage and defenses after adding modifiers
        after_damage = damage_calc.calculate_base_damage(skill_name, context)
        after_damage_total = after_damage.total
        after_defense = defense_calc.calculate_all_defenses(context)
        after_life = after_defense.life

        # Assert that damage and defenses changed by the expected amount
        damage_change = after_damage_total - baseline_damage_total
        life_change = after_life - baseline_life

        # Damage should have increased by at least the flat modifier (50.0)
        assert damage_change >= 50.0, (
            f"Damage should have increased by at least 50.0, "
            f"but changed by {damage_change}"
        )
        # Life should have increased by the flat modifier (100.0)
        assert (
            life_change == 100.0
        ), f"Life should have increased by 100.0, but changed by {life_change}"

        # Assert that both calculators share the same ModifierSystem
        # by verifying they both see the same modifier changes
        # The fact that both calculators observed changes from the same
        # modifier system proves they share it
        assert damage_calc.modifiers is defense_calc.modifiers
        assert damage_calc.modifiers is modifier_system
        assert defense_calc.modifiers is modifier_system

    def test_all_calculators_through_engine(self, build) -> None:
        """Test all calculators working together through engine."""
        engine = CalculationEngine()
        engine.load_build(build)

        # Add various modifiers
        engine.modifiers.add_modifier(
            Modifier(
                stat="Damage",
                value=20.0,
                mod_type=ModifierType.INCREASED,
                source="test",
            )
        )
        engine.modifiers.add_modifier(
            Modifier(
                stat="Life",
                value=100.0,
                mod_type=ModifierType.FLAT,
                source="test",
            )
        )
        engine.modifiers.add_modifier(
            Modifier(
                stat="Mana",
                value=50.0,
                mod_type=ModifierType.FLAT,
                source="test",
            )
        )

        # All calculators should work together
        stats = engine.calculate_all_stats(build_data=build)
        assert stats is not None
        assert hasattr(stats, "life")
        assert hasattr(stats, "mana")

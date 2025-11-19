"""Integration tests for calculator components working together."""

import copy

import pytest

from pobapi.calculator.engine import CalculationEngine
from pobapi.calculator.modifiers import Modifier, ModifierType

pytestmark = pytest.mark.integration


class TestCalculatorComponentsIntegration:
    """Test integration between different calculator components."""

    def test_modifier_system_to_damage_calculator(self, build):
        """Test modifier system feeding into damage calculator."""
        engine = CalculationEngine()
        engine.load_build(build)

        # Add damage modifier
        engine.modifiers.add_modifier(
            Modifier(
                stat="Damage",
                value=50.0,
                mod_type=ModifierType.INCREASED,
                source="test",
            )
        )

        # Calculate damage
        stats = engine.calculate_all_stats(build_data=build)
        assert stats is not None

    def test_modifier_system_to_defense_calculator(self, build):
        """Test modifier system feeding into defense calculator."""
        engine = CalculationEngine()
        engine.load_build(build)

        # Add defense modifiers
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
                stat="Armour",
                value=50.0,
                mod_type=ModifierType.INCREASED,
                source="test",
            )
        )

        # Calculate defense
        stats = engine.calculate_all_stats(build_data=build)
        assert stats is not None
        assert hasattr(stats, "life")

    def test_modifier_system_to_resource_calculator(self, build):
        """Test modifier system feeding into resource calculator."""
        engine = CalculationEngine()
        engine.load_build(build)

        # Add resource modifiers
        engine.modifiers.add_modifier(
            Modifier(
                stat="Mana",
                value=50.0,
                mod_type=ModifierType.FLAT,
                source="test",
            )
        )
        engine.modifiers.add_modifier(
            Modifier(
                stat="ManaRegen",
                value=10.0,
                mod_type=ModifierType.FLAT,
                source="test",
            )
        )

        # Calculate resources
        stats = engine.calculate_all_stats(build_data=build)
        assert stats is not None
        assert hasattr(stats, "mana")

    def test_damage_and_defense_calculators_together(self, build):
        """Test damage and defense calculators working together."""
        engine = CalculationEngine()
        engine.load_build(build)

        # Add both damage and defense modifiers
        engine.modifiers.add_modifier(
            Modifier(
                stat="Damage",
                value=30.0,
                mod_type=ModifierType.INCREASED,
                source="test",
            )
        )
        engine.modifiers.add_modifier(
            Modifier(
                stat="Life",
                value=200.0,
                mod_type=ModifierType.FLAT,
                source="test",
            )
        )

        # Calculate all stats
        stats = engine.calculate_all_stats(build_data=build)
        assert stats is not None
        assert hasattr(stats, "life")

    def test_skill_stats_with_modifier_system(self, build):
        """Test skill stats calculator with modifier system."""
        engine = CalculationEngine()
        engine.load_build(build)

        # Add skill-related modifiers
        engine.modifiers.add_modifier(
            Modifier(
                stat="SkillDamage",
                value=25.0,
                mod_type=ModifierType.INCREASED,
                source="test",
            )
        )

        # Calculate stats
        stats = engine.calculate_all_stats(build_data=build)
        assert stats is not None

    def test_minion_calculator_with_modifier_system(self, build):
        """Test minion calculator with modifier system."""
        engine = CalculationEngine()
        engine.load_build(build)

        # Add minion modifiers
        engine.modifiers.add_modifier(
            Modifier(
                stat="MinionDamage",
                value=40.0,
                mod_type=ModifierType.INCREASED,
                source="test",
            )
        )
        engine.modifiers.add_modifier(
            Modifier(
                stat="MinionLife",
                value=100.0,
                mod_type=ModifierType.FLAT,
                source="test",
            )
        )

        # Calculate stats
        stats = engine.calculate_all_stats(build_data=build)
        assert stats is not None

    def test_party_calculator_with_modifier_system(self, build):
        """Test party calculator with modifier system."""
        from pobapi.calculator.party import PartyMember

        engine = CalculationEngine()

        # Create a copy of build to avoid mutating the shared fixture
        build_copy = copy.deepcopy(build)

        # Add party members
        party_members = [
            PartyMember(
                name="Support",
                auras=["Hatred", "Discipline"],
                aura_effectiveness=100.0,
            )
        ]

        build_copy.party_members = party_members  # type: ignore
        engine.load_build(build_copy)

        # Calculate stats
        stats = engine.calculate_all_stats(build_data=build_copy)
        assert stats is not None


class TestGameDataLoaderIntegration:
    """Test integration of GameDataLoader with other components."""

    def test_game_data_loader_with_passive_tree_parser(self, build):
        """Test GameDataLoader providing data to PassiveTreeParser."""
        from pobapi.calculator.passive_tree_parser import PassiveTreeParser

        # GameDataLoader loads data on demand, no explicit load_all method
        # Parser should be able to use loaded data
        if build.active_skill_tree and build.active_skill_tree.nodes:
            modifiers = PassiveTreeParser.parse_tree(build.active_skill_tree.nodes)
            assert isinstance(modifiers, list)

    def test_game_data_loader_with_item_modifier_parser(self):
        """Test GameDataLoader providing data to ItemModifierParser."""
        from pobapi.calculator.item_modifier_parser import ItemModifierParser

        # GameDataLoader loads data on demand, no explicit load_all method
        # Parser should work with loaded data
        modifiers = ItemModifierParser.parse_item_text(
            "+50 to maximum Life\n+20% increased Life"
        )
        assert isinstance(modifiers, list)


class TestAdditionalCalculatorIntegrations:
    """Test integration for additional calculator components."""

    def test_mirage_calculator_with_modifier_system(self, build):
        """Test MirageCalculator with modifier system."""
        engine = CalculationEngine()
        engine.load_build(build)

        # Add modifiers that affect mirage
        engine.modifiers.add_modifier(
            Modifier(
                stat="MirageDamage",
                value=30.0,
                mod_type=ModifierType.INCREASED,
                source="test",
            )
        )

        # Calculate stats (mirage calculator is part of engine)
        stats = engine.calculate_all_stats(build_data=build)
        assert stats is not None

    def test_pantheon_tools_with_modifier_system(self, build):
        """Test PantheonTools with modifier system."""
        from pobapi.calculator.pantheon import PantheonGod, PantheonSoul

        engine = CalculationEngine()
        engine.load_build(build)

        # Calculate stats before applying pantheon to get baseline
        stats_before = engine.calculate_all_stats(build_data=build)
        fire_res_before = stats_before.fire_resistance or 0.0

        # Create pantheon god with souls
        souls = [
            PantheonSoul(
                name="Minor Soul",
                mods=["+5% to Fire Resistance"],
            )
        ]
        god = PantheonGod(name="Test God", souls=souls)

        # Apply pantheon god to engine
        engine.pantheon_tools.apply_soul_mod(god)

        # Calculate stats after applying pantheon
        stats = engine.calculate_all_stats(build_data=build)
        assert stats is not None
        # Verify that pantheon soul modifier affected fire resistance
        fire_res_after = stats.fire_resistance or 0.0
        assert fire_res_after >= fire_res_before

    def test_config_modifier_parser_with_engine(self, build):
        """Test ConfigModifierParser integration with CalculationEngine."""

        engine = CalculationEngine()
        engine.load_build(build)

        # Config parser should extract modifiers from build config
        if build.config:
            # Config modifiers are processed during load_build
            stats = engine.calculate_all_stats(build_data=build)
            assert stats is not None

    def test_skill_modifier_parser_with_engine(self, build):
        """Test SkillModifierParser integration with CalculationEngine."""

        engine = CalculationEngine()
        engine.load_build(build)

        # Skill parser should extract modifiers from skills
        if build.skill_groups:
            # Skill modifiers are processed during load_build
            stats = engine.calculate_all_stats(build_data=build)
            assert stats is not None

    def test_penetration_calculator_with_damage_calculator(self, build):
        """Test PenetrationCalculator integration with DamageCalculator."""

        engine = CalculationEngine()
        engine.load_build(build)

        # Add penetration modifiers
        engine.modifiers.add_modifier(
            Modifier(
                stat="FirePenetration",
                value=10.0,
                mod_type=ModifierType.FLAT,
                source="test",
            )
        )

        # Penetration affects damage calculations
        stats = engine.calculate_all_stats(build_data=build)
        assert stats is not None

    def test_all_calculators_together(self, build):
        """Test all calculator components working together."""
        engine = CalculationEngine()
        engine.load_build(build)

        # Add various modifiers affecting different calculators
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

        # Calculate all stats - all calculators should work together
        stats = engine.calculate_all_stats(build_data=build)
        assert stats is not None
        assert hasattr(stats, "life")
        assert hasattr(stats, "mana")

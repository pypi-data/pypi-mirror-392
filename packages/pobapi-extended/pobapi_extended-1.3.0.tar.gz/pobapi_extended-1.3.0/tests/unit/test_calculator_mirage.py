"""Tests for Mirage calculator."""

from unittest.mock import Mock

import pytest

from pobapi.calculator.damage import DamageBreakdown, DamageCalculator
from pobapi.calculator.mirage import MirageCalculator, MirageStats
from pobapi.calculator.modifiers import ModifierSystem


class TestMirageStats:
    """Tests for MirageStats dataclass."""

    def test_init_basic(self):
        """Test basic initialization."""
        stats = MirageStats(name="Test Mirage")
        assert stats.name == "Test Mirage"
        assert stats.count == 1
        assert stats.damage_multiplier == 1.0
        assert stats.speed_multiplier == 1.0
        assert stats.dps == 0.0
        assert stats.breakdown is None

    def test_init_with_values(self):
        """Test initialization with all values."""
        breakdown = DamageBreakdown()
        stats = MirageStats(
            name="Test",
            count=3,
            damage_multiplier=0.8,
            speed_multiplier=0.9,
            dps=100.0,
            breakdown=breakdown,
        )
        assert stats.count == 3
        assert stats.damage_multiplier == 0.8
        assert stats.speed_multiplier == 0.9
        assert stats.dps == 100.0
        assert stats.breakdown == breakdown


class TestMirageCalculator:
    """Tests for MirageCalculator class."""

    @pytest.fixture
    def mock_modifiers(self):
        """Create a mock ModifierSystem."""
        return Mock(spec=ModifierSystem)

    @pytest.fixture
    def mock_damage_calc(self):
        """Create a mock DamageCalculator."""
        return Mock(spec=DamageCalculator)

    @pytest.fixture
    def calculator(self, mock_modifiers, mock_damage_calc):
        """Create a MirageCalculator instance."""
        return MirageCalculator(mock_modifiers, mock_damage_calc)

    def test_init(self, mock_modifiers, mock_damage_calc):
        """Test initialization."""
        calc = MirageCalculator(mock_modifiers, mock_damage_calc)
        assert calc.modifiers == mock_modifiers
        assert calc.damage_calc == mock_damage_calc

    def test_calculate_mirage_archer_not_triggered(self, calculator):
        """Test calculate_mirage_archer returns None when not triggered."""
        context = {"triggeredByMirageArcher": False}
        result = calculator.calculate_mirage_archer("Arc", context)
        assert result is None

    def test_calculate_mirage_archer_triggered(
        self, calculator, mock_modifiers, mock_damage_calc
    ):
        """Test calculate_mirage_archer calculates stats when triggered."""
        context = {"triggeredByMirageArcher": True}

        # Mock modifier calculations
        mock_modifiers.calculate_stat.side_effect = lambda stat, default, ctx: {
            "MirageArcherLessDamage": -30.0,
            "MirageArcherLessAttackSpeed": -20.0,
            "MirageArcherMaxCount": 1.0,
        }.get(stat, default)

        # Mock damage calculations
        breakdown = DamageBreakdown()
        breakdown.physical = 100.0
        breakdown.fire = 50.0
        mock_damage_calc.calculate_total_dps_with_dot.return_value = (100.0, 0.0, 0.0)
        mock_damage_calc.calculate_damage_against_enemy.return_value = breakdown

        result = calculator.calculate_mirage_archer("Arc", context)

        assert result is not None
        assert result.name == "1 Mirage Archers using Arc"
        assert result.count == 1
        assert result.damage_multiplier == pytest.approx(0.7)  # 1.0 + (-30.0 / 100.0)
        assert result.speed_multiplier == pytest.approx(0.8)  # 1.0 + (-20.0 / 100.0)
        assert result.breakdown is not None

    def test_calculate_saviour_wrong_skill(self, calculator):
        """Test calculate_saviour returns None for wrong skill."""
        result = calculator.calculate_saviour("Arc", {})
        assert result is None

    def test_calculate_saviour_correct_skill(
        self, calculator, mock_modifiers, mock_damage_calc
    ):
        """Test calculate_saviour calculates stats for Reflection skill."""
        context = {"bestSwordAttackSkill": "Cyclone"}

        mock_modifiers.calculate_stat.side_effect = lambda stat, default, ctx: {
            "SaviourMirageWarriorLessDamage": -20.0,
            "SaviourMirageWarriorMaxCount": 2.0,
        }.get(stat, default)

        breakdown = DamageBreakdown()
        mock_damage_calc.calculate_total_dps_with_dot.return_value = (200.0, 0.0, 0.0)
        mock_damage_calc.calculate_damage_against_enemy.return_value = breakdown

        result = calculator.calculate_saviour("Reflection", context)

        assert result is not None
        assert "Mirage Warriors" in result.name
        assert result.count == 2

    def test_calculate_saviour_dual_wield_same(
        self, calculator, mock_modifiers, mock_damage_calc
    ):
        """Test calculate_saviour halves count when dual wielding same weapon."""
        context = {
            "bestSwordAttackSkill": "Cyclone",
            "dualWieldSameWeapon": True,
        }

        mock_modifiers.calculate_stat.side_effect = lambda stat, default, ctx: {
            "SaviourMirageWarriorLessDamage": -20.0,
            "SaviourMirageWarriorMaxCount": 2.0,
        }.get(stat, default)

        mock_damage_calc.calculate_total_dps_with_dot.return_value = (200.0, 0.0, 0.0)
        mock_damage_calc.calculate_damage_against_enemy.return_value = DamageBreakdown()

        result = calculator.calculate_saviour("Reflection", context)

        assert result is not None
        assert result.count == 1  # 2.0 / 2.0 = 1.0

    def test_calculate_tawhoas_chosen_wrong_skill(self, calculator):
        """Test calculate_tawhoas_chosen returns None for wrong skill."""
        result = calculator.calculate_tawhoas_chosen("Arc", {})
        assert result is None

    def test_calculate_tawhoas_chosen_correct_skill(
        self, calculator, mock_modifiers, mock_damage_calc
    ):
        """Test calculate_tawhoas_chosen calculates stats."""
        context = {
            "bestSlamMeleeAttackSkill": "Earthshatter",
            "tawhoasChosenCooldown": 4.0,
            "triggeredSkillCooldown": 0.0,
        }

        mock_modifiers.calculate_stat.side_effect = lambda stat, default, ctx: {
            "ChieftainMirageChieftainMoreDamage": 50.0,
            "CooldownRecovery": 100.0,
        }.get(stat, default)

        mock_damage_calc.calculate_total_dps_with_dot.return_value = (100.0, 0.0, 0.0)
        mock_damage_calc.calculate_damage_against_enemy.return_value = DamageBreakdown()

        result = calculator.calculate_tawhoas_chosen("Tawhoa's Chosen", context)

        assert result is not None
        assert "Tawhoa's Chosen" in result.name
        assert result.count == 1
        assert result.damage_multiplier == pytest.approx(1.5)  # 1.0 + (50.0 / 100.0)

    def test_calculate_sacred_wisps_not_triggered(self, calculator):
        """Test calculate_sacred_wisps returns None when not triggered."""
        context = {"triggeredBySacredWisps": False}
        result = calculator.calculate_sacred_wisps("Arc", context)
        assert result is None

    def test_calculate_sacred_wisps_triggered(
        self, calculator, mock_modifiers, mock_damage_calc
    ):
        """Test calculate_sacred_wisps calculates stats when triggered."""
        context = {"triggeredBySacredWisps": True}

        mock_modifiers.calculate_stat.side_effect = lambda stat, default, ctx: {
            "SacredWispsLessDamage": -40.0,
            "SacredWispsChance": 50.0,
            "SacredWispsMaxCount": 2.0,
        }.get(stat, default)

        mock_damage_calc.calculate_total_dps_with_dot.return_value = (100.0, 0.0, 0.0)
        mock_damage_calc.calculate_damage_against_enemy.return_value = DamageBreakdown()

        result = calculator.calculate_sacred_wisps("Arc", context)

        assert result is not None
        assert "Sacred Wisps" in result.name
        assert result.count == 2
        assert result.speed_multiplier == pytest.approx(0.5)  # 50.0 / 100.0

    def test_calculate_generals_cry_not_triggered(self, calculator):
        """Test calculate_generals_cry returns None when not triggered."""
        context = {"triggeredByGeneralsCry": False}
        result = calculator.calculate_generals_cry("Cyclone", context)
        assert result is None

    def test_calculate_generals_cry_triggered(
        self, calculator, mock_modifiers, mock_damage_calc
    ):
        """Test calculate_generals_cry calculates stats when triggered."""
        context = {
            "triggeredByGeneralsCry": True,
            "generalsCryCooldown": 1.0,
            "isChanneling": False,
            "hitTime": 0.5,
        }

        mock_modifiers.calculate_stat.side_effect = lambda stat, default, ctx: {
            "GeneralsCryDoubleMaxCount": 5.0,
        }.get(stat, default)

        mock_damage_calc.calculate_total_dps_with_dot.return_value = (100.0, 0.0, 0.0)
        mock_damage_calc.calculate_damage_against_enemy.return_value = DamageBreakdown()

        result = calculator.calculate_generals_cry("Cyclone", context)

        assert result is not None
        assert "GC Mirages" in result.name
        assert result.count == 5

    def test_calculate_all_mirages_none(self, calculator):
        """Test calculate_all_mirages returns empty list when none apply."""
        result = calculator.calculate_all_mirages("Arc", {})
        assert result == []

    def test_calculate_all_mirages_some(
        self, calculator, mock_modifiers, mock_damage_calc
    ):
        """Test calculate_all_mirages returns list of applicable mirages."""
        context = {"triggeredByMirageArcher": True}

        mock_modifiers.calculate_stat.side_effect = lambda stat, default, ctx: {
            "MirageArcherLessDamage": -30.0,
            "MirageArcherLessAttackSpeed": -20.0,
            "MirageArcherMaxCount": 1.0,
        }.get(stat, default)

        mock_damage_calc.calculate_total_dps_with_dot.return_value = (100.0, 0.0, 0.0)
        mock_damage_calc.calculate_damage_against_enemy.return_value = DamageBreakdown()

        result = calculator.calculate_all_mirages("Arc", context)

        assert len(result) == 1
        assert result[0].name == "1 Mirage Archers using Arc"

    def test_calculate_all_mirages_multiple(
        self, calculator, mock_modifiers, mock_damage_calc
    ):
        """Test calculate_all_mirages can return multiple mirages."""
        context = {
            "triggeredByMirageArcher": True,
            "triggeredBySacredWisps": True,
        }

        def side_effect(stat, default, ctx):
            if "MirageArcher" in stat:
                return {
                    "MirageArcherLessDamage": -30.0,
                    "MirageArcherLessAttackSpeed": -20.0,
                    "MirageArcherMaxCount": 1.0,
                }.get(stat, default)
            elif "SacredWisps" in stat:
                return {
                    "SacredWispsLessDamage": -40.0,
                    "SacredWispsChance": 50.0,
                    "SacredWispsMaxCount": 2.0,
                }.get(stat, default)
            return default

        mock_modifiers.calculate_stat.side_effect = side_effect
        mock_damage_calc.calculate_total_dps_with_dot.return_value = (100.0, 0.0, 0.0)
        mock_damage_calc.calculate_damage_against_enemy.return_value = DamageBreakdown()

        result = calculator.calculate_all_mirages("Arc", context)

        assert len(result) == 2
        assert any("Mirage Archers" in m.name for m in result)
        assert any("Sacred Wisps" in m.name for m in result)

    def test_calculate_mirage_archer_none_context(
        self, calculator, mock_modifiers, mock_damage_calc
    ):
        """Test calculate_mirage_archer with None context - covers line 75."""
        # Mock modifier calculations
        mock_modifiers.calculate_stat.side_effect = lambda stat, default, ctx: {
            "MirageArcherLessDamage": -30.0,
            "MirageArcherLessAttackSpeed": -20.0,
            "MirageArcherMaxCount": 1.0,
        }.get(stat, default)

        # Mock damage calculations
        breakdown = DamageBreakdown()
        mock_damage_calc.calculate_total_dps_with_dot.return_value = (100.0, 0.0, 0.0)
        mock_damage_calc.calculate_damage_against_enemy.return_value = breakdown

        # Pass None context (covers line 75)
        result = calculator.calculate_mirage_archer("Arc", None)
        # Should return None because triggeredByMirageArcher is False by default
        assert result is None

    def test_calculate_saviour_none_context(
        self, calculator, mock_modifiers, mock_damage_calc
    ):
        """Test calculate_saviour with None context - covers line 135."""
        # Mock modifier calculations
        mock_modifiers.calculate_stat.side_effect = lambda stat, default, ctx: {
            "SaviourMirageWarriorLessDamage": 0.0,
            "SaviourMirageWarriorMaxCount": 2.0,
        }.get(stat, default)

        mock_damage_calc.calculate_total_dps_with_dot.return_value = (200.0, 0.0, 0.0)
        mock_damage_calc.calculate_damage_against_enemy.return_value = DamageBreakdown()

        # Pass None context (covers line 135)
        result = calculator.calculate_saviour("Reflection", None)
        # Should return result because skill_name is "Reflection"
        assert result is not None

    def test_calculate_tawhoas_chosen_none_context(
        self, calculator, mock_modifiers, mock_damage_calc
    ):
        """Test calculate_tawhoas_chosen with None context - covers line 199."""
        # Mock modifier calculations
        mock_modifiers.calculate_stat.side_effect = lambda stat, default, ctx: {
            "ChieftainMirageChieftainMoreDamage": 0.0,
            "CooldownRecovery": 100.0,
        }.get(stat, default)

        mock_damage_calc.calculate_total_dps_with_dot.return_value = (100.0, 0.0, 0.0)
        mock_damage_calc.calculate_damage_against_enemy.return_value = DamageBreakdown()

        # Pass None context (covers line 199)
        result = calculator.calculate_tawhoas_chosen("Tawhoa's Chosen", None)
        # Should return result because skill_name is "Tawhoa's Chosen"
        assert result is not None

    def test_calculate_sacred_wisps_none_context(self, calculator):
        """Test calculate_sacred_wisps with None context - covers line 271."""
        # Pass None context (covers line 271)
        result = calculator.calculate_sacred_wisps("Arc", None)
        # Should return None because triggeredBySacredWisps is False by default
        assert result is None

    def test_calculate_generals_cry_none_context(self, calculator):
        """Test calculate_generals_cry with None context - covers line 332."""
        # Pass None context (covers line 332)
        result = calculator.calculate_generals_cry("Cyclone", None)
        # Should return None because triggeredByGeneralsCry is False by default
        assert result is None

    def test_calculate_all_mirages_none_context(self, calculator):
        """Test calculate_all_mirages with None context - covers line 389."""
        # Pass None context (covers line 389)
        result = calculator.calculate_all_mirages("Arc", None)
        assert result == []

    def test_calculate_all_mirages_with_saviour(
        self, calculator, mock_modifiers, mock_damage_calc
    ):
        """Test calculate_all_mirages includes saviour - covers line 400."""
        context = {"bestSwordAttackSkill": "Cyclone"}

        mock_modifiers.calculate_stat.side_effect = lambda stat, default, ctx: {
            "SaviourMirageWarriorLessDamage": -20.0,
            "SaviourMirageWarriorMaxCount": 2.0,
        }.get(stat, default)

        mock_damage_calc.calculate_total_dps_with_dot.return_value = (200.0, 0.0, 0.0)
        mock_damage_calc.calculate_damage_against_enemy.return_value = DamageBreakdown()

        result = calculator.calculate_all_mirages("Reflection", context)

        # Should include saviour (covers line 400)
        assert len(result) == 1
        assert "Mirage Warriors" in result[0].name

    def test_calculate_all_mirages_with_tawhoas(
        self, calculator, mock_modifiers, mock_damage_calc
    ):
        """Test calculate_all_mirages includes tawhoas - covers line 404."""
        context = {
            "bestSlamMeleeAttackSkill": "Earthshatter",
            "tawhoasChosenCooldown": 4.0,
            "triggeredSkillCooldown": 0.0,
        }

        mock_modifiers.calculate_stat.side_effect = lambda stat, default, ctx: {
            "ChieftainMirageChieftainMoreDamage": 50.0,
            "CooldownRecovery": 100.0,
        }.get(stat, default)

        mock_damage_calc.calculate_total_dps_with_dot.return_value = (100.0, 0.0, 0.0)
        mock_damage_calc.calculate_damage_against_enemy.return_value = DamageBreakdown()

        result = calculator.calculate_all_mirages("Tawhoa's Chosen", context)

        # Should include tawhoas (covers line 404)
        assert len(result) == 1
        assert "Tawhoa's Chosen" in result[0].name

    def test_calculate_all_mirages_with_generals_cry(
        self, calculator, mock_modifiers, mock_damage_calc
    ):
        """Test calculate_all_mirages includes generals_cry - covers line 412."""
        context = {
            "triggeredByGeneralsCry": True,
            "generalsCryCooldown": 1.0,
            "isChanneling": False,
            "hitTime": 0.5,
        }

        mock_modifiers.calculate_stat.side_effect = lambda stat, default, ctx: {
            "GeneralsCryDoubleMaxCount": 5.0,
        }.get(stat, default)

        mock_damage_calc.calculate_total_dps_with_dot.return_value = (100.0, 0.0, 0.0)
        mock_damage_calc.calculate_damage_against_enemy.return_value = DamageBreakdown()

        result = calculator.calculate_all_mirages("Cyclone", context)

        # Should include generals_cry (covers line 412)
        assert len(result) == 1
        assert "GC Mirages" in result[0].name

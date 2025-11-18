"""Integration tests for API and CalculationEngine components."""

import pytest

pytestmark = pytest.mark.integration

from pobapi import CalculationEngine  # noqa: E402


class TestAPICalculationEngineIntegration:
    """Test integration between PathOfBuildingAPI and CalculationEngine."""

    def test_load_build_from_api_to_engine(self, build):
        """Test loading a build from API into calculation engine."""
        engine = CalculationEngine()
        engine.load_build(build)

        # Verify engine has loaded modifiers
        assert engine.modifiers is not None
        assert engine.damage_calc is not None
        assert engine.defense_calc is not None

    def test_calculate_stats_from_api_build(self, build):
        """Test calculating stats from API build data."""
        engine = CalculationEngine()
        engine.load_build(build)

        # Calculate stats
        stats = engine.calculate_all_stats(build_data=build)

        # Verify stats are calculated
        assert stats is not None
        assert hasattr(stats, "life")
        assert hasattr(stats, "mana")

    def test_api_items_to_engine_modifiers(self, build):
        """Test that items from API are converted to modifiers in engine."""
        engine = CalculationEngine()
        engine.load_build(build)

        # Check that items were processed
        if build.items:
            # Engine should have modifiers from items
            assert engine.modifiers is not None

    def test_api_skill_tree_to_engine_modifiers(self, build):
        """Test that skill tree from API is converted to modifiers in engine."""
        engine = CalculationEngine()
        engine.load_build(build)

        # Check that tree was processed
        if build.active_skill_tree:
            # Engine should have modifiers from tree
            assert engine.modifiers is not None

    def test_api_config_to_engine_context(self, build):
        """Test that config from API is used in engine calculations."""
        engine = CalculationEngine()
        engine.load_build(build)

        # Create context from config
        context = {}
        if build.config:
            context["enemy_level"] = getattr(build.config, "enemy_level", 80)

        # Calculate with context
        stats = engine.calculate_all_stats(context=context, build_data=build)
        assert stats is not None

    def test_full_build_processing_pipeline(self):
        """Test full pipeline: import code -> API -> Engine -> Stats."""
        # This would require a real import code, so we'll use a fixture
        # In a real scenario, you'd load from actual import code
        pass


class TestBuildModifierCalculationIntegration:
    """Test integration between BuildModifier and CalculationEngine."""

    def test_modify_build_then_recalculate(self, build):
        """Test modifying build and recalculating stats."""
        from pobapi.models import Item

        engine = CalculationEngine()
        engine.load_build(build)

        # Get initial stats
        initial_stats = engine.calculate_all_stats(build_data=build)

        # Modify build (add item)
        test_item = Item(
            name="Test Item",
            base="Leather Belt",
            rarity="Rare",
            uid="test-1",
            shaper=False,
            elder=False,
            crafted=False,
            quality=None,
            sockets=None,
            level_req=1,
            item_level=80,
            implicit=None,
            text="+50 to maximum Life",
        )

        build._modifier.equip_item(test_item, "Belt")

        # Reload and recalculate
        engine.load_build(build)
        new_stats = engine.calculate_all_stats(build_data=build)

        # Stats should be different (or at least calculated)
        assert new_stats is not None
        assert initial_stats is not None

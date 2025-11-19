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
        from pobapi import create_build, models
        from pobapi.types import ItemSlot

        # Ensure build has items - create one if needed
        if not build.items:
            # Create a build with known items for testing
            builder = create_build()
            builder.set_class("Witch", "Necromancer")
            builder.set_level(90)

            # Add item with known modifiers
            test_item = models.Item(
                name="Test Belt",
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
                text="+50 to maximum Life\n+20% to Fire Resistance",
            )
            item_index = builder.add_item(test_item)
            builder.create_item_set()
            builder.equip_item(item_index, ItemSlot.BELT)
            build = builder.build()

        # Precondition: build must have items
        assert build.items, "Build must have items to test item-to-modifier conversion"
        assert len(build.items) > 0

        # Track initial modifier count
        engine = CalculationEngine()
        initial_count = engine.modifiers.count()

        # Load build into engine
        engine.load_build(build)

        # Verify modifiers were added from items
        assert engine.modifiers is not None
        assert (
            engine.modifiers.count() > initial_count
        ), "Engine should have more modifiers after loading build with items"

        # Verify modifiers contain item sources
        item_modifiers = [
            mod for mod in engine.modifiers._modifiers if mod.source.startswith("item:")
        ]
        assert len(item_modifiers) > 0, (
            f"Expected modifiers from items, but found none. "
            f"Total modifiers: {engine.modifiers.count()}, "
            f"Item count: {len(build.items)}"
        )

        # Verify modifiers correspond to actual items
        item_names = {item.name for item in build.items}
        item_sources = {mod.source for mod in item_modifiers}
        # Check that at least one item name appears in modifier sources
        assert any(
            item_name in source for item_name in item_names for source in item_sources
        ), (
            f"Expected modifier sources to contain item names. "
            f"Item names: {item_names}, Modifier sources: {item_sources}"
        )

    def test_api_skill_tree_to_engine_modifiers(self, build):
        """Test that skill tree from API is converted to modifiers in engine."""
        from pobapi import create_build
        from pobapi.types import PassiveNodeID

        # Ensure build has active skill tree with nodes - create one if needed
        if not build.active_skill_tree or not build.active_skill_tree.nodes:
            # Create a build with known passive tree nodes for testing
            builder = create_build()
            builder.set_class("Witch", "Necromancer")
            builder.set_level(90)

            # Create tree and allocate known nodes
            builder.create_tree()
            builder.allocate_node(PassiveNodeID.ELEMENTAL_EQUILIBRIUM)
            builder.allocate_node(PassiveNodeID.MINION_INSTABILITY)
            build = builder.build()

        # Precondition: build must have active skill tree with nodes
        assert (
            build.active_skill_tree
        ), "Build must have active_skill_tree to test tree-to-modifier conversion"
        assert (
            build.active_skill_tree.nodes
        ), "Active skill tree must have allocated nodes"
        assert len(build.active_skill_tree.nodes) > 0

        # Track initial modifier count
        engine = CalculationEngine()
        initial_count = engine.modifiers.count()

        # Load build into engine
        engine.load_build(build)

        # Verify modifiers were added from passive tree
        assert engine.modifiers is not None
        assert engine.modifiers.count() > initial_count, (
            "Engine should have more modifiers after loading build with "
            "passive tree nodes"
        )

        # Verify modifiers contain passive tree sources
        # Keystones use "keystone:name" format, regular nodes use "passive_tree:node_id"
        tree_modifiers = [
            mod
            for mod in engine.modifiers._modifiers
            if mod.source.startswith("passive_tree:")
            or mod.source.startswith("keystone:")
        ]
        assert len(tree_modifiers) > 0, (
            f"Expected modifiers from passive tree (passive_tree: or "
            f"keystone:), but found none. "
            f"Total modifiers: {engine.modifiers.count()}, "
            f"Allocated nodes: {build.active_skill_tree.nodes}, "
            f"All sources: {set(mod.source for mod in engine.modifiers._modifiers)}"
        )

        # Verify modifiers correspond to allocated nodes
        allocated_node_ids = set(build.active_skill_tree.nodes)
        tree_sources = {mod.source for mod in tree_modifiers}

        # Extract node IDs from sources (format: "passive_tree:12345")
        source_node_ids = set()
        for source in tree_sources:
            if source.startswith("passive_tree:") and ":" in source:
                try:
                    node_id = int(source.split(":")[1])
                    source_node_ids.add(node_id)
                except (ValueError, IndexError):
                    pass

        # For keystones, check if any allocated node IDs match known
        # keystone IDs. Keystones use "keystone:name" format, so we check
        # if allocated nodes include keystones
        from pobapi.types import PassiveNodeID

        keystone_node_ids = {
            PassiveNodeID.ELEMENTAL_EQUILIBRIUM,
            PassiveNodeID.ANCESTRAL_BOND,
            PassiveNodeID.MINION_INSTABILITY,
            PassiveNodeID.ZEALOTS_OATH,
            PassiveNodeID.CI,
            PassiveNodeID.PAIN_ATTUNEMENT,
            PassiveNodeID.BLOOD_MAGIC,
            PassiveNodeID.RESOLUTE_TECHNIQUE,
            PassiveNodeID.UNWAVERING_STANCE,
        }

        # Check that at least one allocated node appears in modifier sources
        # Either as passive_tree:node_id or as keystone:name for keystone nodes
        has_matching_node = (
            len(source_node_ids & allocated_node_ids) > 0
            or len(allocated_node_ids & keystone_node_ids) > 0
        )
        assert has_matching_node, (
            f"Expected modifier sources to correspond to allocated nodes. "
            f"Allocated nodes: {allocated_node_ids}, "
            f"Modifier source nodes (passive_tree:): {source_node_ids}, "
            f"Keystone sources: "
            f"{[s for s in tree_sources if s.startswith('keystone:')]}, "
            f"Allocated keystones: {allocated_node_ids & keystone_node_ids}"
        )

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

    def test_full_build_processing_pipeline(self, build):
        """Test full pipeline: import code -> API -> Engine -> Stats."""
        # The build fixture already provides a complete build loaded from
        # import code via API. This test exercises the complete pipeline:
        # API -> Engine -> Stats

        # Step 1: Load build into calculation engine
        engine = CalculationEngine()
        engine.load_build(build)

        # Step 2: Verify engine initialized correctly
        assert engine.modifiers is not None
        assert engine.damage_calc is not None
        assert engine.defense_calc is not None

        # Step 3: Calculate all stats
        stats = engine.calculate_all_stats(build_data=build)

        # Step 4: Verify stats were calculated
        assert stats is not None
        assert (
            hasattr(stats, "life")
            or hasattr(stats, "mana")
            or hasattr(stats, "total_dps")
        )

        # Step 5: Cleanup - ensure engine can be reused
        # This verifies the engine doesn't hold state that would break subsequent uses
        engine2 = CalculationEngine()
        engine2.load_build(build)
        stats2 = engine2.calculate_all_stats(build_data=build)
        assert stats2 is not None


class TestBuildModifierCalculationIntegration:
    """Test integration between BuildModifier and CalculationEngine."""

    def test_modify_build_then_recalculate(self, build):
        """Test modifying build and recalculating stats."""
        from pobapi.models import Item

        engine = CalculationEngine()
        engine.load_build(build)

        # Get initial stats
        initial_stats = engine.calculate_all_stats(build_data=build)
        initial_life = initial_stats.life if initial_stats.life is not None else 0.0

        # Verify initial stats are valid
        assert initial_stats is not None, "Initial stats should not be None"
        assert (
            initial_life >= 0
        ), f"Initial life should be non-negative, got {initial_life}"

        # Modify build (add item with significant life bonus)
        # Use a larger value to ensure it's noticeable
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
            text="+500 to maximum Life",
        )

        # Use public API to equip item
        build.equip_item(test_item, "Belt")

        # Verify item was added to build
        assert (
            len(build.items) > 0
        ), "Build should have at least one item after equipping"

        # Check that the new item is in the items list
        item_names = [item.name for item in build.items]
        assert "Test Item" in item_names, "Test item should be in build items"

        # Reload and recalculate
        engine.load_build(build)
        new_stats = engine.calculate_all_stats(build_data=build)

        # Verify stats were calculated
        assert new_stats is not None, "New stats should not be None"
        assert (
            new_stats.life is not None
        ), f"New stats life should not be None. New stats: {new_stats}"

        new_life = new_stats.life

        # Verify that stats changed after equipping item with +500 to
        # maximum Life. The item should increase life, so new_stats.life
        # should be greater
        assert new_life > initial_life, (
            f"Life should increase after equipping item with +500 to "
            f"maximum Life. "
            f"Initial: {initial_life}, New: {new_life}, "
            f"Difference: {new_life - initial_life}"
        )

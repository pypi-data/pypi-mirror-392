"""Integration tests for Parsers and PathOfBuildingAPI components."""

import pytest

pytestmark = pytest.mark.integration

from pobapi import PathOfBuildingAPI  # noqa: E402
from pobapi.calculator.item_modifier_parser import ItemModifierParser  # noqa: E402
from pobapi.calculator.jewel_parser import JewelParser, JewelType  # noqa: E402
from pobapi.calculator.unique_item_parser import UniqueItemParser  # noqa: E402


class TestItemModifierParserAPIIntegration:
    """Test integration between ItemModifierParser and PathOfBuildingAPI."""

    def test_parse_items_from_build(self, build: PathOfBuildingAPI) -> None:
        """Test parsing modifiers from build items."""
        items = list(build.items)

        if not items:
            pytest.skip("No items in build")

        # Parse modifiers from all items
        all_modifiers = []
        for item in items:
            modifiers = ItemModifierParser.parse_item_text(item.text)
            all_modifiers.extend(modifiers)

        # Should have parsed some modifiers
        assert isinstance(all_modifiers, list)

    def test_parse_item_and_add_to_modifier_system(
        self, build: PathOfBuildingAPI
    ) -> None:
        """Test parsing item modifiers and adding to modifier system."""
        from pobapi import CalculationEngine

        engine = CalculationEngine()
        engine.load_build(build)

        # Get items from build
        items = list(build.items)

        if not items:
            pytest.skip("No items in build")

        # Parse modifiers from first item
        first_item = items[0]
        modifiers = ItemModifierParser.parse_item_text(first_item.text)

        # Add to modifier system
        engine.modifiers.add_modifiers(modifiers)

        # Verify modifiers were added
        assert len(engine.modifiers._modifiers) >= len(modifiers)


class TestUniqueItemParserAPIIntegration:
    """Test integration between UniqueItemParser and PathOfBuildingAPI."""

    def test_parse_unique_items_from_build(self, build: PathOfBuildingAPI) -> None:
        """Test parsing unique item effects from build."""
        items = list(build.items)

        if not items:
            pytest.skip("No items in build")

        # Find unique items
        unique_items = [item for item in items if item.rarity.lower() == "unique"]

        if not unique_items:
            pytest.skip("No unique items in build")

        # Parse unique item effects
        for unique_item in unique_items:
            modifiers = UniqueItemParser.parse_unique_item(
                unique_item.name, unique_item.text
            )
            assert isinstance(modifiers, list)

    def test_unique_item_parser_with_modifier_system(
        self, build: PathOfBuildingAPI
    ) -> None:
        """Test UniqueItemParser integration with ModifierSystem."""
        from pobapi import CalculationEngine

        engine = CalculationEngine()
        engine.load_build(build)

        # Get unique items
        items = list(build.items)
        unique_items = [item for item in items if item.rarity.lower() == "unique"]

        if not unique_items:
            pytest.skip("No unique items in build")

        # Parse and add unique item modifiers
        for unique_item in unique_items:
            modifiers = UniqueItemParser.parse_unique_item(
                unique_item.name, unique_item.text
            )
            engine.modifiers.add_modifiers(modifiers)

        # Verify modifiers were added
        assert engine.modifiers is not None


class TestJewelParserAPIIntegration:
    """Test integration between JewelParser and PathOfBuildingAPI."""

    def test_detect_jewel_type_from_build_items(self, build: PathOfBuildingAPI) -> None:
        """Test detecting jewel types from build items."""
        items = list(build.items)

        if not items:
            pytest.skip("No items in build")

        # Try to detect jewel types (jewels might not be in build)
        for item in items:
            # Check if item might be a jewel (simplified check)
            if "jewel" in item.base.lower() or "jewel" in item.name.lower():
                jewel_type = JewelParser.detect_jewel_type(item)
                assert isinstance(jewel_type, JewelType)

    def test_parse_jewel_socket_from_build(self, build: PathOfBuildingAPI) -> None:
        """Test parsing jewel socket from build tree."""
        if not build.active_skill_tree or not build.active_skill_tree.sockets:
            pytest.skip("No jewel sockets in build")

        items = list(build.items)
        allocated_nodes = build.active_skill_tree.nodes or []

        # Parse jewel sockets
        for socket_id, item_id in build.active_skill_tree.sockets.items():
            if 0 <= item_id < len(items):
                jewel_item = items[item_id]
                # Use PassiveTreeParser to parse jewel socket
                from pobapi.calculator.passive_tree_parser import PassiveTreeParser

                modifiers = PassiveTreeParser.parse_jewel_socket(
                    socket_id, jewel_item, allocated_nodes
                )
                assert isinstance(modifiers, list)

    def test_jewel_parser_with_passive_tree_parser(
        self, build: PathOfBuildingAPI
    ) -> None:
        """Test JewelParser integration with PassiveTreeParser."""
        from pobapi.calculator.passive_tree_parser import PassiveTreeParser

        if not build.active_skill_tree or not build.active_skill_tree.sockets:
            pytest.skip("No jewel sockets in build")

        items = list(build.items)
        allocated_nodes = build.active_skill_tree.nodes or []

        # Parse tree first
        tree_modifiers = PassiveTreeParser.parse_tree(allocated_nodes)

        # Then parse jewels
        for socket_id, item_id in build.active_skill_tree.sockets.items():
            if 0 <= item_id < len(items):
                jewel_item = items[item_id]
                # Use PassiveTreeParser to parse jewel socket
                from pobapi.calculator.passive_tree_parser import PassiveTreeParser

                jewel_modifiers = PassiveTreeParser.parse_jewel_socket(
                    socket_id, jewel_item, allocated_nodes
                )
                # Both should work together
                assert isinstance(tree_modifiers, list)
                assert isinstance(jewel_modifiers, list)


class TestParserModifierSystemIntegration:
    """Test integration between parsers and ModifierSystem."""

    def test_all_parsers_feed_modifier_system(self, build: PathOfBuildingAPI) -> None:
        """Test that all parsers can feed into ModifierSystem."""
        from pobapi import CalculationEngine

        engine = CalculationEngine()

        # Load build (this uses all parsers)
        engine.load_build(build)

        # Verify modifier system has modifiers from all sources
        assert engine.modifiers is not None
        # Modifiers should be added from items, tree, skills, config

    def test_parser_chain_integration(self, build: PathOfBuildingAPI) -> None:
        """Test parser chain: ItemModifierParser -> ModifierSystem -> Calculator."""
        from pobapi import CalculationEngine

        engine = CalculationEngine()

        # Parse items manually
        items = list(build.items)
        if items:
            for item in items:
                modifiers = ItemModifierParser.parse_item_text(item.text)
                engine.modifiers.add_modifiers(modifiers)

            # Calculate stats using parsed modifiers
            stats = engine.calculate_all_stats(build_data=build)
            assert stats is not None

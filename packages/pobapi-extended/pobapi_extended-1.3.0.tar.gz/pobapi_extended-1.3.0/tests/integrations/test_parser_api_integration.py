"""Integration tests for Parsers and PathOfBuildingAPI components."""

import pytest

pytestmark = pytest.mark.integration

from pobapi import PathOfBuildingAPI  # noqa: E402
from pobapi.calculator.item_modifier_parser import ItemModifierParser  # noqa: E402
from pobapi.calculator.jewel_parser import JewelParser, JewelType  # noqa: E402
from pobapi.calculator.modifiers import Modifier, ModifierType  # noqa: E402
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

        # Verify parsing occurred - should have at least some modifiers
        assert (
            len(all_modifiers) > 0
        ), "Expected at least one modifier to be parsed from items"

        # Verify modifier structure - each modifier should be a Modifier
        # object with required attributes
        for modifier in all_modifiers:
            assert isinstance(
                modifier, Modifier
            ), f"Expected Modifier object, got {type(modifier)}"
            assert (
                isinstance(modifier.stat, str) and modifier.stat
            ), "Modifier must have non-empty stat name"
            assert isinstance(
                modifier.value, int | float
            ), "Modifier must have numeric value"
            assert isinstance(
                modifier.mod_type, ModifierType
            ), "Modifier must have valid ModifierType"
            assert (
                isinstance(modifier.source, str) and modifier.source
            ), "Modifier must have non-empty source"

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
        assert engine.modifiers.count() >= len(modifiers)


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

        # Record initial modifier count before adding unique item modifiers
        initial_modifier_count = engine.modifiers.count()

        # Parse and add unique item modifiers
        for unique_item in unique_items:
            modifiers = UniqueItemParser.parse_unique_item(
                unique_item.name, unique_item.text
            )
            assert isinstance(modifiers, list), "Expected list of modifiers from parser"

            # Record modifier count before adding this item's modifiers
            modifier_count_before = engine.modifiers.count()

            # Add modifiers to the system
            engine.modifiers.add_modifiers(modifiers)

            # Verify modifiers were actually added (count increased or
            # modifiers present)
            modifier_count_after = engine.modifiers.count()
            delta = modifier_count_after - modifier_count_before

            # Assert that modifiers were added (delta > 0) or at least one
            # modifier from parsed set exists
            if len(modifiers) > 0:
                assert delta > 0, (
                    f"Expected modifier count to increase after adding "
                    f"{len(modifiers)} modifiers from {unique_item.name}, "
                    f"but count remained {modifier_count_before}"
                )

                # Verify at least one modifier from parsed set exists in the system
                # by checking if any modifier stat appears in the system
                parsed_stats = {mod.stat for mod in modifiers}
                found_stats = {
                    stat
                    for stat in parsed_stats
                    if len(engine.modifiers.get_modifiers(stat)) > 0
                }
                assert len(found_stats) > 0, (
                    f"Expected at least one modifier stat from parsed set "
                    f"{parsed_stats} to be present in modifier system for "
                    f"{unique_item.name}"
                )

        # Verify total modifier count increased from initial state
        final_modifier_count = engine.modifiers.count()
        assert final_modifier_count > initial_modifier_count, (
            f"Expected modifier count to increase from initial "
            f"{initial_modifier_count} to at least "
            f"{initial_modifier_count + 1}, but got {final_modifier_count}"
        )


class TestJewelParserAPIIntegration:
    """Test integration between JewelParser and PathOfBuildingAPI."""

    def test_detect_jewel_type_from_build_items(
        self, build_with_jewels: PathOfBuildingAPI
    ) -> None:
        """Test detecting jewel types from build items."""
        items = list(build_with_jewels.items)

        if not items:
            pytest.skip("No items in build")

        # Collect all jewels first
        jewels = [
            item
            for item in items
            if "jewel" in item.base.lower() or "jewel" in item.name.lower()
        ]

        if not jewels:
            pytest.skip("No jewels found in build items")

        # Iterate over filtered jewels and validate jewel type detection
        for jewel in jewels:
            jewel_type = JewelParser.detect_jewel_type(jewel.text)
            # JewelType is a class with constants, not an Enum
            assert jewel_type in (
                JewelType.NORMAL,
                JewelType.RADIUS,
                JewelType.CONVERSION,
                JewelType.TIMELESS,
            ), f"Invalid jewel type: {jewel_type}"

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

        # Verify that modifiers were actually populated by checking common
        # stats. Try to get modifiers for several common stats that are
        # typically present in builds
        common_stats = [
            "Life",
            "EnergyShield",
            "Mana",
            "PhysicalDamage",
            "CritChance",
            "AccuracyRating",
            "Armour",
            "Evasion",
            "Resist",
            "Strength",
            "Dexterity",
            "Intelligence",
            "MovementSpeed",
            "AttackSpeed",
        ]

        # Check that at least one common stat has modifiers
        modifiers_found = False
        for stat in common_stats:
            modifiers = engine.modifiers.get_modifiers(stat)
            if len(modifiers) > 0:
                modifiers_found = True
                break

        assert modifiers_found, (
            "Expected modifiers to be populated after load_build, "
            "but no modifiers found for common stats"
        )

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

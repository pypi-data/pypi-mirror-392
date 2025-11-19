"""Integration tests for TreesParser and related components."""

import pytest
from lxml.etree import fromstring

from pobapi import PathOfBuildingAPI
from pobapi.parsers import TreesParser

pytestmark = pytest.mark.integration


class TestTreesParserAPIIntegration:
    """Test integration between TreesParser and PathOfBuildingAPI."""

    def test_parse_trees_from_build(self, build: PathOfBuildingAPI) -> None:
        """Test parsing trees from build XML."""
        xml_root = build.xml

        # Parse trees using TreesParser
        trees = TreesParser.parse_trees(xml_root)

        # Should return list of tree data
        assert isinstance(trees, list)
        assert len(trees) > 0

        # Verify tree structure
        for tree in trees:
            assert "url" in tree or "nodes" in tree
            assert "nodes" in tree
            assert "sockets" in tree

    def test_trees_parser_with_path_of_building_api(
        self, build: PathOfBuildingAPI
    ) -> None:
        """Test TreesParser integration with PathOfBuildingAPI."""
        xml_root = build.xml

        # Parse trees
        trees = TreesParser.parse_trees(xml_root)

        # Compare with API's trees property
        api_trees = list(build.trees)

        # Should have same number of trees
        assert len(trees) == len(api_trees)

        # Verify structure matches
        for parsed_tree, api_tree in zip(trees, api_trees, strict=True):
            assert parsed_tree["nodes"] == api_tree.nodes
            assert parsed_tree["sockets"] == api_tree.sockets

    def test_trees_parser_with_active_tree(self, build: PathOfBuildingAPI) -> None:
        """Test TreesParser with active skill tree."""
        xml_root = build.xml

        # Parse trees
        trees = TreesParser.parse_trees(xml_root)

        # Get active tree from API
        active_tree = build.active_skill_tree

        # Find corresponding parsed tree
        tree_element = xml_root.find("Tree")
        if tree_element is None:
            pytest.fail("Tree element not found in XML root")

        active_spec_attr = tree_element.get("activeSpec")
        if active_spec_attr is None:
            pytest.fail("activeSpec attribute not found in Tree element")

        active_spec_index = int(active_spec_attr) - 1
        if 0 <= active_spec_index < len(trees):
            parsed_active_tree = trees[active_spec_index]
            assert parsed_active_tree["nodes"] == active_tree.nodes
            assert parsed_active_tree["sockets"] == active_tree.sockets
        else:
            pytest.fail(
                f"Invalid active_spec_index: active_spec_attr={active_spec_attr}, "
                f"computed active_spec_index={active_spec_index}, "
                f"len(trees)={len(trees)}"
            )


class TestTreesParserDefaultBuildParserIntegration:
    """Test integration between TreesParser and DefaultBuildParser."""

    def test_default_parser_uses_trees_parser(self, sample_xml: str) -> None:
        """Test that DefaultBuildParser uses TreesParser internally."""
        from pobapi.parsers import DefaultBuildParser

        xml_root = fromstring(sample_xml.encode())
        parser = DefaultBuildParser()

        # Parse trees using DefaultBuildParser
        trees = parser.parse_trees(xml_root)

        # Should return same structure as TreesParser
        trees_direct = TreesParser.parse_trees(xml_root)

        assert len(trees) == len(trees_direct)
        for tree, tree_direct in zip(trees, trees_direct, strict=True):
            assert tree["nodes"] == tree_direct["nodes"]
            assert tree["sockets"] == tree_direct["sockets"]


class TestTreesParserBuildFactoryIntegration:
    """Test integration between TreesParser and BuildFactory."""

    def test_factory_uses_trees_parser(self, sample_xml: str) -> None:
        """Test that BuildFactory uses TreesParser through DefaultBuildParser."""
        from pobapi.factory import BuildFactory

        xml_bytes = sample_xml.encode()
        factory = BuildFactory()

        # Create build using factory
        build = factory.from_xml_bytes(xml_bytes)

        # Parse trees directly
        trees = TreesParser.parse_trees(build.xml)

        # Compare with build's trees
        build_trees = list(build.trees)

        assert len(trees) == len(build_trees)
        for parsed_tree, build_tree in zip(trees, build_trees, strict=True):
            assert parsed_tree["nodes"] == build_tree.nodes


class TestTreesParserCalculationEngineIntegration:
    """Test integration between TreesParser and CalculationEngine."""

    def test_trees_parser_feeds_calculation_engine(
        self, build: PathOfBuildingAPI
    ) -> None:
        """Test that trees parsed by TreesParser feed into CalculationEngine."""
        from pobapi import CalculationEngine

        # Parse trees
        trees = TreesParser.parse_trees(build.xml)

        # Load build into engine
        engine = CalculationEngine()
        # Capture modifier count before loading build
        initial_modifier_count = len(engine.modifiers._modifiers)
        engine.load_build(build)

        # Engine should have processed tree modifiers
        assert engine.modifiers is not None

        # Verify tree nodes were processed
        if trees and trees[0]["nodes"]:
            # Engine should have modifiers from tree - count should increase
            final_modifier_count = len(engine.modifiers._modifiers)
            assert final_modifier_count > initial_modifier_count, (
                f"Expected modifiers to be added from tree nodes. "
                f"Initial count: {initial_modifier_count}, "
                f"Final count: {final_modifier_count}"
            )


class TestTreesParserPassiveTreeParserIntegration:
    """Test integration between TreesParser and PassiveTreeParser."""

    def test_trees_parser_with_passive_tree_parser(
        self, build: PathOfBuildingAPI
    ) -> None:
        """Test TreesParser integration with PassiveTreeParser."""
        from pobapi.calculator.passive_tree_parser import PassiveTreeParser

        # Parse trees using TreesParser
        trees = TreesParser.parse_trees(build.xml)

        # Parse tree nodes using PassiveTreeParser
        if trees and trees[0]["nodes"]:
            nodes = trees[0]["nodes"]
            modifiers = PassiveTreeParser.parse_tree(nodes)

            # Should have parsed modifiers
            assert isinstance(modifiers, list)

    def test_trees_parser_jewel_sockets_with_passive_tree_parser(
        self, build: PathOfBuildingAPI
    ) -> None:
        """Test TreesParser jewel sockets with PassiveTreeParser."""
        from pobapi.calculator.passive_tree_parser import PassiveTreeParser

        # Parse trees
        trees = TreesParser.parse_trees(build.xml)

        # Get items for jewel parsing
        items = list(build.items)

        # Process jewel sockets
        for tree in trees:
            if tree["sockets"] and items:
                allocated_nodes = tree["nodes"]
                for socket_id, item_id in tree["sockets"].items():
                    if 0 <= item_id < len(items):
                        jewel_item = items[item_id]
                        modifiers = PassiveTreeParser.parse_jewel_socket(
                            socket_id, jewel_item, allocated_nodes
                        )
                        assert isinstance(modifiers, list)


class TestTreesParserFullIntegration:
    """Test full integration of TreesParser with multiple components."""

    def test_trees_parser_full_workflow(self, sample_xml: str) -> None:
        """Test full workflow: TreesParser -> API -> CalculationEngine."""
        from pobapi import CalculationEngine
        from pobapi.factory import BuildFactory

        # Parse trees
        xml_root = fromstring(sample_xml.encode())
        trees = TreesParser.parse_trees(xml_root)

        # Create build using factory
        factory = BuildFactory()
        build = factory.from_xml_bytes(sample_xml.encode())

        # Verify trees match
        build_trees = list(build.trees)
        assert len(trees) == len(build_trees)

        # Load into calculation engine
        engine = CalculationEngine()
        engine.load_build(build)

        # Engine should have processed everything
        assert engine.modifiers is not None

    def test_trees_parser_with_serialization(self, build: PathOfBuildingAPI) -> None:
        """Test TreesParser with build serialization."""
        # Parse trees
        trees = TreesParser.parse_trees(build.xml)

        # Serialize build
        xml = build.to_xml()

        # Parse serialized XML
        from lxml.etree import fromstring

        xml_root = fromstring(xml)
        trees_serialized = TreesParser.parse_trees(xml_root)

        # Should have same trees
        assert len(trees) == len(trees_serialized)
        for tree, tree_serialized in zip(trees, trees_serialized, strict=True):
            assert tree["nodes"] == tree_serialized["nodes"]

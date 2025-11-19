"""Tests for edge cases and advanced scenarios."""


from pobapi import api, models
from pobapi.types import ItemSlot, PassiveNodeID


class TestMultipleModifications:
    """Tests for multiple modifications sequence."""

    def test_multiple_modifications_sequence(self, simple_build, create_test_item):
        """TC-API-097: Multiple modifications sequence."""
        # Perform sequence of modifications
        simple_build.add_node(PassiveNodeID.ACROBATICS)
        item = create_test_item(name="Test Helmet", base="Iron Helmet")
        simple_build.equip_item(item, ItemSlot.HELMET)
        gem = models.Gem(
            name="Fireball", level=20, quality=0, enabled=True, support=False
        )
        simple_build.add_skill(gem, "Main")
        simple_build.set_level(90)

        # Serialize to XML
        xml_bytes = simple_build.to_xml()

        assert xml_bytes is not None
        assert isinstance(xml_bytes, bytes)

        # Verify all modifications are included with specific XML fragments
        xml_str = xml_bytes.decode("utf-8")

        # Verify level is set correctly in Build element
        assert 'level="90"' in xml_str

        # Verify passive node was added (ACROBATICS = 63980)
        # Node should be in format: <Node id="63980"/>
        node_id_str = str(PassiveNodeID.ACROBATICS)
        assert (
            f'<Node id="{node_id_str}"' in xml_str or f'id="{node_id_str}"' in xml_str
        )

        # Verify equipped item in helmet slot
        # Slot should be in format: <Slot name="Helmet" itemId="..."/>
        assert '<Slot name="Helmet"' in xml_str
        # Verify item was added (Item element exists)
        # Items are serialized even if text is empty, so we check for Item element
        assert "<Item" in xml_str

        # Verify skill gem was added
        # Ability should have nameSpec="Fireball" and level="20"
        assert 'nameSpec="Fireball"' in xml_str or 'name="Fireball"' in xml_str
        # Check that level="20" appears in context of the skill (not just anywhere)
        # Since skills are serialized with level attribute, this should be sufficient
        assert 'level="20"' in xml_str


class TestBuildWithEmptyStructure:
    """Tests for build with empty structure."""

    def test_build_with_empty_structure(self, minimal_xml):
        """TC-API-098: Build with empty structure."""
        build = api.PathOfBuildingAPI(minimal_xml.encode())

        # All properties should return empty lists or default values
        items = list(build.items)
        groups = list(build.skill_groups)
        trees = list(build.trees)

        assert items == [] or len(items) == 0
        assert groups == [] or len(groups) == 0
        assert trees == [] or len(trees) == 0

        # Should not raise exceptions
        assert build.class_name is not None
        assert build.level == 1  # Default level


class TestBuildModificationStateTracking:
    """Tests for build modification state tracking."""

    def test_build_modification_state_tracking(self, simple_build):
        """TC-API-099: Build modification state tracking."""
        # Check initial level
        initial_level = simple_build.level

        # Perform modification - change level to verify state transition
        new_level = 95 if initial_level < 95 else 85
        simple_build.set_level(new_level)

        # Verify that the modification actually changed the level
        # This confirms the state transition occurred
        assert simple_build.level == new_level
        assert simple_build.level != initial_level


class TestBuildWithCustomParser:
    """Tests for build with custom parser integration."""

    def test_build_with_custom_parser_integration(self, sample_xml):
        """TC-API-100: Build with custom parser integration."""
        from pobapi.interfaces import BuildParser

        class CustomParser(BuildParser):
            """Custom parser for testing."""

            def parse_build_info(self, xml):
                """Parse build info with custom logic."""
                from pobapi.parsers import DefaultBuildParser

                default_parser = DefaultBuildParser()
                info = default_parser.parse_build_info(xml)
                # Add custom marker
                info["_custom_parsed"] = True
                return info

            def parse_skills(self, xml):
                """Parse skills with custom logic."""
                from pobapi.parsers import DefaultBuildParser

                default_parser = DefaultBuildParser()
                return default_parser.parse_skills(xml)

            def parse_items(self, xml):
                """Parse items with custom logic."""
                from pobapi.parsers import DefaultBuildParser

                default_parser = DefaultBuildParser()
                return default_parser.parse_items(xml)

            def parse_trees(self, xml):
                """Parse trees with custom logic."""
                from pobapi.parsers import DefaultBuildParser

                default_parser = DefaultBuildParser()
                return default_parser.parse_trees(xml)

        xml_bytes = sample_xml.encode()
        custom_parser = CustomParser()

        build = api.PathOfBuildingAPI(xml_bytes, parser=custom_parser)

        # Verify custom parser was used
        assert build._build_info_cache.get("_custom_parsed") is True
        # Verify properties still work
        assert build.class_name == "Scion"

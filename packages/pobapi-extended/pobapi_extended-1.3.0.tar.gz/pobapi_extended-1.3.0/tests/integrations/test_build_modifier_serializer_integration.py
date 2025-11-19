"""Integration tests for BuildModifier and Serializer components."""

import pytest

pytestmark = pytest.mark.integration

from lxml.etree import fromstring  # noqa: E402

from pobapi import PathOfBuildingAPI  # noqa: E402
from pobapi.models import Item  # noqa: E402
from pobapi.serializers import ImportCodeGenerator  # noqa: E402


class TestBuildModifierSerializerIntegration:
    """Test integration between BuildModifier and Serializers."""

    def test_modify_build_then_serialize_xml(self, build: PathOfBuildingAPI) -> None:
        """Test modifying build and serializing to XML."""
        # Add item via BuildModifier
        test_item = Item(
            name="Test Ring",
            base="Iron Ring",
            rarity="Rare",
            uid="test-ring-1",
            shaper=False,
            elder=False,
            crafted=False,
            quality=20,
            sockets=None,
            level_req=1,
            item_level=84,
            implicit=None,
            text="+20 to Strength\n+30 to maximum Life",
        )

        build._modifier.equip_item(test_item, "Ring1")

        # Serialize to XML
        xml = build.to_xml()
        assert xml is not None
        assert len(xml) > 0

        # Verify item is in XML
        xml_root = fromstring(xml)
        items_elem = xml_root.find("Items")
        assert items_elem is not None

    def test_modify_build_then_generate_import_code(
        self, build: PathOfBuildingAPI
    ) -> None:
        """Test modifying build and generating import code."""
        # Add item via BuildModifier
        test_item = Item(
            name="Test Belt",
            base="Leather Belt",
            rarity="Rare",
            uid="test-belt-1",
            shaper=False,
            elder=False,
            crafted=False,
            quality=None,
            sockets=None,
            level_req=1,
            item_level=84,
            implicit=None,
            text="+50 to maximum Life",
        )

        build._modifier.equip_item(test_item, "Belt")

        # Generate import code
        import_code = ImportCodeGenerator.generate_from_api(build)
        assert import_code is not None
        assert len(import_code) > 0

    def test_modify_build_multiple_times_then_serialize(
        self, build: PathOfBuildingAPI
    ) -> None:
        """Test multiple modifications and serialization."""
        # Add multiple items
        items = [
            Item(
                name=f"Test Item {i}",
                base="Iron Ring",
                rarity="Rare",
                uid=f"test-{i}",
                shaper=False,
                elder=False,
                crafted=False,
                quality=None,
                sockets=None,
                level_req=1,
                item_level=84,
                implicit=None,
                text=f"+{10 * i} to Strength",
            )
            for i in range(3)
        ]

        slots = ["Ring1", "Ring2", "Amulet"]
        for item, slot in zip(items, slots):
            build._modifier.equip_item(item, slot)

        # Serialize
        xml = build.to_xml()
        assert xml is not None

        # Generate import code
        import_code = ImportCodeGenerator.generate_from_api(build)
        assert import_code is not None

    def test_modify_build_add_skill_then_serialize(
        self, build: PathOfBuildingAPI
    ) -> None:
        """Test adding skill and serializing."""
        from pobapi.models import Gem

        # Add skill gem
        test_gem = Gem(
            name="Arc",
            enabled=True,
            level=20,
            quality=20,
            support=False,
        )

        build._modifier.add_skill(test_gem, "Test Group")

        # Serialize
        xml = build.to_xml()
        assert xml is not None

        # Verify skill is in XML
        xml_root = fromstring(xml)
        skills_elem = xml_root.find("Skills")
        assert skills_elem is not None


class TestBuildFactoryBuilderIntegration:
    """Test integration between BuildFactory and BuildBuilder."""

    def test_factory_creates_builder(self) -> None:
        """Test BuildFactory can work with BuildBuilder."""
        from pobapi import create_build
        from pobapi.factory import BuildFactory

        # Create build using factory pattern
        factory = BuildFactory()

        # Create build using builder
        builder = create_build()
        builder.set_class("Witch")
        builder.set_level(90)

        # Get API instance
        build = builder.build()

        # Factory should be able to work with it
        xml = factory.from_xml_bytes(build.to_xml())
        assert xml is not None

    def test_factory_and_builder_round_trip(self) -> None:
        """Test round-trip: Factory -> Builder -> Factory."""
        from pobapi import create_build
        from pobapi.factory import BuildFactory

        # Create build with builder
        builder = create_build()
        builder.set_class("Ranger")
        builder.set_level(85)
        build1 = builder.build()

        # Serialize
        xml = build1.to_xml()

        # Create new build from XML using factory
        factory = BuildFactory()
        build2 = factory.from_xml_bytes(xml)

        # Both should have same class
        assert build1.class_name == build2.class_name
        assert build1.level == build2.level

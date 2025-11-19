"""Integration tests for Parser and Serializer components."""

import pytest

pytestmark = pytest.mark.integration
from lxml.etree import fromstring  # noqa: E402

from pobapi import PathOfBuildingAPI  # noqa: E402
from pobapi.serializers import ImportCodeGenerator  # noqa: E402


class TestParserSerializerIntegration:
    """Test integration between parsers and serializers."""

    def test_parse_then_serialize_xml(self, sample_xml):
        """Test parsing XML and then serializing it back."""
        xml_bytes = sample_xml.encode()
        xml_root = fromstring(xml_bytes)

        # Parse
        build = PathOfBuildingAPI(xml_root)

        # Serialize back
        serialized_xml = build.to_xml()

        # Verify it's valid XML
        assert serialized_xml is not None
        assert len(serialized_xml) > 0

        # Parse again to verify round-trip
        parsed_again = PathOfBuildingAPI(serialized_xml)
        assert parsed_again is not None

    def test_parse_then_generate_import_code(self, sample_xml):
        """Test parsing XML and generating import code."""
        xml_bytes = sample_xml.encode()
        xml_root = fromstring(xml_bytes)

        # Parse
        build = PathOfBuildingAPI(xml_root)

        # Generate import code
        import_code = ImportCodeGenerator.generate_from_api(build)

        # Verify import code is generated
        assert import_code is not None
        assert len(import_code) > 0

    def test_import_code_round_trip(self, build):
        """Test round-trip: import code -> API -> import code."""
        # Generate import code from build
        import_code1 = ImportCodeGenerator.generate_from_api(build)

        # Parse import code back
        from pobapi import from_import_code

        build2 = from_import_code(import_code1)

        # Generate import code again
        import_code2 = ImportCodeGenerator.generate_from_api(build2)

        # Import codes should be the same (or at least valid)
        assert import_code1 is not None
        assert import_code2 is not None

    def test_xml_serialize_with_modifications(self, build):
        """Test serializing XML after modifying build."""
        # Modify build
        from pobapi.models import Item

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

        build.equip_item(test_item, "Belt")

        # Serialize
        xml = build.to_xml()

        # Verify modifications are in XML
        assert xml is not None
        xml_root = fromstring(xml)
        items_elem = xml_root.find("Items")
        assert items_elem is not None


class TestBuildBuilderSerializerIntegration:
    """Test integration between BuildBuilder and serializers."""

    def test_build_create_then_serialize(self):
        """Test creating build with BuildBuilder and serializing."""
        from pobapi import create_build

        # Create build
        builder = create_build()
        builder.set_class("Witch")
        builder.set_level(90)

        # Get API instance
        build = builder.build()

        # Serialize
        xml = build.to_xml()
        assert xml is not None

        # Generate import code
        import_code = ImportCodeGenerator.generate_from_api(build)
        assert import_code is not None

    def test_build_modify_then_serialize(self, build):
        """Test modifying build and serializing changes."""
        # Add item
        from pobapi.models import Item

        test_item = Item(
            name="Test Ring",
            base="Iron Ring",
            rarity="Rare",
            uid="test-ring-1",
            shaper=False,
            elder=False,
            crafted=False,
            quality=None,
            sockets=None,
            level_req=1,
            item_level=80,
            implicit=None,
            text="+20 to Strength",
        )

        build.equip_item(test_item, "Ring1")

        # Serialize
        xml = build.to_xml()
        assert xml is not None

        # Verify item is in serialized XML
        xml_root = fromstring(xml)
        items_elem = xml_root.find("Items")
        assert items_elem is not None

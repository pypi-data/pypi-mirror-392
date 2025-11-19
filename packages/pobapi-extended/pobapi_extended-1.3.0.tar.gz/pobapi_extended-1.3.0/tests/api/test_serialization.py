"""Tests for serialization methods."""


from pobapi import api, models
from pobapi.types import ItemSlot, PassiveNodeID


class TestToXML:
    """Tests for to_xml method."""

    def test_to_xml_with_modifications(self, simple_build, create_test_item):
        """TC-API-078: Serialize to XML with modifications."""
        # Make several modifications
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
        assert b"<?xml" in xml_bytes

        # Verify modifications are in XML
        xml_str = xml_bytes.decode("utf-8")
        assert "90" in xml_str  # Level should be in XML


class TestToImportCode:
    """Tests for to_import_code method."""

    def test_to_import_code_roundtrip_with_modifications(self, simple_build):
        """Test roundtrip with modifications."""
        # Make modifications
        simple_build.set_level(90)
        simple_build.set_bandit("Alira")

        # Serialize to import code
        import_code = simple_build.to_import_code()

        # Load back
        new_build = api.from_import_code(import_code)

        # Verify modifications are preserved
        assert new_build.level == 90
        assert new_build.bandit == "Alira"

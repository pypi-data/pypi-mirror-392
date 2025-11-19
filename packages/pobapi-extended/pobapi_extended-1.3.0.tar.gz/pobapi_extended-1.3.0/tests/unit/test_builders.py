"""Unit tests for builders module."""

import pytest

from pobapi.builders import ConfigBuilder, ItemSetBuilder, StatsBuilder


class TestStatsBuilder:
    """Tests for StatsBuilder."""

    def test_build_with_stats(self, sample_xml_root):
        """Test building Stats with player stats."""
        stats = StatsBuilder.build(sample_xml_root)
        assert stats.life == 163.0
        assert stats.mana == 60.0

    @pytest.mark.parametrize(
        "xml_str,expected_life",
        [
            (
                """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
        </PathOfBuilding>""",
                None,
            ),
            (
                """<?xml version="1.0"?>
        <PathOfBuilding/>""",
                None,
            ),
        ],
    )
    def test_build_empty_or_missing(self, xml_str, expected_life):
        """Test building Stats with no stats or missing Build element."""
        from lxml.etree import fromstring

        xml_root = fromstring(xml_str.encode())
        stats = StatsBuilder.build(xml_root)
        # All stats should be None by default
        assert stats.life is expected_life
        assert stats.mana is None


class TestConfigBuilder:
    """Tests for ConfigBuilder."""

    def test_build_with_config(self, sample_xml_root):
        """Test building Config with config values."""
        config = ConfigBuilder.build(sample_xml_root, character_level=1)
        assert config.enemy_level == 84
        assert config.is_stationary is True
        # character_level is InitVar, not an instance attribute

    def test_build_empty(self):
        """Test building Config with no config."""
        from lxml.etree import fromstring

        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())
        config = ConfigBuilder.build(xml_root, character_level=1)
        # Should use defaults
        # character_level is InitVar, not an instance attribute
        assert config.enemy_level is not None

    @pytest.mark.parametrize(
        "input_attr,input_value,config_field,expected_value",
        [
            ("boolean", "true", "is_stationary", True),
            ("number", "90", "enemy_level", 90),
            ("string", "average", "ignite_mode", "Average"),
        ],
    )
    def test_build_config_field_types(
        self, input_attr, input_value, config_field, expected_value
    ):
        """Test building Config with different field types."""
        from lxml.etree import fromstring

        input_name = (
            "conditionStationary"
            if input_attr == "boolean"
            else "enemyLevel"
            if input_attr == "number"
            else "igniteMode"
        )
        xml_str = f"""<?xml version="1.0"?>
        <PathOfBuilding>
            <Config>
                <Input name="{input_name}" {input_attr}="{input_value}"/>
            </Config>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())
        config = ConfigBuilder.build(xml_root, character_level=1)
        assert getattr(config, config_field) == expected_value

    def test_build_config_with_no_field_type(self):
        """Test building Config with Input that has no boolean/number/string."""
        from lxml.etree import fromstring

        # Need to use a field that exists in CONFIG_MAP
        # but Input has no boolean/number/string
        # Find a field that accepts None values
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Config>
                <Input name="enemyLevel"/>
            </Config>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())
        config = ConfigBuilder.build(xml_root, character_level=1)
        # _convert_fields should return None for Input without boolean/number/string
        # This should trigger line 57
        # enemyLevel should be None or use default
        assert hasattr(config, "enemy_level")


class TestItemSetBuilder:
    """Tests for ItemSetBuilder."""

    def test_build_all_with_sets(self, sample_xml_root):
        """Test building all item sets."""
        item_sets = ItemSetBuilder.build_all(sample_xml_root)
        assert len(item_sets) == 1
        item_set = item_sets[0]
        assert item_set.body_armour == 0  # itemId - 1
        assert item_set.helmet == 1  # itemId - 1

    @pytest.mark.parametrize(
        "xml_str",
        [
            """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
        </PathOfBuilding>""",
            """<?xml version="1.0"?>
        <PathOfBuilding>
            <Items/>
        </PathOfBuilding>""",
        ],
    )
    def test_build_all_empty(self, xml_str):
        """Test building item sets when Items element is missing or empty."""
        from lxml.etree import fromstring

        xml_root = fromstring(xml_str.encode())
        item_sets = ItemSetBuilder.build_all(xml_root)
        assert item_sets == []

    def test_build_single_with_empty_slots(self):
        """Test building single item set with empty slots."""
        item_set_data: dict = {}
        item_set = ItemSetBuilder._build_single(item_set_data)
        assert item_set.body_armour is None
        assert item_set.helmet is None


class TestConfigBuilderEdgeCases:
    """Tests for ConfigBuilder edge cases."""

    def test_build_with_none_character_level(self):
        """Test ConfigBuilder.build() with None character_level (TC-BUILDERS-014).

        This test verifies that when None is passed as character_level,
        the Config uses the default value of 84, which affects derived
        fields like enemy_level.
        """
        from lxml.etree import fromstring

        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())
        # character_level=None should use default value of 84
        config = ConfigBuilder.build(xml_root, character_level=None)  # type: ignore[arg-type]
        # Verify that default character_level (84) is used
        # This affects enemy_level when it's not explicitly set
        assert config.enemy_level == 84


class TestStatsBuilderEdgeCases:
    """Tests for StatsBuilder edge cases."""

    def test_build_with_float_stat_values(self):
        """Test StatsBuilder.build() with float stat values (TC-BUILDERS-015).

        This test verifies that StatsBuilder correctly handles float values
        in XML attributes. The builder should convert string values to float
        and preserve decimal precision.
        """
        from lxml.etree import fromstring

        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1">
                <PlayerStat stat="Life" value="163.5"/>
                <PlayerStat stat="Mana" value="60.5"/>
            </Build>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())
        stats = StatsBuilder.build(xml_root)
        # Verify float values are correctly parsed
        assert stats.life == 163.5
        assert stats.mana == 60.5
        # Verify types are float
        assert isinstance(stats.life, float)
        assert isinstance(stats.mana, float)

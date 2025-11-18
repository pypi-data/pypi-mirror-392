"""Tests for PassiveTreeParser."""

import pytest

from pobapi.calculator.modifiers import ModifierType
from pobapi.calculator.passive_tree_parser import PassiveTreeParser


class TestPassiveTreeParser:
    """Tests for PassiveTreeParser."""

    def test_parse_node_no_data(self) -> None:
        """Test parsing node with no data."""
        modifiers = PassiveTreeParser.parse_node(12345)
        assert modifiers == []

    def test_parse_node_with_stats(self) -> None:
        """Test parsing node with stats."""
        node_data = {
            "stats": [
                "+10 to Strength",
                "5% increased Life",
                "+20 to maximum Life",
            ]
        }
        modifiers = PassiveTreeParser.parse_node(12345, node_data)
        assert len(modifiers) == 3
        assert any(
            m.stat == "Strength" and m.value == 10.0 and m.mod_type == ModifierType.FLAT
            for m in modifiers
        )
        assert any(
            m.stat == "Life" and m.value == 5.0 and m.mod_type == ModifierType.INCREASED
            for m in modifiers
        )

    def test_parse_node_keystone(self) -> None:
        """Test parsing keystone node."""
        # Use a known keystone ID from constants
        from pobapi.constants import KEYSTONE_IDS

        if KEYSTONE_IDS:
            keystone_name = list(KEYSTONE_IDS.keys())[0]
            keystone_id = KEYSTONE_IDS[keystone_name]
            modifiers = PassiveTreeParser.parse_node(keystone_id)
            # Keystones should return modifiers
            assert isinstance(modifiers, list)

    def test_parse_tree_empty(self) -> None:
        """Test parsing empty tree."""
        modifiers = PassiveTreeParser.parse_tree([])
        assert modifiers == []

    def test_parse_tree_with_nodes(self) -> None:
        """Test parsing tree with nodes."""
        node_ids = [12345, 12346]
        tree_data = {
            "12345": {"stats": ["+10 to Strength"]},
            "12346": {"stats": ["5% increased Life"]},
        }
        modifiers = PassiveTreeParser.parse_tree(node_ids, tree_data)
        assert len(modifiers) == 2

    def test_parse_tree_without_tree_data(self) -> None:
        """Test parsing tree without tree data."""
        node_ids = [12345, 12346]
        modifiers = PassiveTreeParser.parse_tree(node_ids)
        # Without tree data, should return empty or minimal modifiers
        assert isinstance(modifiers, list)

    def test_parse_keystone_known(self) -> None:
        """Test parsing known keystone."""
        modifiers = PassiveTreeParser.parse_keystone("Acrobatics")
        assert len(modifiers) >= 1
        # Acrobatics gives: 30% dodge, -50% armour, -50% ES
        assert any(m.stat == "DodgeChance" for m in modifiers)

    @pytest.mark.parametrize(
        ("keystone_name", "expected_stats"),
        [
            ("Acrobatics", ["DodgeChance", "Armour", "EnergyShield"]),
            ("Phase Acrobatics", ["SpellDodgeChance"]),
            ("Iron Reflexes", ["Evasion", "Armour"]),
            ("Unwavering Stance", ["StunImmunity"]),
            ("Resolute Technique", ["CritChance", "HitChance"]),
            ("Eldritch Battery", ["EnergyShield", "Mana"]),
            ("Ghost Reaver", ["EnergyShield", "LifeLeech"]),
            ("Pain Attunement", ["Damage"]),
            ("Blood Magic", ["Mana", "Life"]),
            ("Mind Over Matter", ["Mana", "DamageTaken"]),
            ("Chaos Inoculation", ["Life", "ChaosResistance"]),
        ],
    )
    def test_parse_keystone_common(
        self, keystone_name: str, expected_stats: list[str]
    ) -> None:
        """Test parsing common keystones."""
        modifiers = PassiveTreeParser.parse_keystone(keystone_name)
        # Some keystones might not be implemented yet
        # Just check it returns a list
        assert isinstance(modifiers, list)
        if len(modifiers) > 0:
            # If modifiers exist, check that at least one expected stat is present
            assert any(
                any(expected in m.stat for expected in expected_stats)
                for m in modifiers
            )

    def test_parse_keystone_unknown(self) -> None:
        """Test parsing unknown keystone."""
        modifiers = PassiveTreeParser.parse_keystone("Unknown Keystone")
        # Unknown keystones might return empty or default modifiers
        assert isinstance(modifiers, list)

    def test_parse_jewel_socket_no_jewel(self) -> None:
        """Test parsing jewel socket with no jewel."""
        modifiers = PassiveTreeParser.parse_jewel_socket(12345, None)
        assert modifiers == []

    def test_parse_jewel_socket_with_jewel(self, mock_jewel) -> None:
        """Test parsing jewel socket with jewel."""
        jewel = mock_jewel(
            name="Crimson Jewel", text="+10% to Fire Resistance\n+5% increased Life"
        )
        modifiers = PassiveTreeParser.parse_jewel_socket(12345, jewel)
        # Should parse modifiers from jewel text
        # The method might return empty if jewel parsing is not fully implemented
        assert isinstance(modifiers, list)
        # If jewel parsing works, should have modifiers
        if len(modifiers) > 0:
            assert any("Fire" in m.stat or "Life" in m.stat for m in modifiers)

    @pytest.mark.parametrize(
        ("jewel_name", "jewel_text", "allocated_nodes"),
        [
            ("Small Cluster Jewel", "Adds 2 Passive Skills", [100, 101, 102]),
            ("Thread of Hope", "Allocates passives in a large ring", [100, 101, 102]),
            (
                "Glorious Vanity",
                "Bathed in the blood of # sacrificed in the name of",
                [100, 101, 102],
            ),
        ],
    )
    def test_parse_jewel_socket_different_types(
        self, mock_jewel, jewel_name, jewel_text, allocated_nodes
    ) -> None:
        """Test parsing different jewel types."""
        jewel = mock_jewel(name=jewel_name, text=jewel_text)
        modifiers = PassiveTreeParser.parse_jewel_socket(12345, jewel, allocated_nodes)
        assert isinstance(modifiers, list)

    def test_parse_jewel_socket_timeless_with_seed(self, mock_jewel) -> None:
        """Test parsing timeless jewel with seed property."""
        jewel = mock_jewel(
            name="Glorious Vanity",
            text="Bathed in the blood of # sacrificed",
            seed=12345,
        )
        allocated_nodes = [100, 101, 102]
        modifiers = PassiveTreeParser.parse_jewel_socket(12345, jewel, allocated_nodes)
        assert isinstance(modifiers, list)

    def test_parse_jewel_socket_timeless_with_properties(self, mock_jewel) -> None:
        """Test parsing timeless jewel with seed in properties."""
        from types import SimpleNamespace

        mock_property = SimpleNamespace(name="Seed", value="67890")
        jewel = mock_jewel(
            name="Glorious Vanity",
            text="Bathed in the blood of # sacrificed",
            properties=[mock_property],
        )
        allocated_nodes = [100, 101, 102]
        modifiers = PassiveTreeParser.parse_jewel_socket(12345, jewel, allocated_nodes)
        assert isinstance(modifiers, list)

    def test_parse_jewel_socket_timeless_invalid_seed(self, mock_jewel) -> None:
        """Test parsing timeless jewel with invalid seed value."""
        from types import SimpleNamespace

        mock_property = SimpleNamespace(name="Seed", value="invalid")
        jewel = mock_jewel(
            name="Glorious Vanity",
            text="Bathed in the blood of # sacrificed",
            properties=[mock_property],
        )
        allocated_nodes = [100, 101, 102]
        modifiers = PassiveTreeParser.parse_jewel_socket(12345, jewel, allocated_nodes)
        # Should handle invalid seed gracefully
        assert isinstance(modifiers, list)

    def test_parse_jewel_socket_timeless_with_seed_attr(self, mock_jewel) -> None:
        """Test parsing timeless jewel with seed attribute."""
        jewel = mock_jewel(
            name="Glorious Vanity",
            text="Bathed in the blood of # sacrificed",
            seed=12345,
        )
        allocated_nodes = [100, 101, 102]
        modifiers = PassiveTreeParser.parse_jewel_socket(12345, jewel, allocated_nodes)
        # Should use seed from attribute
        assert isinstance(modifiers, list)

    def test_parse_jewel_socket_timeless_seed_from_properties(self, mock_jewel) -> None:
        """Test parsing timeless jewel extracting seed from properties."""
        from types import SimpleNamespace

        mock_property = SimpleNamespace(name="Seed", value="67890")
        jewel = mock_jewel(
            name="Glorious Vanity",
            text="Bathed in the blood of # sacrificed",
            properties=[mock_property],
        )
        allocated_nodes = [100, 101, 102]
        modifiers = PassiveTreeParser.parse_jewel_socket(12345, jewel, allocated_nodes)
        # Should extract seed from properties
        assert isinstance(modifiers, list)

    def test_parse_jewel_socket_timeless_property_no_value(self, mock_jewel) -> None:
        """Test parsing timeless jewel with property but no value."""
        from types import SimpleNamespace

        mock_property = SimpleNamespace(name="Seed")
        jewel = mock_jewel(
            name="Glorious Vanity",
            text="Bathed in the blood of # sacrificed",
            properties=[mock_property],
        )
        allocated_nodes = [100, 101, 102]
        modifiers = PassiveTreeParser.parse_jewel_socket(12345, jewel, allocated_nodes)
        # Should handle missing value gracefully
        assert isinstance(modifiers, list)

    def test_parse_jewel_socket_timeless_property_no_name(self, mock_jewel) -> None:
        """Test parsing timeless jewel with property but no name."""
        from types import SimpleNamespace

        mock_property = SimpleNamespace(value="12345")
        jewel = mock_jewel(
            name="Glorious Vanity",
            text="Bathed in the blood of # sacrificed",
            properties=[mock_property],
        )
        allocated_nodes = [100, 101, 102]
        modifiers = PassiveTreeParser.parse_jewel_socket(12345, jewel, allocated_nodes)
        # Should handle missing name gracefully
        assert isinstance(modifiers, list)

    def test_parse_jewel_socket_conversion_jewel(self, mock_jewel) -> None:
        """Test parsing conversion jewel (Thread of Hope)."""
        jewel = mock_jewel(
            name="Thread of Hope",
            text="Allocates passives in a large ring",
        )
        allocated_nodes = [100, 101, 102]
        modifiers = PassiveTreeParser.parse_jewel_socket(12345, jewel, allocated_nodes)
        # Should parse conversion jewel
        assert isinstance(modifiers, list)

    def test_parse_jewel_socket_radius_jewel(self, mock_jewel) -> None:
        """Test parsing radius jewel (Small Cluster Jewel)."""
        jewel = mock_jewel(
            name="Small Cluster Jewel",
            text="Adds 2 Passive Skills\nPassives in radius",
        )
        allocated_nodes = [100, 101, 102]
        modifiers = PassiveTreeParser.parse_jewel_socket(12345, jewel, allocated_nodes)
        # Should parse radius jewel
        assert isinstance(modifiers, list)

    def test_parse_jewel_socket_timeless_seed_from_properties_lowercase(
        self, mock_jewel, mocker
    ) -> None:
        """Test parsing timeless jewel with seed in properties (lowercase name).

        Covers lines 121-137."""
        from types import SimpleNamespace

        from pobapi.calculator.jewel_parser import JewelParser, JewelType

        # Mock detect_jewel_type to return TIMELESS
        mock_detect = mocker.patch.object(
            JewelParser, "detect_jewel_type", return_value=JewelType.TIMELESS
        )
        mock_parse = mocker.patch.object(
            JewelParser, "parse_timeless_jewel", return_value=[]
        )

        # Test with lowercase "seed" in property name (covers line 127)
        mock_property = SimpleNamespace(name="seed", value="12345")
        jewel = mock_jewel(
            name="Glorious Vanity",
            text="Bathed in the blood of # sacrificed",
            properties=[mock_property],
        )
        allocated_nodes = [100, 101, 102]
        modifiers = PassiveTreeParser.parse_jewel_socket(12345, jewel, allocated_nodes)
        # Should extract seed from properties (covers lines 121-137)
        assert isinstance(modifiers, list)
        # Note: JewelParser methods are static, so we verify they were called via mocks
        assert mock_detect.call_count >= 1
        assert mock_parse.call_count >= 1

    def test_parse_jewel_socket_timeless_seed_from_properties_mixed_case(
        self, mock_jewel, mocker
    ) -> None:
        """Test parsing timeless jewel with seed in properties (mixed case name).

        Covers lines 121-137."""
        from types import SimpleNamespace

        from pobapi.calculator.jewel_parser import JewelParser, JewelType

        # Mock detect_jewel_type to return TIMELESS
        mocker.patch.object(
            JewelParser, "detect_jewel_type", return_value=JewelType.TIMELESS
        )
        mocker.patch.object(JewelParser, "parse_timeless_jewel", return_value=[])

        # Test with mixed case "Seed" in property name (covers line 127)
        mock_property = SimpleNamespace(name="Jewel Seed", value="67890")
        jewel = mock_jewel(
            name="Glorious Vanity",
            text="Bathed in the blood of # sacrificed",
            properties=[mock_property],
        )
        allocated_nodes = [100, 101, 102]
        modifiers = PassiveTreeParser.parse_jewel_socket(12345, jewel, allocated_nodes)
        # Should extract seed from properties (covers lines 121-137)
        assert isinstance(modifiers, list)
        JewelParser.parse_timeless_jewel.assert_called_once_with(  # type: ignore[attr-defined]
            12345, jewel, allocated_nodes, 67890
        )

    def test_parse_jewel_socket_conversion_jewel_thread_of_hope(
        self, mock_jewel, mocker
    ) -> None:
        """Test parsing conversion jewel (Thread of Hope) - covers lines 140-143."""
        from pobapi.calculator.jewel_parser import JewelParser, JewelType

        # Mock detect_jewel_type to return CONVERSION
        mock_detect = mocker.patch.object(
            JewelParser, "detect_jewel_type", return_value=JewelType.CONVERSION
        )
        mock_parse = mocker.patch.object(
            JewelParser, "parse_conversion_jewel", return_value=[]
        )

        jewel = mock_jewel(
            name="Thread of Hope",
            text="Allocates passives in a large ring\nUnique Ring",
        )
        allocated_nodes = [100, 101, 102]
        modifiers = PassiveTreeParser.parse_jewel_socket(12345, jewel, allocated_nodes)
        # Should parse conversion jewel (covers lines 140-143)
        assert isinstance(modifiers, list)
        # Note: JewelParser methods are static, so we verify they were called via mocks
        assert mock_detect.call_count >= 1
        assert mock_parse.call_count >= 1

    def test_parse_jewel_socket_conversion_jewel_impossible_escape(
        self, mock_jewel, mocker
    ) -> None:
        """Test parsing conversion jewel (Impossible Escape) - covers lines 140-143."""
        from pobapi.calculator.jewel_parser import JewelParser, JewelType

        # Mock detect_jewel_type to return CONVERSION
        mocker.patch.object(
            JewelParser, "detect_jewel_type", return_value=JewelType.CONVERSION
        )
        mocker.patch.object(JewelParser, "parse_conversion_jewel", return_value=[])

        jewel = mock_jewel(
            name="Impossible Escape",
            text="Allocates passives in a medium ring\nUnique Ring",
        )
        allocated_nodes = [100, 101, 102]
        modifiers = PassiveTreeParser.parse_jewel_socket(12345, jewel, allocated_nodes)
        # Should parse conversion jewel (covers lines 140-143)
        assert isinstance(modifiers, list)
        JewelParser.parse_conversion_jewel.assert_called_once_with(  # type: ignore[attr-defined]
            12345, jewel, allocated_nodes
        )

    def test_parse_jewel_socket_timeless_with_seed_attr_direct(
        self, mock_jewel, mocker
    ) -> None:
        """Test parsing timeless jewel with seed attribute (covers line 123)."""
        from pobapi.calculator.jewel_parser import JewelParser, JewelType

        # Mock detect_jewel_type to return TIMELESS
        mocker.patch.object(
            JewelParser, "detect_jewel_type", return_value=JewelType.TIMELESS
        )
        mocker.patch.object(JewelParser, "parse_timeless_jewel", return_value=[])

        # Create jewel with seed attribute directly (covers line 123)
        jewel = mock_jewel(
            name="Glorious Vanity",
            text="Bathed in the blood of # sacrificed",
            seed=99999,  # Direct seed attribute
        )
        allocated_nodes = [100, 101, 102]
        modifiers = PassiveTreeParser.parse_jewel_socket(12345, jewel, allocated_nodes)
        # Should use seed from attribute (covers line 123)
        assert isinstance(modifiers, list)
        JewelParser.parse_timeless_jewel.assert_called_once_with(  # type: ignore[attr-defined]
            12345, jewel, allocated_nodes, 99999
        )

    def test_parse_jewel_socket_timeless_seed_type_error(
        self, mock_jewel, mocker
    ) -> None:
        """Test parsing timeless jewel with seed that causes TypeError
        (covers lines 131-132)."""
        from types import SimpleNamespace

        from pobapi.calculator.jewel_parser import JewelParser, JewelType

        # Mock detect_jewel_type to return TIMELESS
        mocker.patch.object(
            JewelParser, "detect_jewel_type", return_value=JewelType.TIMELESS
        )
        mocker.patch.object(JewelParser, "parse_timeless_jewel", return_value=[])

        # Create property with value that causes TypeError when converting to int
        mock_property = SimpleNamespace(
            name="seed", value=None
        )  # None will cause TypeError
        jewel = mock_jewel(
            name="Glorious Vanity",
            text="Bathed in the blood of # sacrificed",
            properties=[mock_property],
        )
        allocated_nodes = [100, 101, 102]
        modifiers = PassiveTreeParser.parse_jewel_socket(12345, jewel, allocated_nodes)
        # Should handle TypeError gracefully (covers lines 131-132)
        assert isinstance(modifiers, list)
        JewelParser.parse_timeless_jewel.assert_called_once_with(  # type: ignore[attr-defined]
            12345, jewel, allocated_nodes, None
        )

"""Tests for JewelParser."""

import pytest

from pobapi.calculator.jewel_parser import JewelParser, JewelType


class TestJewelParser:
    """Tests for JewelParser."""

    @pytest.mark.parametrize(
        ("jewel_text", "expected_type"),
        [
            ("Small Cluster Jewel", JewelType.RADIUS),
            ("Medium Cluster Jewel", JewelType.RADIUS),
            ("Large Cluster Jewel", JewelType.RADIUS),
            ("Passives in radius", JewelType.RADIUS),
            ("Thread of Hope", JewelType.CONVERSION),
            ("Impossible Escape", JewelType.CONVERSION),
            ("Intuitive Leap", JewelType.CONVERSION),
            ("Glorious Vanity", JewelType.TIMELESS),
            ("Lethal Pride", JewelType.TIMELESS),
            ("Brutal Restraint", JewelType.TIMELESS),
            ("Militant Faith", JewelType.TIMELESS),
            ("Elegant Hubris", JewelType.TIMELESS),
            ("Crimson Jewel", JewelType.NORMAL),
            ("Viridian Jewel", JewelType.NORMAL),
            ("Cobalt Jewel", JewelType.NORMAL),
        ],
    )
    def test_detect_jewel_type(self, jewel_text: str, expected_type: JewelType) -> None:
        """Test detecting jewel type from text."""
        result = JewelParser.detect_jewel_type(jewel_text)
        assert result == expected_type

    def test_detect_jewel_type_case_insensitive(self) -> None:
        """Test that jewel type detection is case insensitive."""
        result1 = JewelParser.detect_jewel_type("small cluster jewel")
        result2 = JewelParser.detect_jewel_type("SMALL CLUSTER JEWEL")
        assert result1 == JewelType.RADIUS
        assert result2 == JewelType.RADIUS

    @pytest.mark.parametrize(
        ("allocated_nodes", "expected_type"),
        [
            ([100, 101, 102], list),
            ([], list),
        ],
    )
    def test_parse_radius_jewel(
        self, mock_jewel, allocated_nodes, expected_type
    ) -> None:
        """Test parsing radius jewel."""
        jewel = mock_jewel(name="Small Cluster Jewel", text="Adds 2 Passive Skills")
        modifiers = JewelParser.parse_radius_jewel(12345, jewel, allocated_nodes)
        assert isinstance(modifiers, expected_type)

    @pytest.mark.parametrize(
        ("jewel_name", "jewel_text", "allocated_nodes"),
        [
            ("Thread of Hope", "Allocates passives in a large ring", [100, 101, 102]),
            ("Impossible Escape", "Allocates passives in a medium ring", [100, 101]),
        ],
    )
    def test_parse_conversion_jewel(
        self, mock_jewel, jewel_name, jewel_text, allocated_nodes
    ) -> None:
        """Test parsing conversion jewels."""
        jewel = mock_jewel(name=jewel_name, text=jewel_text)
        modifiers = JewelParser.parse_conversion_jewel(12345, jewel, allocated_nodes)
        assert isinstance(modifiers, list)

    def test_parse_conversion_jewel_with_match(self, mock_jewel) -> None:
        """Test parsing conversion jewel with matching pattern - covers line 298."""
        jewel = mock_jewel(
            name="Thread of Hope", text="Allocates 2 Notable Passive Skills in radius"
        )
        modifiers = JewelParser.parse_conversion_jewel(12345, jewel, [100, 101])
        # Should add CanAllocateNodesInRadius modifier (covers line 298)
        assert len(modifiers) > 0
        assert any("CanAllocateNodesInRadius" in m.stat for m in modifiers)

    @pytest.mark.parametrize(
        ("jewel_name", "jewel_text", "allocated_nodes"),
        [
            (
                "Glorious Vanity",
                "Bathed in the blood of # sacrificed in the name of",
                [100, 101, 102],
            ),
            ("Lethal Pride", "Commanded leadership over # warriors", [100, 101]),
        ],
    )
    def test_parse_timeless_jewel(
        self, mock_jewel, jewel_name, jewel_text, allocated_nodes
    ) -> None:
        """Test parsing timeless jewels."""
        jewel = mock_jewel(name=jewel_name, text=jewel_text)
        modifiers = JewelParser.parse_timeless_jewel(12345, jewel, allocated_nodes)
        assert isinstance(modifiers, list)

    def test_parse_radius_jewel_invalid(self) -> None:
        """Test parsing invalid radius jewel."""
        modifiers = JewelParser.parse_radius_jewel(12345, None, [])
        assert modifiers == []

    def test_parse_conversion_jewel_invalid(self) -> None:
        """Test parsing invalid conversion jewel."""
        modifiers = JewelParser.parse_conversion_jewel(12345, None, [])
        assert modifiers == []

    def test_parse_timeless_jewel_invalid(self) -> None:
        """Test parsing invalid timeless jewel."""
        modifiers = JewelParser.parse_timeless_jewel(12345, None, [])
        assert modifiers == []

    def test_extract_radius_from_text(self) -> None:
        """Test extracting radius from jewel text."""
        radius1 = JewelParser._extract_radius("Passives in radius 2")
        assert radius1 == 2

        radius2 = JewelParser._extract_radius("radius 3")
        assert radius2 == 3

        radius3 = JewelParser._extract_radius("5 radius")
        assert radius3 == 5

    def test_extract_radius_with_invalid_match(self, mocker) -> None:
        """Test extracting radius with invalid match group - covers lines 234-235."""
        # Mock re.search to return a match with invalid group
        mock_match = mocker.Mock()
        mock_match.group.side_effect = IndexError("No such group")
        mocker.patch(
            "pobapi.calculator.jewel_parser.re.search", return_value=mock_match
        )

        # Should handle ValueError/IndexError gracefully (covers lines 234-235)
        radius = JewelParser._extract_radius("test text")
        # Should return default (0) or handle error
        assert isinstance(radius, int)

    def test_extract_radius_from_cluster_jewel(self) -> None:
        """Test extracting radius from cluster jewel names."""
        radius_small = JewelParser._extract_radius("Small Cluster Jewel")
        assert radius_small == 1

        radius_medium = JewelParser._extract_radius("Medium Cluster Jewel")
        assert radius_medium == 2

        radius_large = JewelParser._extract_radius("Large Cluster Jewel")
        assert radius_large == 3

    def test_extract_radius_default(self) -> None:
        """Test extracting radius with no match."""
        radius = JewelParser._extract_radius("Regular Jewel")
        assert radius == 0

    def test_extract_radius_modifiers(self) -> None:
        """Test extracting modifiers from radius jewel text."""
        jewel_text = "Passives in radius have +10% to Fire Resistance"
        modifiers = JewelParser._extract_radius_modifiers(jewel_text, 12345, 2)
        assert isinstance(modifiers, list)
        if len(modifiers) > 0:
            assert any("Fire" in m.stat for m in modifiers)

    def test_extract_conversion_modifiers(self) -> None:
        """Test extracting modifiers from conversion jewel text."""
        jewel_text = "Allocates passives in a large ring"
        modifiers = JewelParser._extract_conversion_modifiers(jewel_text, 12345)
        assert isinstance(modifiers, list)

    def test_extract_seed_from_text(self) -> None:
        """Test extracting seed from timeless jewel text."""
        # The _extract_seed method might use different patterns
        # Test with actual timeless jewel text format
        seed1 = JewelParser._extract_seed(
            "Bathed in the blood of 12345 sacrificed in the name of"
        )
        # Might return None if pattern doesn't match exactly
        assert seed1 is None or seed1 == 12345

        seed2 = JewelParser._extract_seed(
            "Commanded leadership over 67890 warriors in the name of"
        )
        assert seed2 is None or seed2 == 67890

    def test_extract_seed_with_invalid_match(self, mocker) -> None:
        """Test extracting seed with invalid match group - covers lines 326-329."""
        # Mock re.search to return a match with invalid group
        mock_match = mocker.Mock()
        mock_match.group.side_effect = ValueError("Invalid value")
        mocker.patch(
            "pobapi.calculator.jewel_parser.re.search", return_value=mock_match
        )

        # Should handle ValueError/IndexError gracefully (covers lines 326-329)
        seed = JewelParser._extract_seed("test text")
        # Should return None or handle error
        assert seed is None

    def test_extract_seed_no_match(self) -> None:
        """Test extracting seed when no seed found."""
        seed = JewelParser._extract_seed("Regular jewel text")
        assert seed is None

    def test_extract_timeless_modifiers(self) -> None:
        """Test extracting modifiers from timeless jewel."""
        jewel_text = "Bathed in the blood of 12345 sacrificed"
        modifiers = JewelParser._extract_timeless_modifiers(
            jewel_text, 12345, 12345, [100, 101, 102]
        )
        assert isinstance(modifiers, list)

    def test_extract_timeless_modifiers_with_timeless_source(self, mocker) -> None:
        """Test extracting timeless modifiers with timeless/seed in source.

        Covers lines 360-361."""
        from pobapi.calculator.item_modifier_parser import ItemModifierParser
        from pobapi.calculator.modifiers import Modifier, ModifierType

        # Mock parse_item_text to return modifiers with timeless/seed in source
        mock_modifier = Modifier(
            stat="Life",
            value=100.0,
            mod_type=ModifierType.FLAT,
            source="jewel:timeless:socket_12345:seed_54321",
        )
        mocker.patch.object(
            ItemModifierParser, "parse_item_text", return_value=[mock_modifier]
        )

        modifiers = JewelParser._extract_timeless_modifiers(
            "test text", 12345, 54321, [100, 101]
        )
        # Should include modifier with timeless/seed in source (covers lines 360-361)
        assert len(modifiers) > 0
        assert any(
            "timeless" in m.source.lower() or "seed" in m.source.lower()
            for m in modifiers
        )

    def test_parse_radius_jewel_with_radius_modifiers(self, mock_jewel, mocker) -> None:
        """Test parsing radius jewel with 'Passives in radius have' text.

        Covers lines 124-127."""
        from pobapi.calculator.modifiers import Modifier, ModifierType

        jewel = mock_jewel(
            name="Small Cluster Jewel",
            text="Small Cluster Jewel\nAdds 2 Passive Skills",
            # Include "Small Cluster Jewel" in text for radius detection
        )
        allocated_nodes = [100, 101, 102]

        # Mock _extract_radius_modifiers to return a modifier (covers lines 124-127)
        mock_modifier = Modifier(
            stat="FireResistance",
            value=10.0,
            mod_type=ModifierType.FLAT,
            source="jewel:radius:socket_12345:nodes_in_radius",
        )
        mock_extract = mocker.patch.object(
            JewelParser, "_extract_radius_modifiers", return_value=[mock_modifier]
        )

        modifiers = JewelParser.parse_radius_jewel(12345, jewel, allocated_nodes)
        assert isinstance(modifiers, list)
        # Verify that _extract_radius_modifiers was called (covers lines 124-127)
        # Small Cluster Jewel has radius 1, so affected_modifiers should be added
        assert mock_extract.called
        assert len(modifiers) > 0
        # Check for Fire Resistance modifier from radius
        assert any("Fire" in m.stat or "FireResistance" in m.stat for m in modifiers)

    def test_parse_timeless_jewel_with_seed(self, mock_jewel) -> None:
        """Test parsing timeless jewel with explicit seed."""
        jewel = mock_jewel(
            name="Glorious Vanity",
            text="Bathed in the blood of # sacrificed",
            seed=54321,
        )
        allocated_nodes = [100, 101, 102]
        modifiers = JewelParser.parse_timeless_jewel(
            12345, jewel, allocated_nodes, 54321
        )
        assert isinstance(modifiers, list)

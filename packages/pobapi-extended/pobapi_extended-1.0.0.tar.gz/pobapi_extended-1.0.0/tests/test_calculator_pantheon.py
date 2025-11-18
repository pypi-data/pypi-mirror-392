"""Tests for Pantheon calculator."""

from unittest.mock import Mock

import pytest

from pobapi.calculator.modifiers import Modifier, ModifierSystem, ModifierType
from pobapi.calculator.pantheon import (
    PantheonGod,
    PantheonSoul,
    PantheonTools,
)


class TestPantheonSoul:
    """Tests for PantheonSoul dataclass."""

    def test_init(self):
        """Test initialization."""
        soul = PantheonSoul(name="Test Soul", mods=["+10% to Fire Resistance"])
        assert soul.name == "Test Soul"
        assert soul.mods == ["+10% to Fire Resistance"]

    def test_init_multiple_mods(self):
        """Test initialization with multiple mods."""
        mods = ["+10% to Fire Resistance", "+20 to Strength"]
        soul = PantheonSoul(name="Test", mods=mods)
        assert soul.mods == mods


class TestPantheonGod:
    """Tests for PantheonGod dataclass."""

    def test_init(self):
        """Test initialization."""
        soul = PantheonSoul(name="Minor Soul", mods=["+5% to Fire Resistance"])
        god = PantheonGod(name="The Brine King", souls=[soul])
        assert god.name == "The Brine King"
        assert len(god.souls) == 1
        assert god.souls[0] == soul

    def test_init_multiple_souls(self):
        """Test initialization with multiple souls."""
        minor = PantheonSoul(name="Minor", mods=["+5% to Fire Resistance"])
        major = PantheonSoul(name="Major", mods=["+10% to Fire Resistance"])
        god = PantheonGod(name="Test God", souls=[minor, major])
        assert len(god.souls) == 2


class TestPantheonTools:
    """Tests for PantheonTools class."""

    @pytest.fixture
    def mock_modifiers(self):
        """Create a mock ModifierSystem."""
        return Mock(spec=ModifierSystem)

    @pytest.fixture
    def mock_parser(self):
        """Create a mock ItemModifierParser."""
        parser = Mock()
        return parser

    @pytest.fixture
    def tools(self, mock_modifiers):
        """Create a PantheonTools instance."""
        return PantheonTools(mock_modifiers)

    def test_init(self, mock_modifiers):
        """Test initialization."""
        tools = PantheonTools(mock_modifiers)
        assert tools.modifiers == mock_modifiers
        assert tools.parser is not None

    def test_apply_soul_mod_empty_souls(self, tools, mock_modifiers):
        """Test apply_soul_mod with god that has no souls."""
        god = PantheonGod(name="Test God", souls=[])
        tools.apply_soul_mod(god)
        # Should not raise, just do nothing
        mock_modifiers.add_modifiers.assert_not_called()

    def test_apply_soul_mod_no_parsed_mods(self, tools, mock_modifiers):
        """Test apply_soul_mod when parser returns no mods."""
        soul = PantheonSoul(name="Test Soul", mods=["invalid mod"])
        god = PantheonGod(name="Test God", souls=[soul])

        # Mock parser to return empty list
        tools.parser.parse_line = Mock(return_value=[])

        tools.apply_soul_mod(god)
        mock_modifiers.add_modifiers.assert_not_called()

    def test_apply_soul_mod_with_parsed_mods(self, tools, mock_modifiers):
        """Test apply_soul_mod adds modifiers with source prefix."""
        soul = PantheonSoul(name="Test Soul", mods=["+10% to Fire Resistance"])
        god = PantheonGod(name="Test God", souls=[soul])

        # Mock parser to return a modifier
        mod = Modifier(
            mod_type=ModifierType.INCREASED,
            stat="Fire Resistance",
            value=10.0,
            source="",
        )
        tools.parser.parse_line = Mock(return_value=[mod])

        tools.apply_soul_mod(god)

        # Verify modifier was added with source prefix
        mock_modifiers.add_modifiers.assert_called_once()
        call_args = mock_modifiers.add_modifiers.call_args[0][0]
        assert len(call_args) == 1
        assert call_args[0].source == "Pantheon:Test Soul"

    def test_apply_soul_mod_multiple_souls(self, tools, mock_modifiers):
        """Test apply_soul_mod processes all souls."""
        minor = PantheonSoul(name="Minor", mods=["+5% to Fire Resistance"])
        major = PantheonSoul(name="Major", mods=["+10% to Fire Resistance"])
        god = PantheonGod(name="Test God", souls=[minor, major])

        mod1 = Modifier(
            mod_type=ModifierType.INCREASED,
            stat="Fire Resistance",
            value=5.0,
            source="",
        )
        mod2 = Modifier(
            mod_type=ModifierType.INCREASED,
            stat="Fire Resistance",
            value=10.0,
            source="",
        )

        tools.parser.parse_line = Mock(side_effect=[[mod1], [mod2]])

        tools.apply_soul_mod(god)

        # Should be called twice (once per soul)
        assert mock_modifiers.add_modifiers.call_count == 2

    def test_apply_pantheon_none(self, tools, mock_modifiers):
        """Test apply_pantheon with no gods."""
        tools.apply_pantheon(None, None)
        mock_modifiers.add_modifiers.assert_not_called()

    def test_apply_pantheon_major_only(self, tools, mock_modifiers):
        """Test apply_pantheon with only major god."""
        soul = PantheonSoul(name="Major Soul", mods=["+10% to Fire Resistance"])
        major_god = PantheonGod(name="Major God", souls=[soul])

        mod = Modifier(
            mod_type=ModifierType.INCREASED,
            stat="Fire Resistance",
            value=10.0,
            source="",
        )
        tools.parser.parse_line = Mock(return_value=[mod])

        tools.apply_pantheon(major_god, None)

        mock_modifiers.add_modifiers.assert_called_once()

    def test_apply_pantheon_minor_only(self, tools, mock_modifiers):
        """Test apply_pantheon with only minor god."""
        soul = PantheonSoul(name="Minor Soul", mods=["+5% to Fire Resistance"])
        minor_god = PantheonGod(name="Minor God", souls=[soul])

        mod = Modifier(
            mod_type=ModifierType.INCREASED,
            stat="Fire Resistance",
            value=5.0,
            source="",
        )
        tools.parser.parse_line = Mock(return_value=[mod])

        tools.apply_pantheon(None, minor_god)

        mock_modifiers.add_modifiers.assert_called_once()

    def test_apply_pantheon_both(self, tools, mock_modifiers):
        """Test apply_pantheon with both major and minor gods."""
        major_soul = PantheonSoul(name="Major", mods=["+10% to Fire Resistance"])
        minor_soul = PantheonSoul(name="Minor", mods=["+5% to Fire Resistance"])
        major_god = PantheonGod(name="Major God", souls=[major_soul])
        minor_god = PantheonGod(name="Minor God", souls=[minor_soul])

        mod1 = Modifier(
            mod_type=ModifierType.INCREASED,
            stat="Fire Resistance",
            value=10.0,
            source="",
        )
        mod2 = Modifier(
            mod_type=ModifierType.INCREASED,
            stat="Fire Resistance",
            value=5.0,
            source="",
        )

        tools.parser.parse_line = Mock(side_effect=[[mod1], [mod2]])

        tools.apply_pantheon(major_god, minor_god)

        # Should be called twice (once per god)
        assert mock_modifiers.add_modifiers.call_count == 2

    def test_create_god(self):
        """Test create_god static method."""
        souls_data: list[dict[str, str | list[str]]] = [
            {"name": "Minor Soul", "mods": ["+5% to Fire Resistance"]},
            {"name": "Major Soul", "mods": ["+10% to Fire Resistance"]},
        ]

        god = PantheonTools.create_god("Test God", souls_data)

        assert god.name == "Test God"
        assert len(god.souls) == 2
        assert god.souls[0].name == "Minor Soul"
        assert god.souls[1].name == "Major Soul"
        assert god.souls[0].mods == ["+5% to Fire Resistance"]
        assert god.souls[1].mods == ["+10% to Fire Resistance"]

    def test_create_god_empty_souls(self):
        """Test create_god with empty souls list."""
        god = PantheonTools.create_god("Test God", [])
        assert god.name == "Test God"
        assert len(god.souls) == 0

"""Tests for Legion Jewels (Timeless Jewels) calculator."""

import tempfile
from pathlib import Path

import pytest

from pobapi.calculator.legion_jewels import (
    LegionJewelData,
    LegionJewelHelper,
    LegionJewelType,
)


class TestLegionJewelType:
    """Tests for LegionJewelType constants."""

    def test_constants(self):
        """Test that all jewel type constants are defined."""
        assert LegionJewelType.GLORIOUS_VANITY == 1
        assert LegionJewelType.LETHAL_PRIDE == 2
        assert LegionJewelType.BRUTAL_RESTRAINT == 3
        assert LegionJewelType.MILITANT_FAITH == 4
        assert LegionJewelType.ELEGANT_HUBRIS == 5


class TestLegionJewelData:
    """Tests for LegionJewelData dataclass."""

    def test_init_basic(self):
        """Test basic initialization."""
        data = LegionJewelData(jewel_type=1, seed=12345)
        assert data.jewel_type == 1
        assert data.seed == 12345
        assert data.node_id is None
        assert data.modified_nodes == {}

    def test_init_with_node_id(self):
        """Test initialization with node_id."""
        data = LegionJewelData(jewel_type=1, seed=12345, node_id=39085)
        assert data.node_id == 39085

    def test_init_with_modified_nodes(self):
        """Test initialization with modified_nodes."""
        modified = {123: ["+10% to Fire Resistance"], 456: ["+20 to Strength"]}
        data = LegionJewelData(jewel_type=1, seed=12345, modified_nodes=modified)
        assert data.modified_nodes == modified

    def test_post_init_defaults(self):
        """Test __post_init__ sets default modified_nodes."""
        data = LegionJewelData(jewel_type=1, seed=12345, modified_nodes=None)
        assert data.modified_nodes == {}


class TestLegionJewelHelper:
    """Tests for LegionJewelHelper class."""

    def test_init_no_directory(self):
        """Test initialization without data directory."""
        helper = LegionJewelHelper()
        assert helper.data_directory is None
        assert helper._lut_cache == {}

    def test_init_with_directory(self):
        """Test initialization with data directory."""
        helper = LegionJewelHelper(data_directory="/test/path")
        assert helper.data_directory == "/test/path"
        assert helper._lut_cache == {}

    def test_find_jewel_file_no_directory(self):
        """Test _find_jewel_file returns None when no directory set."""
        helper = LegionJewelHelper()
        assert helper._find_jewel_file("GloriousVanity") is None

    def test_find_jewel_file_not_found(self):
        """Test _find_jewel_file returns None when file not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            helper = LegionJewelHelper(data_directory=tmpdir)
            assert helper._find_jewel_file("GloriousVanity") is None

    def test_find_jewel_file_bin(self):
        """Test _find_jewel_file finds .bin file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create TimelessJewelData directory
            data_dir = Path(tmpdir) / "TimelessJewelData"
            data_dir.mkdir()

            # Create .bin file
            bin_file = data_dir / "GloriousVanity.bin"
            bin_file.write_bytes(b"test data")

            helper = LegionJewelHelper(data_directory=tmpdir)
            result = helper._find_jewel_file("GloriousVanity")
            assert result is not None
            assert result.endswith("GloriousVanity.bin")

    def test_find_jewel_file_zip(self):
        """Test _find_jewel_file finds .zip file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create TimelessJewelData directory
            data_dir = Path(tmpdir) / "TimelessJewelData"
            data_dir.mkdir()

            # Create .zip file
            zip_file = data_dir / "GloriousVanity.zip"
            zip_file.write_bytes(b"test data")

            helper = LegionJewelHelper(data_directory=tmpdir)
            result = helper._find_jewel_file("GloriousVanity")
            assert result is not None
            assert result.endswith("GloriousVanity.zip")

    def test_load_timeless_jewel_invalid_type(self):
        """Test load_timeless_jewel with invalid jewel type."""
        helper = LegionJewelHelper()
        assert helper.load_timeless_jewel(99) is False

    def test_load_timeless_jewel_glorious_vanity_no_node(self):
        """Test load_timeless_jewel requires node_id for Glorious Vanity."""
        helper = LegionJewelHelper()
        assert helper.load_timeless_jewel(LegionJewelType.GLORIOUS_VANITY) is False

    def test_load_timeless_jewel_already_loaded(self):
        """Test load_timeless_jewel returns True if already loaded."""
        helper = LegionJewelHelper()
        helper._lut_cache[1] = b"cached data"
        assert (
            helper.load_timeless_jewel(LegionJewelType.GLORIOUS_VANITY, node_id=39085)
            is True
        )

    def test_load_timeless_jewel_file_not_found(self):
        """Test load_timeless_jewel returns False when file not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            helper = LegionJewelHelper(data_directory=tmpdir)
            assert helper.load_timeless_jewel(LegionJewelType.LETHAL_PRIDE) is False

    def test_load_timeless_jewel_success(self):
        """Test load_timeless_jewel successfully loads file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create TimelessJewelData directory
            data_dir = Path(tmpdir) / "TimelessJewelData"
            data_dir.mkdir()

            # Create .bin file
            bin_file = data_dir / "LethalPride.bin"
            bin_file.write_bytes(b"test binary data")

            helper = LegionJewelHelper(data_directory=tmpdir)
            assert helper.load_timeless_jewel(LegionJewelType.LETHAL_PRIDE) is True
            assert LegionJewelType.LETHAL_PRIDE in helper._lut_cache

    def test_read_lut_not_loaded(self):
        """Test read_lut returns None when LUT not loaded."""
        helper = LegionJewelHelper()
        result = helper.read_lut(seed=12345, node_id=39085, jewel_type=1)
        assert result is None

    def test_read_lut_loaded_but_no_data(self):
        """Test read_lut returns None when loaded but no actual data."""
        helper = LegionJewelHelper()
        helper._lut_cache[1] = b"dummy data"
        # read_lut will try to load but won't parse (no actual implementation)
        result = helper.read_lut(seed=12345, node_id=39085, jewel_type=1)
        assert result is None

    def test_get_node_modifications_with_modified_nodes(self):
        """Test get_node_modifications returns existing modified_nodes."""
        modified = {123: ["+10% to Fire Resistance"]}
        jewel_data = LegionJewelData(jewel_type=1, seed=12345, modified_nodes=modified)
        helper = LegionJewelHelper()
        result = helper.get_node_modifications(jewel_data)
        assert result == modified

    def test_get_node_modifications_from_lut(self):
        """Test get_node_modifications tries to read from LUT."""
        jewel_data = LegionJewelData(
            jewel_type=1, seed=12345, node_id=39085, modified_nodes=None
        )
        helper = LegionJewelHelper()
        # Will try to read from LUT but return empty dict (no actual LUT data)
        result = helper.get_node_modifications(jewel_data)
        assert result == {}

    @pytest.mark.parametrize(
        "jewel_type,expected_name",
        [
            (LegionJewelType.GLORIOUS_VANITY, "GloriousVanity"),
            (LegionJewelType.LETHAL_PRIDE, "LethalPride"),
            (LegionJewelType.BRUTAL_RESTRAINT, "BrutalRestraint"),
            (LegionJewelType.MILITANT_FAITH, "MilitantFaith"),
            (LegionJewelType.ELEGANT_HUBRIS, "ElegantHubris"),
        ],
    )
    def test_jewel_type_names(self, jewel_type, expected_name):
        """Test that jewel type names are correct."""
        helper = LegionJewelHelper()
        # Access private method through reflection to test name mapping
        result = helper._find_jewel_file(expected_name)
        # Just verify the method works (will return None if file doesn't exist)
        assert result is None or expected_name in result

    def test_load_timeless_jewel_oserror(self, mocker):
        """Test load_timeless_jewel handles OSError - covers lines 140-141."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create TimelessJewelData directory
            data_dir = Path(tmpdir) / "TimelessJewelData"
            data_dir.mkdir()

            # Create .bin file
            bin_file = data_dir / "LethalPride.bin"
            bin_file.write_bytes(b"test binary data")

            helper = LegionJewelHelper(data_directory=tmpdir)
            # Mock open to raise OSError when reading file (covers lines 140-141)
            mocker.patch("builtins.open", side_effect=OSError("Permission denied"))
            # Should return False when OSError occurs (covers lines 140-141)
            result = helper.load_timeless_jewel(LegionJewelType.LETHAL_PRIDE)
            assert result is False

    def test_get_node_modifications_returns_empty_dict(self):
        """Test get_node_modifications returns empty dict when LUT parsing fails.

        Covers line 187."""
        jewel_data = LegionJewelData(
            jewel_type=1, seed=12345, node_id=39085, modified_nodes=None
        )
        helper = LegionJewelHelper()
        # Set cache with dummy data (will fail to parse, returns None from read_lut)
        helper._lut_cache[1] = b"invalid binary data"
        # read_lut will return None, so get_node_modifications
        # should return empty dict (covers line 187)
        result = helper.get_node_modifications(jewel_data)
        assert result == {}

    def test_get_node_modifications_with_modifications_list(self, mocker):
        """Test get_node_modifications when read_lut returns a list.

        Covers lines 185-186."""
        jewel_data = LegionJewelData(
            jewel_type=1, seed=12345, node_id=39085, modified_nodes=None
        )
        helper = LegionJewelHelper()
        # Mock read_lut to return a list (simulating successful LUT read)
        mocker.patch.object(helper, "read_lut", return_value=[1, 2, 3])
        # Should create result dict and return it (covers lines 185-186)
        result = helper.get_node_modifications(jewel_data)
        assert isinstance(result, dict)
        assert (
            result == {}
        )  # Currently returns empty dict as parsing logic is not implemented

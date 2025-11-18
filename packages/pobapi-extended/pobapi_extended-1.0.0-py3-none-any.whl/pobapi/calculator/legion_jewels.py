"""Legion Jewels (Timeless Jewels) support for Path of Building.

This module handles Timeless Jewels that modify passive tree nodes:
- Glorious Vanity
- Lethal Pride
- Brutal Restraint
- Militant Faith
- Elegant Hubris
"""

from dataclasses import dataclass
from typing import Any

__all__ = ["LegionJewelType", "LegionJewelData", "LegionJewelHelper"]


class LegionJewelType:
    """Legion Jewel type constants."""

    GLORIOUS_VANITY = 1  # Glorious Vanity
    LETHAL_PRIDE = 2  # Lethal Pride
    BRUTAL_RESTRAINT = 3  # Brutal Restraint
    MILITANT_FAITH = 4  # Militant Faith
    ELEGANT_HUBRIS = 5  # Elegant Hubris


@dataclass
class LegionJewelData:
    """Data for a Legion Jewel.

    :param jewel_type: Type of Legion Jewel (1-5).
    :param seed: Seed value for the jewel.
    :param node_id: Node ID where the jewel is socketed (for Glorious Vanity).
    :param modified_nodes: Dictionary of node_id -> modified stats.
    """

    jewel_type: int
    seed: int
    node_id: int | None = None
    modified_nodes: dict[int, list[str]] | None = None

    def __post_init__(self):
        """Initialize default values."""
        if self.modified_nodes is None:
            self.modified_nodes = {}


class LegionJewelHelper:
    """Helper for loading and reading Legion Jewel lookup tables.

    In Path of Building (Lua), Legion Jewels use binary lookup tables (LUTs)
    that map seed values to node modifications. These LUTs are stored in:
    - /Data/TimelessJewelData/ directory
    - Files: GloriousVanity.bin/.zip, LethalPride.bin/.zip, etc.

    Our implementation provides a structure for loading these LUTs,
    but the actual binary data files need to be extracted from PoB or
    generated from the game's data files.
    """

    def __init__(self, data_directory: str | None = None):
        """Initialize Legion Jewel helper.

        :param data_directory: Directory containing TimelessJewelData files.
        """
        self.data_directory = data_directory
        self._lut_cache: dict[int, Any] = {}  # Cache for loaded LUTs

    def _find_jewel_file(self, jewel_type_name: str) -> str | None:
        """Find Legion Jewel data file.

        :param jewel_type_name: Name of jewel type (e.g., "GloriousVanity").
        :return: Path to file if found, None otherwise.
        """
        import os

        if not self.data_directory:
            return None

        # Try .bin first (uncompressed)
        bin_path = os.path.join(
            self.data_directory, "TimelessJewelData", f"{jewel_type_name}.bin"
        )
        if os.path.exists(bin_path):
            return bin_path

        # Try .zip (compressed)
        zip_path = os.path.join(
            self.data_directory, "TimelessJewelData", f"{jewel_type_name}.zip"
        )
        if os.path.exists(zip_path):
            return zip_path

        return None

    def load_timeless_jewel(self, jewel_type: int, node_id: int | None = None) -> bool:
        """Load timeless jewel lookup table.

        :param jewel_type: Type of Legion Jewel (1-5).
        :param node_id: Node ID for Glorious Vanity (required for type 1).
        :return: True if loaded successfully, False otherwise.
        """
        jewel_type_names = {
            1: "GloriousVanity",
            2: "LethalPride",
            3: "BrutalRestraint",
            4: "MilitantFaith",
            5: "ElegantHubris",
        }

        if jewel_type not in jewel_type_names:
            return False

        # Glorious Vanity requires node_id
        if jewel_type == 1 and node_id is None:
            return False

        # Check if already loaded
        if jewel_type in self._lut_cache:
            return True

        # Try to load file
        jewel_name = jewel_type_names[jewel_type]
        file_path = self._find_jewel_file(jewel_name)

        if not file_path:
            # File not found - would need to extract from PoB or generate
            return False

        # Load binary data (simplified - actual implementation would need
        # to parse the binary format)
        try:
            with open(file_path, "rb") as f:
                data = f.read()
                # Store in cache (actual parsing would happen here)
                self._lut_cache[jewel_type] = data
                return True
        except OSError:
            return False

    def read_lut(self, seed: int, node_id: int, jewel_type: int) -> list[int] | None:
        """Read lookup table entry for a seed and node.

        :param seed: Seed value for the jewel.
        :param node_id: Node ID to modify.
        :param jewel_type: Type of Legion Jewel (1-5).
        :return: List of modification values or None if not found.
        """
        # Check if LUT is loaded
        if jewel_type not in self._lut_cache:
            if not self.load_timeless_jewel(jewel_type, node_id):
                return None

        # Actual implementation would:
        # 1. Parse the binary LUT format
        # 2. Find the entry for the given seed and node_id
        # 3. Return the modification values

        # For now, return None (requires actual LUT data files)
        return None

    def get_node_modifications(
        self, jewel_data: LegionJewelData
    ) -> dict[int, list[str]]:
        """Get node modifications from Legion Jewel.

        :param jewel_data: Legion Jewel data.
        :return: Dictionary of node_id -> list of modifier strings.
        """
        if jewel_data.modified_nodes:
            return jewel_data.modified_nodes

        # Try to read from LUT
        modifications = self.read_lut(
            jewel_data.seed, jewel_data.node_id or 0, jewel_data.jewel_type
        )

        if modifications:
            # Convert modifications to modifier strings
            # (actual implementation would parse the binary format)
            result: dict[int, list[str]] = {}
            # ... parsing logic ...
            return result

        return {}

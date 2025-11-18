"""Parser for special jewel types (Radius, Conversion, Timeless).

This module handles parsing and applying effects from special jewel types
that modify passive tree nodes in various ways.
"""

import re
from typing import Any

from pobapi.calculator.item_modifier_parser import ItemModifierParser
from pobapi.calculator.modifiers import Modifier, ModifierType

__all__ = ["JewelParser", "JewelType"]


class JewelType:
    """Types of special jewels."""

    NORMAL = "normal"  # Regular jewel
    RADIUS = "radius"  # Radius jewel (e.g., "Small Cluster Jewel")
    CONVERSION = "conversion"  # Conversion jewel (e.g., "Thread of Hope")
    TIMELESS = "timeless"  # Timeless jewel (e.g., "Glorious Vanity")


class JewelParser:
    """Parser for special jewel types.

    This class handles:
    - Radius jewels: Modify nodes within a certain radius
    - Conversion jewels: Convert node types or properties
    - Timeless jewels: Modify nodes based on seed value
    """

    # Radius jewel patterns
    RADIUS_JEWEL_PATTERNS = [
        r"Small Cluster Jewel",
        r"Medium Cluster Jewel",
        r"Large Cluster Jewel",
        r"Notable Cluster Jewel",
        r"Passives in radius",
    ]

    # Conversion jewel patterns
    CONVERSION_JEWEL_PATTERNS = [
        r"Thread of Hope",
        r"Impossible Escape",
        r"Intuitive Leap",
        r"Brutal Restraint",
        r"Lethal Pride",
        r"Militant Faith",
        r"Elegant Hubris",
    ]

    # Timeless jewel patterns
    TIMELESS_JEWEL_PATTERNS = [
        r"Glorious Vanity",
        r"Lethal Pride",
        r"Brutal Restraint",
        r"Militant Faith",
        r"Elegant Hubris",
    ]

    @staticmethod
    def detect_jewel_type(jewel_text: str) -> str:
        """Detect the type of jewel from its text.

        :param jewel_text: Full jewel item text.
        :return: Jewel type (JewelType constant).
        """
        jewel_text_upper = jewel_text.upper()

        # Check for timeless jewels first (they can also be conversion)
        for pattern in JewelParser.TIMELESS_JEWEL_PATTERNS:
            if pattern.upper() in jewel_text_upper:
                return JewelType.TIMELESS

        # Check for conversion jewels
        for pattern in JewelParser.CONVERSION_JEWEL_PATTERNS:
            if pattern.upper() in jewel_text_upper:
                return JewelType.CONVERSION

        # Check for radius jewels
        for pattern in JewelParser.RADIUS_JEWEL_PATTERNS:
            if pattern.upper() in jewel_text_upper:
                return JewelType.RADIUS

        return JewelType.NORMAL

    @staticmethod
    def parse_radius_jewel(
        socket_id: int, jewel_item: Any, allocated_nodes: list[int]
    ) -> list[Modifier]:
        """Parse a radius jewel and extract modifiers.

        Radius jewels modify nodes within a certain radius of the socket.
        Examples: Small/Medium/Large Cluster Jewels, Thread of Hope.

        :param socket_id: Jewel socket node ID.
        :param jewel_item: Jewel item object.
        :param allocated_nodes: List of allocated node IDs (for radius calculation).
        :return: List of Modifier objects from the jewel and affected nodes.
        """
        modifiers: list[Modifier] = []

        if not jewel_item or not hasattr(jewel_item, "text"):
            return modifiers

        jewel_text = jewel_item.text

        # Parse regular jewel modifiers
        jewel_modifiers = ItemModifierParser.parse_item_text(
            jewel_text, source=f"jewel:radius:socket_{socket_id}"
        )
        modifiers.extend(jewel_modifiers)

        # Extract radius from jewel text
        # Pattern: "Passives in radius have X" or "X radius"
        radius = JewelParser._extract_radius(jewel_text)

        if radius > 0:
            # Find nodes within radius
            # In a full implementation, this would use passive tree geometry
            # For now, we'll extract modifiers from jewel text that affect nodes
            affected_modifiers = JewelParser._extract_radius_modifiers(
                jewel_text, socket_id, radius
            )
            modifiers.extend(affected_modifiers)

        return modifiers

    @staticmethod
    def parse_conversion_jewel(
        socket_id: int, jewel_item: Any, allocated_nodes: list[int]
    ) -> list[Modifier]:
        """Parse a conversion jewel and extract modifiers.

        Conversion jewels convert node types or properties.
        Examples: Thread of Hope (allows allocating nodes without connections),
                  Impossible Escape (allows allocating nodes without path).

        :param socket_id: Jewel socket node ID.
        :param jewel_item: Jewel item object.
        :param allocated_nodes: List of allocated node IDs.
        :return: List of Modifier objects from the jewel.
        """
        modifiers: list[Modifier] = []

        if not jewel_item or not hasattr(jewel_item, "text"):
            return modifiers

        jewel_text = jewel_item.text

        # Parse regular jewel modifiers
        jewel_modifiers = ItemModifierParser.parse_item_text(
            jewel_text, source=f"jewel:conversion:socket_{socket_id}"
        )
        modifiers.extend(jewel_modifiers)

        # Extract conversion effects
        # Thread of Hope: "Allocates X Notable Passive Skills in radius"
        # Impossible Escape: "Allocates X Keystone Passive Skills in radius"
        conversion_modifiers = JewelParser._extract_conversion_modifiers(
            jewel_text, socket_id
        )
        modifiers.extend(conversion_modifiers)

        return modifiers

    @staticmethod
    def parse_timeless_jewel(
        socket_id: int,
        jewel_item: Any,
        allocated_nodes: list[int],
        seed: int | None = None,
    ) -> list[Modifier]:
        """Parse a timeless jewel and extract modifiers.

        Timeless jewels modify nodes based on a seed value.
        Examples: Glorious Vanity, Lethal Pride, Brutal Restraint, etc.

        :param socket_id: Jewel socket node ID.
        :param jewel_item: Jewel item object.
        :param allocated_nodes: List of allocated node IDs.
        :param seed: Seed value for the timeless jewel (if available).
        :return: List of Modifier objects from the jewel.
        """
        modifiers: list[Modifier] = []

        if not jewel_item or not hasattr(jewel_item, "text"):
            return modifiers

        jewel_text = jewel_item.text

        # Parse regular jewel modifiers
        jewel_modifiers = ItemModifierParser.parse_item_text(
            jewel_text, source=f"jewel:timeless:socket_{socket_id}"
        )
        modifiers.extend(jewel_modifiers)

        # Extract seed if not provided
        if seed is None:
            seed = JewelParser._extract_seed(jewel_text)

        # Timeless jewels modify nodes based on seed
        # In a full implementation, this would use the seed to determine
        # which nodes are modified and how
        if seed is not None:
            timeless_modifiers = JewelParser._extract_timeless_modifiers(
                jewel_text, socket_id, seed, allocated_nodes
            )
            modifiers.extend(timeless_modifiers)

        return modifiers

    @staticmethod
    def _extract_radius(jewel_text: str) -> int:
        """Extract radius value from jewel text.

        :param jewel_text: Jewel item text.
        :return: Radius value (default: 0).
        """
        # Pattern: "Passives in radius X" or "X radius"
        patterns = [
            r"Passives in radius (\d+)",
            r"radius (\d+)",
            r"(\d+) radius",
        ]

        for pattern in patterns:
            match = re.search(pattern, jewel_text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    pass

        # Default radius for cluster jewels
        if "Small Cluster Jewel" in jewel_text:
            return 1
        if "Medium Cluster Jewel" in jewel_text:
            return 2
        if "Large Cluster Jewel" in jewel_text:
            return 3

        return 0

    @staticmethod
    def _extract_radius_modifiers(
        jewel_text: str, socket_id: int, radius: int
    ) -> list[Modifier]:
        """Extract modifiers that affect nodes in radius.

        :param jewel_text: Jewel item text.
        :param socket_id: Socket ID.
        :param radius: Radius value.
        :return: List of Modifier objects.
        """
        modifiers: list[Modifier] = []

        # Pattern: "Passives in radius have X"
        pattern = r"Passives in radius have (.+?)(?:\.|$)"
        matches = re.finditer(pattern, jewel_text, re.IGNORECASE)

        for match in matches:
            modifier_text = match.group(1).strip()
            # Parse the modifier text
            radius_modifiers = ItemModifierParser.parse_line(
                modifier_text, source=f"jewel:radius:socket_{socket_id}:nodes_in_radius"
            )
            modifiers.extend(radius_modifiers)

        return modifiers

    @staticmethod
    def _extract_conversion_modifiers(
        jewel_text: str, socket_id: int
    ) -> list[Modifier]:
        """Extract conversion modifiers from jewel text.

        :param jewel_text: Jewel item text.
        :param socket_id: Socket ID.
        :return: List of Modifier objects.
        """
        modifiers: list[Modifier] = []

        # Thread of Hope: "Allocates X Notable Passive Skills in radius"
        # Impossible Escape: "Allocates X Keystone Passive Skills in radius"
        patterns = [
            r"Allocates (\d+) Notable Passive Skills in radius",
            r"Allocates (\d+) Keystone Passive Skills in radius",
        ]

        for pattern in patterns:
            match = re.search(pattern, jewel_text, re.IGNORECASE)
            if match:
                # This is a special flag that allows allocating nodes
                # The actual nodes would be determined by the passive tree geometry
                modifiers.append(
                    Modifier(
                        stat="CanAllocateNodesInRadius",
                        value=1.0,
                        mod_type=ModifierType.FLAG,
                        source=f"jewel:conversion:socket_{socket_id}",
                    )
                )

        return modifiers

    @staticmethod
    def _extract_seed(jewel_text: str) -> int | None:
        """Extract seed value from timeless jewel text.

        :param jewel_text: Jewel item text.
        :return: Seed value or None.
        """
        # Pattern: "Seed: X" or "Seed X" or just a number at the end
        patterns = [
            r"Seed:\s*(\d+)",
            r"Seed\s+(\d+)",
            r"\((\d+)\)",  # Number in parentheses
        ]

        for pattern in patterns:
            match = re.search(pattern, jewel_text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    pass

        return None

    @staticmethod
    def _extract_timeless_modifiers(
        jewel_text: str, socket_id: int, seed: int, allocated_nodes: list[int]
    ) -> list[Modifier]:
        """Extract modifiers from timeless jewel based on seed.

        :param jewel_text: Jewel item text.
        :param socket_id: Socket ID.
        :param seed: Seed value.
        :param allocated_nodes: List of allocated node IDs.
        :return: List of Modifier objects.
        """
        modifiers: list[Modifier] = []

        # Timeless jewels modify specific nodes based on seed
        # The seed determines which nodes are affected and what modifiers they get
        # This is a simplified implementation - full version would use seed algorithm

        # Extract any explicit modifiers from jewel text
        # Pattern: "X% increased Y" or similar in timeless jewel context
        timeless_modifiers = ItemModifierParser.parse_item_text(
            jewel_text, source=f"jewel:timeless:socket_{socket_id}:seed_{seed}"
        )

        # Filter out modifiers that are already parsed as regular jewel modifiers
        # (This is a simplified check - full implementation would be more sophisticated)
        for mod in timeless_modifiers:
            if "timeless" in mod.source.lower() or "seed" in mod.source.lower():
                modifiers.append(mod)

        return modifiers

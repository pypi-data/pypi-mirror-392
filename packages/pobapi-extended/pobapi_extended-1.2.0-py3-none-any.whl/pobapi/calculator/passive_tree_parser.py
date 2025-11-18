"""Parser for extracting modifiers from passive skill tree.

This module parses passive skill tree nodes and extracts modifiers,
replicating Path of Building's passive tree parsing system.
"""

from typing import Any

from pobapi.calculator.item_modifier_parser import ItemModifierParser
from pobapi.calculator.jewel_parser import JewelParser, JewelType
from pobapi.calculator.modifiers import Modifier, ModifierType

__all__ = ["PassiveTreeParser"]


class PassiveTreeParser:
    """Parser for extracting modifiers from passive skill tree nodes.

    This class processes passive tree nodes and converts them to Modifier objects.
    In a full implementation, this would load node data from game files and
    apply modifiers based on allocated nodes.
    """

    # This is a placeholder implementation
    # Full implementation would require:
    # 1. Loading passive tree data (nodes.json or similar)
    # 2. Mapping node IDs to their effects
    # 3. Parsing node modifiers from game data

    @staticmethod
    def parse_node(
        node_id: int, node_data: dict[str, Any] | None = None
    ) -> list[Modifier]:
        """Parse a passive tree node and extract modifiers.

        :param node_id: Passive tree node ID.
        :param node_data: Optional node data dictionary (from game files).
        :return: List of Modifier objects from the node.
        """
        modifiers: list[Modifier] = []

        # Check if this is a keystone node
        from pobapi.constants import KEYSTONE_IDS

        for keystone_name, keystone_id in KEYSTONE_IDS.items():
            if node_id == keystone_id:
                # Keystones are handled separately
                return PassiveTreeParser.parse_keystone(keystone_name)

        # Parse node data if provided
        if node_data:
            stats = node_data.get("stats", [])
            source = f"passive_tree:{node_id}"

            for stat_text in stats:
                # Parse stat text using ItemModifierParser
                # Node stats use the same format as item modifiers
                stat_modifiers = ItemModifierParser.parse_line(stat_text, source=source)
                modifiers.extend(stat_modifiers)

        return modifiers

    @staticmethod
    def parse_tree(
        node_ids: list[int], tree_data: dict[str, Any] | None = None
    ) -> list[Modifier]:
        """Parse entire passive tree and extract all modifiers.

        :param node_ids: List of allocated node IDs.
        :param tree_data: Optional tree data dictionary (from game files).
            If provided, should be a dict mapping node_id -> node_data.
        :return: List of all Modifier objects from allocated nodes.
        """
        modifiers: list[Modifier] = []

        for node_id in node_ids:
            # Get node data if tree_data is provided
            node_data = None
            if tree_data and isinstance(tree_data, dict):
                node_data = tree_data.get(str(node_id))

            node_mods = PassiveTreeParser.parse_node(node_id, node_data)
            modifiers.extend(node_mods)

        return modifiers

    @staticmethod
    def parse_jewel_socket(
        socket_id: int,
        jewel_item: Any | None = None,
        allocated_nodes: list[int] | None = None,
    ) -> list[Modifier]:
        """Parse a jewel socket and extract modifiers from the jewel.

        This method detects the jewel type and uses the appropriate parser:
        - Normal jewels: Regular modifier parsing
        - Radius jewels: Parse radius effects
        - Conversion jewels: Parse conversion effects
        - Timeless jewels: Parse seed-based effects

        :param socket_id: Jewel socket node ID.
        :param jewel_item: Optional jewel item in the socket.
        :param allocated_nodes: Optional list of allocated node IDs
            (for radius/conversion jewels).
        :return: List of Modifier objects from the jewel.
        """
        modifiers: list[Modifier] = []

        if not jewel_item or not hasattr(jewel_item, "text"):
            return modifiers

        jewel_text = jewel_item.text
        allocated_nodes = allocated_nodes or []

        # Detect jewel type
        jewel_type = JewelParser.detect_jewel_type(jewel_text)

        # Parse based on jewel type
        if jewel_type == JewelType.TIMELESS:
            # Extract seed if available from jewel item
            seed = None
            if hasattr(jewel_item, "seed"):
                seed = jewel_item.seed
            elif hasattr(jewel_item, "properties"):
                # Try to extract seed from properties
                for prop in getattr(jewel_item, "properties", []):
                    if hasattr(prop, "name") and "seed" in prop.name.lower():
                        if hasattr(prop, "value"):
                            try:
                                seed = int(prop.value)
                            except (ValueError, TypeError):
                                pass

            timeless_modifiers = JewelParser.parse_timeless_jewel(
                socket_id, jewel_item, allocated_nodes, seed
            )
            modifiers.extend(timeless_modifiers)

        elif jewel_type == JewelType.CONVERSION:
            conversion_modifiers = JewelParser.parse_conversion_jewel(
                socket_id, jewel_item, allocated_nodes
            )
            modifiers.extend(conversion_modifiers)

        elif jewel_type == JewelType.RADIUS:
            radius_modifiers = JewelParser.parse_radius_jewel(
                socket_id, jewel_item, allocated_nodes
            )
            modifiers.extend(radius_modifiers)

        else:
            # Normal jewel - parse as regular item
            jewel_modifiers = ItemModifierParser.parse_item_text(
                jewel_text, source=f"jewel:socket_{socket_id}"
            )
            modifiers.extend(jewel_modifiers)

        return modifiers

    @staticmethod
    def parse_keystone(keystone_name: str) -> list[Modifier]:
        """Parse a keystone and extract its modifiers.

        :param keystone_name: Name of the keystone.
        :return: List of Modifier objects from the keystone.
        """
        modifiers: list[Modifier] = []

        # Keystone effects are special - they often change game mechanics
        # This requires special handling for each keystone
        keystone_name_lower = keystone_name.lower().replace(" ", "_")

        keystone_effects: dict[str, list[Modifier]] = {
            "acrobatics": [
                Modifier(
                    stat="Evasion",
                    value=30.0,
                    mod_type=ModifierType.INCREASED,
                    source="keystone:acrobatics",
                ),
                Modifier(
                    stat="EnergyShield",
                    value=-50.0,
                    mod_type=ModifierType.INCREASED,
                    source="keystone:acrobatics",
                ),
                Modifier(
                    stat="DodgeChance",
                    value=30.0,
                    mod_type=ModifierType.FLAT,
                    source="keystone:acrobatics",
                ),
            ],
            "chaos_inoculation": [
                Modifier(
                    stat="Life",
                    value=1.0,
                    mod_type=ModifierType.BASE,
                    source="keystone:chaos_inoculation",
                ),
                Modifier(
                    stat="ChaosResistance",
                    value=100.0,
                    mod_type=ModifierType.FLAT,
                    source="keystone:chaos_inoculation",
                ),
            ],
            "iron_reflexes": [
                Modifier(
                    stat="Evasion",
                    value=0.0,
                    mod_type=ModifierType.BASE,
                    source="keystone:iron_reflexes",
                ),
                Modifier(
                    stat="Armour",
                    value=100.0,
                    mod_type=ModifierType.INCREASED,
                    source="keystone:iron_reflexes",
                ),
            ],
            "elemental_overload": [
                Modifier(
                    stat="ElementalDamage",
                    value=40.0,
                    mod_type=ModifierType.MORE,
                    source="keystone:elemental_overload",
                ),
                Modifier(
                    stat="CritChance",
                    value=-100.0,
                    mod_type=ModifierType.INCREASED,
                    source="keystone:elemental_overload",
                ),
            ],
            "pain_attunement": [
                Modifier(
                    stat="SpellDamage",
                    value=30.0,
                    mod_type=ModifierType.MORE,
                    source="keystone:pain_attunement",
                    conditions={"on_low_life": True},
                ),
            ],
            "mind_over_matter": [
                Modifier(
                    stat="DamageTakenFromMana",
                    value=30.0,
                    mod_type=ModifierType.FLAT,
                    source="keystone:mind_over_matter",
                ),
            ],
            "blood_magic": [
                Modifier(
                    stat="ManaReservation",
                    value=0.0,
                    mod_type=ModifierType.BASE,
                    source="keystone:blood_magic",
                ),
                Modifier(
                    stat="Mana",
                    value=0.0,
                    mod_type=ModifierType.BASE,
                    source="keystone:blood_magic",
                ),
            ],
            "resolute_technique": [
                Modifier(
                    stat="HitChance",
                    value=100.0,
                    mod_type=ModifierType.FLAT,
                    source="keystone:resolute_technique",
                ),
                Modifier(
                    stat="CritChance",
                    value=0.0,
                    mod_type=ModifierType.BASE,
                    source="keystone:resolute_technique",
                ),
            ],
            "unwavering_stance": [
                Modifier(
                    stat="EvadeChance",
                    value=0.0,
                    mod_type=ModifierType.BASE,
                    source="keystone:unwavering_stance",
                ),
                Modifier(
                    stat="StunImmunity",
                    value=1.0,
                    mod_type=ModifierType.FLAG,
                    source="keystone:unwavering_stance",
                ),
            ],
            "vaal_pact": [
                Modifier(
                    stat="LifeRegen",
                    value=0.0,
                    mod_type=ModifierType.BASE,
                    source="keystone:vaal_pact",
                ),
                Modifier(
                    stat="LifeLeechInstant",
                    value=1.0,
                    mod_type=ModifierType.FLAG,
                    source="keystone:vaal_pact",
                ),
            ],
            "ghost_reaver": [
                Modifier(
                    stat="LifeLeech",
                    value=0.0,
                    mod_type=ModifierType.BASE,
                    source="keystone:ghost_reaver",
                ),
                Modifier(
                    stat="EnergyShieldLeech",
                    value=100.0,
                    mod_type=ModifierType.INCREASED,
                    source="keystone:ghost_reaver",
                ),
            ],
            "zealots_oath": [
                Modifier(
                    stat="LifeRegen",
                    value=0.0,
                    mod_type=ModifierType.BASE,
                    source="keystone:zealots_oath",
                ),
                Modifier(
                    stat="EnergyShieldRegen",
                    value=100.0,
                    mod_type=ModifierType.INCREASED,
                    source="keystone:zealots_oath",
                ),
            ],
            "ancestral_bond": [
                Modifier(
                    stat="CanDealDamage",
                    value=0.0,
                    mod_type=ModifierType.FLAG,
                    source="keystone:ancestral_bond",
                ),
                Modifier(
                    stat="TotemLimit",
                    value=1.0,
                    mod_type=ModifierType.FLAT,
                    source="keystone:ancestral_bond",
                ),
            ],
            "avatar_of_fire": [
                Modifier(
                    stat="PhysicalToFire",
                    value=50.0,
                    mod_type=ModifierType.FLAT,
                    source="keystone:avatar_of_fire",
                ),
                Modifier(
                    stat="ColdToFire",
                    value=50.0,
                    mod_type=ModifierType.FLAT,
                    source="keystone:avatar_of_fire",
                ),
                Modifier(
                    stat="LightningToFire",
                    value=50.0,
                    mod_type=ModifierType.FLAT,
                    source="keystone:avatar_of_fire",
                ),
                Modifier(
                    stat="ChaosDamage",
                    value=0.0,
                    mod_type=ModifierType.BASE,
                    source="keystone:avatar_of_fire",
                ),
            ],
            "point_blank": [
                Modifier(
                    stat="ProjectileDamage",
                    value=50.0,
                    mod_type=ModifierType.MORE,
                    source="keystone:point_blank",
                    conditions={"projectile_distance": "close"},
                ),
                Modifier(
                    stat="ProjectileDamage",
                    value=-50.0,
                    mod_type=ModifierType.MORE,
                    source="keystone:point_blank",
                    conditions={"projectile_distance": "far"},
                ),
            ],
            "phase_acrobatics": [
                Modifier(
                    stat="SpellDodgeChance",
                    value=30.0,
                    mod_type=ModifierType.FLAT,
                    source="keystone:phase_acrobatics",
                ),
            ],
            "arrow_dancing": [
                Modifier(
                    stat="MeleeEvadeChance",
                    value=-30.0,
                    mod_type=ModifierType.INCREASED,
                    source="keystone:arrow_dancing",
                ),
                Modifier(
                    stat="ProjectileEvadeChance",
                    value=30.0,
                    mod_type=ModifierType.INCREASED,
                    source="keystone:arrow_dancing",
                ),
            ],
            "eldritch_battery": [
                Modifier(
                    stat="EnergyShield",
                    value=0.0,
                    mod_type=ModifierType.BASE,
                    source="keystone:eldritch_battery",
                ),
                Modifier(
                    stat="ManaFromEnergyShield",
                    value=1.0,
                    mod_type=ModifierType.FLAG,
                    source="keystone:eldritch_battery",
                ),
            ],
            "elemental_equilibrium": [
                Modifier(
                    stat="ElementalEquilibrium",
                    value=1.0,
                    mod_type=ModifierType.FLAG,
                    source="keystone:elemental_equilibrium",
                ),
            ],
            "perfect_agony": [
                Modifier(
                    stat="CritMultiplierForDoT",
                    value=50.0,
                    mod_type=ModifierType.INCREASED,
                    source="keystone:perfect_agony",
                ),
            ],
            "crimson_dance": [
                Modifier(
                    stat="BleedStacks",
                    value=8.0,
                    mod_type=ModifierType.FLAT,
                    source="keystone:crimson_dance",
                ),
                Modifier(
                    stat="BleedDamage",
                    value=-50.0,
                    mod_type=ModifierType.INCREASED,
                    source="keystone:crimson_dance",
                ),
            ],
        }

        if keystone_name_lower in keystone_effects:
            return keystone_effects[keystone_name_lower]

        return modifiers

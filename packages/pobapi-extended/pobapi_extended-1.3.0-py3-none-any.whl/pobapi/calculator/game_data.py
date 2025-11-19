"""Game data structures and loaders.

This module provides structures for loading and accessing game data
from Path of Exile, such as passive tree nodes, skill gems, and unique items.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

__all__ = [
    "PassiveNode",
    "SkillGem",
    "UniqueItem",
    "GameDataLoader",
]


@dataclass
class PassiveNode:
    """Represents a passive skill tree node.

    This structure matches Path of Building's passive tree node structure
    from PassiveSkills.dat and tree JSON files.

    :param node_id: Unique node ID.
    :param name: Node name.
    :param stats: List of stat modifiers
        (e.g., ["+10 to Strength", "5% increased Life"]).
    :param is_keystone: Whether this is a keystone node.
    :param is_notable: Whether this is a notable node.
    :param is_jewel_socket: Whether this is a jewel socket.
    :param class_start: Whether this is a class starting node.
    :param mastery_effects: List of mastery effects (for mastery nodes).
    :param passive_skill_graph_id: ID in skill graph (from PassiveSkills.dat).
    :param flavour_text: Flavour text description.
    :param reminder_text_keys: Keys for reminder text.
    :param passive_skill_buffs_keys: Keys for passive skill buffs.
    :param stat_keys: List of stat keys (from StatsKeys in DAT).
    :param stat_values: List of stat values (from StatValues in DAT).
    :param icon_path: Path to icon file (Icon_DDSFile).
    :param skill_points_granted: Number of skill points granted (default: 1).
    :param x: X coordinate in tree (from tree JSON).
    :param y: Y coordinate in tree (from tree JSON).
    :param connections: List of connected node IDs (from tree JSON).
    :param is_mastery: Whether this is a mastery node.
    :param is_ascendancy: Whether this is an ascendancy node.
    """

    node_id: int
    name: str
    stats: list[str]
    is_keystone: bool = False
    is_notable: bool = False
    is_jewel_socket: bool = False
    class_start: bool = False
    mastery_effects: list[str] | None = None
    # New fields from PassiveSkills.dat
    passive_skill_graph_id: int | None = None
    flavour_text: str | None = None
    reminder_text_keys: list[str] = field(default_factory=list)
    passive_skill_buffs_keys: list[str] = field(default_factory=list)
    stat_keys: list[str] = field(default_factory=list)
    stat_values: list[int | float] = field(default_factory=list)
    icon_path: str | None = None
    skill_points_granted: int = 1
    # Geometry from tree JSON
    x: float | None = None
    y: float | None = None
    connections: list[int] = field(default_factory=list)
    # Additional flags
    is_mastery: bool = False
    is_ascendancy: bool = False


@dataclass
class SkillGem:
    """Represents a skill gem.

    This structure matches Path of Building's gem data structure from Data/Gems.lua
    and Data/Skills/*.lua files.

    :param name: Gem name.
    :param base_damage: Base damage by type (dict with "Physical", "Fire", etc.).
    :param damage_effectiveness: Damage effectiveness percentage.
    :param cast_time: Base cast time (for spells).
    :param attack_time: Base attack time (for attacks).
    :param mana_cost: Base mana cost.
    :param mana_cost_percent: Mana cost as percentage of base mana.
    :param quality_stats: List of quality bonus stats.
    :param level_stats: List of level-up stats (per level).
    :param is_attack: Whether this is an attack skill.
    :param is_spell: Whether this is a spell skill.
    :param is_totem: Whether this is a totem skill.
    :param is_trap: Whether this is a trap skill.
    :param is_mine: Whether this is a mine skill.
    :param game_id: Game ID (e.g., "Metadata/Items/Gems/SkillGemFireball").
    :param variant_id: Variant ID (e.g., "Fireball").
    :param granted_effect_id: ID of the skill this gem grants (links to Skills data).
    :param secondary_granted_effect_id: Secondary effect ID for Vaal gems.
    :param req_str: Required Strength.
    :param req_dex: Required Dexterity.
    :param req_int: Required Intelligence.
    :param tags: List of gem tags (e.g., ["spell", "fire", "projectile"]).
    :param tag_string: Comma-separated tag string
        (e.g., "Projectile, Spell, AoE, Fire").
    :param natural_max_level: Natural maximum level of the gem.
    :param base_type_name: Base type name (e.g., "Fireball").
    :param is_vaal: Whether this is a Vaal gem.
    :param is_support: Whether this is a support gem.
    :param granted_effect: Reference to the Skill object (set after loading).
    """

    name: str
    base_damage: dict[str, tuple[float, float]] = field(
        default_factory=dict
    )  # (min, max) for each damage type
    damage_effectiveness: float = 100.0
    cast_time: float | None = None
    attack_time: float | None = None
    mana_cost: float | None = None
    mana_cost_percent: float | None = None
    quality_stats: list[str] = field(default_factory=list)
    level_stats: list[str] = field(default_factory=list)
    is_attack: bool = False
    is_spell: bool = False
    is_totem: bool = False
    is_trap: bool = False
    is_mine: bool = False
    # New fields from Lua Gems.lua structure
    game_id: str | None = None
    variant_id: str | None = None
    granted_effect_id: str | None = None
    secondary_granted_effect_id: str | None = None
    req_str: int = 0
    req_dex: int = 0
    req_int: int = 0
    tags: list[str] = field(default_factory=list)
    tag_string: str | None = None
    natural_max_level: int = 20
    base_type_name: str | None = None
    is_vaal: bool = False
    is_support: bool = False
    granted_effect: "Any | None" = None  # Reference to Skill object

    def __post_init__(self):
        """Initialize default values."""
        pass


@dataclass
class UniqueItem:
    """Represents a unique item with special effects.

    :param name: Unique item name.
    :param base_type: Base item type (e.g., "Leather Belt").
    :param special_effects: List of special effect descriptions.
    :param implicit_mods: List of implicit modifiers.
    :param explicit_mods: List of explicit modifiers.
    """

    name: str
    base_type: str
    special_effects: list[str]
    implicit_mods: list[str] | None = None
    explicit_mods: list[str] | None = None

    def __post_init__(self):
        """Initialize default values."""
        if self.implicit_mods is None:
            self.implicit_mods = []
        if self.explicit_mods is None:
            self.explicit_mods = []


class GameDataLoader:
    """Loader for game data files.

    This class loads game data from various sources:
    - Passive tree nodes (from nodes.json or similar)
    - Skill gems (from gems.json or similar)
    - Unique items (from uniques.json or similar)

    In Path of Building (Lua), game data is loaded from:
    1. Built-in Lua tables in src/Data/ folder
    2. Parsed .dat files from Path of Exile game directory
    3. Updated data from community sources

    Our implementation supports loading from JSON files, which can be:
    - Extracted from PoB's Lua tables
    - Generated from .dat file parsers
    - Created from community sources
    """

    def __init__(self, data_directory: str | None = None):
        """Initialize game data loader.

        :param data_directory: Optional directory path to search for data files.
            If None, will search in standard locations:
            - Current directory
            - ./data/
            - ./pobapi/data/
            - Environment variable POBAPI_DATA_DIR
        """
        self._passive_nodes: dict[int, PassiveNode] = {}
        self._skill_gems: dict[str, SkillGem] = {}
        self._unique_items: dict[str, UniqueItem] = {}
        self.data_directory = data_directory
        self._data_paths: list[str] = []  # For testing purposes

    def _find_data_file(self, filename: str) -> str | None:
        """Find data file in standard locations.

        :param filename: Name of the data file (e.g., "nodes.json").
        :return: Path to the file if found, None otherwise.
        """
        import os

        # List of directories to search
        search_dirs: list[str] = []

        # 1. Explicit data directory
        if self.data_directory:
            search_dirs.append(self.data_directory)

        # 2. Environment variable
        env_data_dir = os.environ.get("POBAPI_DATA_DIR")
        if env_data_dir:
            search_dirs.append(env_data_dir)

        # 3. Standard locations
        search_dirs.extend(
            [
                ".",  # Current directory
                "./data",
                "./pobapi/data",
                os.path.join(
                    os.path.dirname(__file__), "data"
                ),  # pobapi/calculator/data
            ]
        )

        # Search for file
        for directory in search_dirs:
            if directory and os.path.isdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.exists(file_path):
                    return file_path

        return None

    def load_passive_tree_data(
        self, data_path: str | None = None
    ) -> dict[int, PassiveNode]:
        """Load passive tree node data.

        In Path of Building (Lua), this data comes from:
        - Built-in Lua tables in src/Data/PassiveSkills.lua
        - Parsed from PassiveSkills.dat file from game directory

        Our implementation loads from JSON files that can be:
        - Extracted from PoB's Lua tables
        - Generated from .dat file parsers

        :param data_path: Path to nodes.json file (optional).
            If None, will search in standard locations.
        :return: Dictionary mapping node_id -> PassiveNode.
        """
        import json
        import os

        # If no path provided, try to find it
        if not data_path:
            data_path = self._find_data_file("nodes.json")

        if data_path and os.path.exists(data_path):
            try:
                with open(data_path, encoding="utf-8") as f:
                    data = json.load(f)
                    # Parse nodes from JSON structure
                    # Expected format: {"nodes": {node_id: {name, stats, ...}}}
                    if isinstance(data, dict) and "nodes" in data:
                        for node_id_str, node_data in data["nodes"].items():
                            node_id = int(node_id_str)
                            node = PassiveNode(
                                node_id=node_id,
                                name=node_data.get("name", f"node_{node_id}"),
                                stats=node_data.get("stats", []),
                                is_keystone=node_data.get("isKeystone", False),
                                is_notable=node_data.get("isNotable", False),
                                is_jewel_socket=node_data.get("isJewelSocket", False),
                                class_start=node_data.get("classStart", False),
                                mastery_effects=node_data.get("masteryEffects"),
                                # New fields from PassiveSkills.dat
                                passive_skill_graph_id=node_data.get(
                                    "passiveSkillGraphId"
                                ),
                                flavour_text=node_data.get("flavourText"),
                                reminder_text_keys=node_data.get(
                                    "reminderTextKeys", []
                                ),
                                passive_skill_buffs_keys=node_data.get(
                                    "passiveSkillBuffsKeys", []
                                ),
                                stat_keys=node_data.get("statKeys", []),
                                stat_values=node_data.get("statValues", []),
                                icon_path=node_data.get("iconPath"),
                                skill_points_granted=node_data.get(
                                    "skillPointsGranted", 1
                                ),
                                # Geometry from tree JSON
                                x=node_data.get("x"),
                                y=node_data.get("y"),
                                connections=node_data.get("connections", []),
                                # Additional flags
                                is_mastery=node_data.get("isMastery", False),
                                is_ascendancy=node_data.get("isAscendancy", False),
                            )
                            self._passive_nodes[node_id] = node
            except (json.JSONDecodeError, KeyError, ValueError, OSError):
                # If file doesn't exist or is invalid, return empty dict
                pass

        return self._passive_nodes

    def load_skill_gem_data(self, data_path: str | None = None) -> dict[str, SkillGem]:
        """Load skill gem data.

        In Path of Building (Lua), this data comes from:
        - Built-in Lua tables in src/Data/Skills.lua
        - Parsed from skills.dat file from game directory

        Our implementation loads from JSON files that can be:
        - Extracted from PoB's Lua tables
        - Generated from .dat file parsers

        :param data_path: Path to gems.json file (optional).
            If None, will search in standard locations.
        :return: Dictionary mapping gem_name -> SkillGem.
        """
        import json
        import os

        # If no path provided, try to find it
        if not data_path:
            data_path = self._find_data_file("gems.json")

        if data_path and os.path.exists(data_path):
            try:
                with open(data_path, encoding="utf-8") as f:
                    data = json.load(f)
                    # Parse gems from JSON structure
                    # Expected format: {"gems": {gem_name: {baseDamage, ...}}}
                    if isinstance(data, dict) and "gems" in data:
                        for gem_name, gem_data in data["gems"].items():
                            base_damage = {}
                            if "baseDamage" in gem_data:
                                for dmg_type, dmg_range in gem_data[
                                    "baseDamage"
                                ].items():
                                    if (
                                        isinstance(dmg_range, list | tuple)
                                        and len(dmg_range) == 2
                                    ):
                                        base_damage[dmg_type] = (
                                            float(dmg_range[0]),
                                            float(dmg_range[1]),
                                        )

                            gem = SkillGem(
                                name=gem_data.get("name", gem_name),
                                base_damage=base_damage,
                                damage_effectiveness=gem_data.get(
                                    "damageEffectiveness", 100.0
                                ),
                                cast_time=gem_data.get("castTime"),
                                attack_time=gem_data.get("attackTime"),
                                mana_cost=gem_data.get("manaCost"),
                                mana_cost_percent=gem_data.get("manaCostPercent"),
                                quality_stats=gem_data.get("qualityStats", []),
                                level_stats=gem_data.get("levelStats", []),
                                is_attack=gem_data.get("isAttack", False),
                                is_spell=gem_data.get("isSpell", False),
                                is_totem=gem_data.get("isTotem", False),
                                is_trap=gem_data.get("isTrap", False),
                                is_mine=gem_data.get("isMine", False),
                                # New fields from Lua structure
                                game_id=gem_data.get("gameId"),
                                variant_id=gem_data.get("variantId"),
                                granted_effect_id=gem_data.get("grantedEffectId"),
                                secondary_granted_effect_id=gem_data.get(
                                    "secondaryGrantedEffectId"
                                ),
                                req_str=gem_data.get("reqStr", 0),
                                req_dex=gem_data.get("reqDex", 0),
                                req_int=gem_data.get("reqInt", 0),
                                tags=gem_data.get("tags", []),
                                tag_string=gem_data.get("tagString"),
                                natural_max_level=gem_data.get("naturalMaxLevel", 20),
                                base_type_name=gem_data.get("baseTypeName"),
                                is_vaal=gem_data.get("isVaal", False),
                                is_support=gem_data.get("isSupport", False),
                            )
                            self._skill_gems[gem_name] = gem
            except (json.JSONDecodeError, KeyError, ValueError, OSError):
                # If file doesn't exist or is invalid, return empty dict
                pass

        return self._skill_gems

    def load_unique_item_data(
        self, data_path: str | None = None
    ) -> dict[str, UniqueItem]:
        """Load unique item data.

        In Path of Building (Lua), this data comes from:
        - Built-in Lua tables in src/Data/Uniques.lua
        - Parsed from items.dat file from game directory

        Our implementation loads from JSON files that can be:
        - Extracted from PoB's Lua tables
        - Generated from .dat file parsers
        - Created from UniqueItemParser database

        :param data_path: Path to uniques.json file (optional).
            If None, will search in standard locations.
        :return: Dictionary mapping unique_name -> UniqueItem.
        """
        import json
        import os

        # If no path provided, try to find it
        if not data_path:
            # Try processed file first (from scraping), then regular uniques.json
            data_path = self._find_data_file("uniques_processed.json")
            if not data_path:
                data_path = self._find_data_file("uniques.json")

        if data_path and os.path.exists(data_path):
            try:
                with open(data_path, encoding="utf-8") as f:
                    data = json.load(f)
                    # Parse uniques from JSON structure
                    # Expected format:
                    # {"uniques": {unique_name: {baseType, effects, ...}}}
                    if isinstance(data, dict) and "uniques" in data:
                        for unique_name, unique_data in data["uniques"].items():
                            # Support both formats:
                            # camelCase (from PoB) and snake_case (from scraping)
                            name = unique_data.get("name", unique_name)
                            base_type = unique_data.get("baseType") or unique_data.get(
                                "base_type", ""
                            )
                            special_effects = unique_data.get(
                                "specialEffects"
                            ) or unique_data.get("special_effects", [])
                            implicit_mods = unique_data.get(
                                "implicitMods"
                            ) or unique_data.get("implicit_mods", [])
                            explicit_mods = unique_data.get(
                                "explicitMods"
                            ) or unique_data.get("explicit_mods", [])

                            unique = UniqueItem(
                                name=name,
                                base_type=base_type,
                                special_effects=special_effects,
                                implicit_mods=implicit_mods,
                                explicit_mods=explicit_mods,
                            )
                            # Use normalized name as key (lowercase, no spaces)
                            key = name.lower().replace(" ", "").replace("'", "")
                            self._unique_items[key] = unique
                            # Also store by original name
                            self._unique_items[unique_name] = unique
            except (json.JSONDecodeError, KeyError, ValueError, OSError):
                # If file doesn't exist or is invalid, return empty dict
                pass

        return self._unique_items

    def get_passive_node(self, node_id: int) -> PassiveNode | None:
        """Get passive node by ID.

        :param node_id: Node ID.
        :return: PassiveNode or None if not found.
        """
        return self._passive_nodes.get(node_id)

    def get_skill_gem(self, gem_name: str) -> SkillGem | None:
        """Get skill gem by name.

        :param gem_name: Gem name.
        :return: SkillGem or None if not found.
        """
        return self._skill_gems.get(gem_name)

    def get_unique_item(self, unique_name: str) -> UniqueItem | None:
        """Get unique item by name.

        :param unique_name: Unique item name.
        :return: UniqueItem or None if not found.
        """
        # Try exact match first
        if unique_name in self._unique_items:
            return self._unique_items[unique_name]

        # Try normalized name (lowercase, no spaces, no apostrophes)
        normalized = unique_name.lower().replace(" ", "").replace("'", "")
        if normalized in self._unique_items:
            return self._unique_items[normalized]

        # Try case-insensitive search
        for key, item in self._unique_items.items():
            if (
                key.lower() == unique_name.lower()
                or item.name.lower() == unique_name.lower()
            ):
                return item

        return None

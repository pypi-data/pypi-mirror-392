"""Path of Building calculation engine ported from Lua to Python.

This module provides a complete calculation engine that replicates
Path of Building's Lua-based calculations in Python.
"""

from pobapi.calculator.conditional import ConditionEvaluator
from pobapi.calculator.config_modifier_parser import ConfigModifierParser
from pobapi.calculator.damage import DamageCalculator, DamageType
from pobapi.calculator.defense import DefenseCalculator
from pobapi.calculator.engine import CalculationEngine
from pobapi.calculator.game_data import (
    GameDataLoader,
    PassiveNode,
    SkillGem,
    UniqueItem,
)
from pobapi.calculator.item_modifier_parser import ItemModifierParser
from pobapi.calculator.jewel_parser import JewelParser, JewelType
from pobapi.calculator.legion_jewels import (
    LegionJewelData,
    LegionJewelHelper,
    LegionJewelType,
)
from pobapi.calculator.minion import MinionCalculator, MinionStats
from pobapi.calculator.mirage import MirageCalculator, MirageStats
from pobapi.calculator.modifiers import ModifierSystem
from pobapi.calculator.pantheon import PantheonGod, PantheonSoul, PantheonTools
from pobapi.calculator.party import PartyCalculator, PartyMember
from pobapi.calculator.passive_tree_parser import PassiveTreeParser
from pobapi.calculator.penetration import PenetrationCalculator
from pobapi.calculator.resource import ResourceCalculator
from pobapi.calculator.skill_modifier_parser import SkillModifierParser
from pobapi.calculator.skill_stats import SkillStatsCalculator
from pobapi.calculator.unique_item_parser import UniqueItemParser
from pobapi.calculator.unique_items_extended import EXTENDED_UNIQUE_EFFECTS

__all__ = [
    "EXTENDED_UNIQUE_EFFECTS",
    "CalculationEngine",
    "ModifierSystem",
    "DamageCalculator",
    "DamageType",
    "DefenseCalculator",
    "ResourceCalculator",
    "SkillStatsCalculator",
    "PenetrationCalculator",
    "MinionCalculator",
    "MinionStats",
    "PartyCalculator",
    "PartyMember",
    "ItemModifierParser",
    "PassiveTreeParser",
    "SkillModifierParser",
    "ConfigModifierParser",
    "ConditionEvaluator",
    "UniqueItemParser",
    "GameDataLoader",
    "PassiveNode",
    "SkillGem",
    "UniqueItem",
    "JewelParser",
    "JewelType",
    "MirageCalculator",
    "MirageStats",
    "LegionJewelData",
    "LegionJewelHelper",
    "LegionJewelType",
    "PantheonGod",
    "PantheonSoul",
    "PantheonTools",
]

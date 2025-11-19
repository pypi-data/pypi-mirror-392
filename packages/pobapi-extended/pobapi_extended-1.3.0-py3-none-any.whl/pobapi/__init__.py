import logging

from .api import PathOfBuildingAPI, create_build, from_import_code, from_url
from .builders import ConfigBuilder, StatsBuilder
from .cache import clear_cache, get_cache
from .exceptions import (
    InvalidImportCodeError,
    InvalidURLError,
    NetworkError,
    ParsingError,
    PobAPIError,
    ValidationError,
)
from .factory import BuildFactory
from .types import (
    Ascendancy,
    BanditChoice,
    CharacterClass,
    DamageType,
    ItemSlot,
    ModType,
    PassiveNodeID,
    SkillName,
)

VERSION = "0.6.0"
PROJECT = "Path Of Building API"
COPYRIGHT = "2020, Peter Pölzl"
AUTHOR = "Peter Pölzl"

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = [
    "PathOfBuildingAPI",
    "from_url",
    "from_import_code",
    "create_build",
    "BuildFactory",
    "StatsBuilder",
    "ConfigBuilder",
    "CharacterClass",
    "Ascendancy",
    "ItemSlot",
    "BanditChoice",
    "SkillName",
    "PassiveNodeID",
    "DamageType",
    "ModType",
    "PobAPIError",
    "InvalidImportCodeError",
    "InvalidURLError",
    "NetworkError",
    "ParsingError",
    "ValidationError",
    "clear_cache",
    "get_cache",
]

# Calculation engine (experimental)
try:
    from pobapi.calculator import (  # noqa: F401
        CalculationEngine,
        ConditionEvaluator,
        ConfigModifierParser,
        DamageCalculator,
        DefenseCalculator,
        GameDataLoader,
        ItemModifierParser,
        ModifierSystem,
        PassiveNode,
        PassiveTreeParser,
        PenetrationCalculator,
        ResourceCalculator,
        SkillGem,
        SkillModifierParser,
        SkillStatsCalculator,
        UniqueItem,
        UniqueItemParser,
    )

    __all__.extend(
        [
            "CalculationEngine",
            "DamageCalculator",
            "DefenseCalculator",
            "ModifierSystem",
            "ResourceCalculator",
            "SkillStatsCalculator",
            "PenetrationCalculator",
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
        ]
    )
except ImportError:
    pass

# Crafting API
try:
    from pobapi.crafting import (  # noqa: F401
        CraftingModifier,
        CraftingResult,
        ItemCraftingAPI,
        ItemModifier,
        ModifierTier,
    )

    __all__.extend(
        [
            "ItemCraftingAPI",
            "ItemModifier",
            "CraftingModifier",
            "CraftingResult",
            "ModifierTier",
        ]
    )
except ImportError:
    pass

# Trade API
try:
    from pobapi.trade import (  # noqa: F401
        FilterType,
        PriceRange,
        TradeAPI,
        TradeFilter,
        TradeQuery,
        TradeResult,
    )

    __all__.extend(
        [
            "TradeAPI",
            "TradeFilter",
            "TradeQuery",
            "TradeResult",
            "PriceRange",
            "FilterType",
        ]
    )
except ImportError:
    pass

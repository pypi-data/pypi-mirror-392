"""Type definitions and enums for Path of Building API."""

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

__all__ = [
    "CharacterClass",
    "Ascendancy",
    "ItemSlot",
    "BanditChoice",
    "SkillName",
    "PassiveNodeID",
    "DamageType",
    "ResistanceType",
    "SocketColor",
    "ItemRarity",
    "ItemType",
    "FlaskType",
    "ChargeType",
    "InfluenceType",
    "ModType",
    "SkillType",
    "DefenseType",
]


class CharacterClass(str, Enum):
    """Character class names."""

    SCION = "Scion"
    WITCH = "Witch"
    RANGER = "Ranger"
    DUELIST = "Duelist"
    MARAUDER = "Marauder"
    TEMPLAR = "Templar"
    SHADOW = "Shadow"


class Ascendancy(str, Enum):
    """Ascendancy class names."""

    # Scion
    ASCENDANT = "Ascendant"

    # Witch
    NECROMANCER = "Necromancer"
    ELEMENTALIST = "Elementalist"
    OCCULTIST = "Occultist"

    # Ranger
    DEADEYE = "Deadeye"
    WARDEN = "Warden"
    PATHFINDER = "Pathfinder"

    # Duelist
    SLAYER = "Slayer"
    GLADIATOR = "Gladiator"
    CHAMPION = "Champion"

    # Marauder
    JUGGERNAUT = "Juggernaut"
    BERSERKER = "Berserker"
    CHIEFTAIN = "Chieftain"

    # Templar
    INQUISITOR = "Inquisitor"
    HIEROPHANT = "Hierophant"
    GUARDIAN = "Guardian"

    # Shadow
    ASSASSIN = "Assassin"
    TRICKSTER = "Trickster"
    SABOTEUR = "Saboteur"


class ItemSlot(str, Enum):
    """Item slot names for equipping items."""

    WEAPON1 = "Weapon1"
    WEAPON1_SWAP = "Weapon1 Swap"
    WEAPON2 = "Weapon2"
    WEAPON2_SWAP = "Weapon2 Swap"
    HELMET = "Helmet"
    BODY_ARMOUR = "Body Armour"
    GLOVES = "Gloves"
    BOOTS = "Boots"
    AMULET = "Amulet"
    RING1 = "Ring1"
    RING2 = "Ring2"
    BELT = "Belt"
    FLASK1 = "Flask1"
    FLASK2 = "Flask2"
    FLASK3 = "Flask3"
    FLASK4 = "Flask4"
    FLASK5 = "Flask5"


class BanditChoice(str, Enum):
    """Bandit choice options."""

    ALIRA = "Alira"
    OAK = "Oak"
    KRAITYN = "Kraityn"
    NONE = None


class SkillName(str, Enum):
    """Common skill gem names."""

    # Attack skills
    CYCLONE = "Cyclone"
    BLADE_VORTEX = "Blade Vortex"
    SPECTRAL_THROW = "Spectral Throw"
    LIGHTNING_STRIKE = "Lightning Strike"
    MOLTEN_STRIKE = "Molten Strike"
    FROST_BLADES = "Frost Blades"
    REAVE = "Reave"
    CLEAVE = "Cleave"
    DOUBLE_STRIKE = "Double Strike"
    HEAVY_STRIKE = "Heavy Strike"
    GROUND_SLAM = "Ground Slam"
    SUNDER = "Sunder"
    EARTHQUAKE = "Earthquake"
    TECTONIC_STRIKE = "Tectonic Strike"
    ICE_CRASH = "Ice Crash"
    WILDSTRIKE = "Wild Strike"
    LACERATE = "Lacerate"
    BLADE_FLURRY = "Blade Flurry"
    SHIELD_CHARGE = "Shield Charge"
    WHIRLING_BLADES = "Whirling Blades"
    LEAP_SLAM = "Leap Slam"
    FLAME_DASH = "Flame Dash"
    LIGHTNING_WARP = "Lightning Warp"
    BODY_SWAP = "Body Swap"

    # Spell skills
    FIREBALL = "Fireball"
    ICE_SHOT = "Ice Shot"
    LIGHTNING_ARROW = "Lightning Arrow"
    ARCTIC_BREATH = "Arctic Breath"
    FREEZING_PULSE = "Freezing Pulse"
    FROSTBOLT = "Frostbolt"
    ICE_NOVA = "Ice Nova"
    GLACIAL_CASCADE = "Glacial Cascade"
    FROSTBOMB = "Frost Bomb"
    COLD_SNAP = "Cold Snap"
    VORTEX = "Vortex"
    WINTER_ORB = "Winter Orb"
    FROSTBLINK = "Frostblink"
    FIRE_TOTEM = "Fire Totem"
    FLAME_TOTEM = "Flame Totem"
    SEARING_TOTEM = "Searing Totem"
    SPARK = "Spark"
    ARC = "Arc"
    LIGHTNING_TENDRILLS = "Lightning Tendrils"
    BALL_LIGHTNING = "Ball Lightning"
    STORM_CALL = "Storm Call"
    DISCHARGE = "Discharge"
    LIGHTNING_TRAP = "Lightning Trap"
    SHOCK_NOVA = "Shock Nova"
    ORB_OF_STORMS = "Orb of Storms"
    WAVE_OF_CONVICTION = "Wave of Conviction"
    PURIFYING_FLAME = "Purifying Flame"
    DIVINE_IRE = "Divine Ire"
    ARMAGEDDON_BRAND = "Armageddon Brand"
    STORM_BRAND = "Storm Brand"
    PENANCE_BRAND = "Penance Brand"
    WINTERTIDE_BRAND = "Wintertide Brand"
    CREMATION = "Cremation"
    DETONATE_DEAD = "Detonate Dead"
    VOLATILE_DEAD = "Volatile Dead"
    UNEARTH = "Unearth"
    BODYSWAP = "Bodyswap"
    FIRE_NOVA_MINE = "Fire Nova Mine"
    PYROCLAST_MINE = "Pyroclast Mine"
    FLAME_SURGE = "Flame Surge"
    SCORCHING_RAY = "Scorching Ray"
    INCINERATE = "Incinerate"
    FLAMEBLAST = "Flameblast"
    FIRE_STORM = "Fire Storm"
    MAGMA_ORB = "Magma Orb"
    MOLTEN_SHELL = "Molten Shell"
    RIGHTEOUS_FIRE = "Righteous Fire"
    FLAMEWALL = "Flame Wall"
    EXPLOSIVE_TRAP = "Explosive Trap"
    FIRE_TRAP = "Fire Trap"
    BLAZING_SALVO = "Blazing Salvo"
    FORBIDDEN_RITE = "Forbidden Rite"
    EYE_OF_WINTER = "Eye of Winter"
    HYDROSPHERE = "Hydrosphere"
    FROSTBOLT_NOVA = "Frostbolt Nova"
    ICICLE_MINE = "Icicle Mine"
    ICE_TRAP = "Ice Trap"
    COLD_CONVERT = "Cold Convert"

    # Minion skills
    RAISE_ZOMBIE = "Raise Zombie"
    RAISE_SPECTRE = "Raise Spectre"
    SKELETAL_WARRIORS = "Skeletal Warriors"
    SUMMON_SKELETON = "Summon Skeleton"
    SUMMON_RAGING_SPIRIT = "Summon Raging Spirit"
    ANIMATE_GUARDIAN = "Animate Guardian"
    ANIMATE_WEAPON = "Animate Weapon"
    DOMINATING_BLOW = "Dominating Blow"
    HERALD_OF_AGONY = "Herald of Agony"
    HERALD_OF_PURITY = "Herald of Purity"
    HERALD_OF_ASH = "Herald of Ash"
    HERALD_OF_ICE = "Herald of Ice"
    HERALD_OF_THUNDER = "Herald of Thunder"

    # Support gems
    MULTI_STRIKE = "Multistrike"
    MELEE_PHYSICAL = "Melee Physical Damage"
    ADDED_FIRE = "Added Fire Damage"
    ELEMENTAL_DAMAGE = "Elemental Damage with Attacks"
    WEAPON_ELEMENTAL = "Weapon Elemental Damage"
    CONCENTRATED_EFFECT = "Concentrated Effect"
    INCREASED_AREA = "Increased Area of Effect"
    CAST_ON_CRIT = "Cast on Critical Strike"
    CAST_ON_MELEE_KILL = "Cast on Melee Kill"
    CAST_WHEN_DAMAGE_TAKEN = "Cast when Damage Taken"
    CAST_WHEN_STUNNED = "Cast when Stunned"
    CAST_ON_DEATH = "Cast on Death"
    SPELL_ECHO = "Spell Echo"
    FASTER_CASTING = "Faster Casting"
    FASTER_ATTACKS = "Faster Attacks"
    INCREASED_DURATION = "Increased Duration"
    ELEMENTAL_FOCUS = "Elemental Focus"
    CONTROLLED_DESTRUCTION = "Controlled Destruction"
    ELEMENTAL_PENETRATION = "Elemental Penetration"
    FIRE_PENETRATION = "Fire Penetration"
    COLD_PENETRATION = "Cold Penetration"
    LIGHTNING_PENETRATION = "Lightning Penetration"
    CHAIN = "Chain"
    FORK = "Fork"
    PIERCE = "Pierce"
    GMP = "Greater Multiple Projectiles"
    LMP = "Lesser Multiple Projectiles"
    FASTER_PROJECTILES = "Faster Projectiles"
    SLOWER_PROJECTILES = "Slower Projectiles"
    POINT_BLANK = "Point Blank"
    MINION_DAMAGE = "Minion Damage"
    MINION_LIFE = "Minion Life"
    MINION_SPEED = "Minion Speed"
    EMPOWER = "Empower"
    ENLIGHTEN = "Enlighten"
    ENHANCE = "Enhance"


class PassiveNodeID:
    """Passive tree node ID constants.

    This class provides named constants for common passive tree nodes
    to avoid using magic numbers.
    """

    # Keystones
    ELEMENTAL_EQUILIBRIUM = 39085
    ANCESTRAL_BOND = 6230
    MINION_INSTABILITY = 55906
    ZEALOTS_OATH = 10490
    CI = 55373  # Chaos Inoculation
    PAIN_ATTUNEMENT = 26740
    MOONSHINE = 33479
    BLOOD_MAGIC = 38048
    RESOLUTE_TECHNIQUE = 63976
    UNWAVERING_STANCE = 63977
    IRON_REFLEXES = 63978
    ONDARS_GUILE = 63979
    ACROBATICS = 63980
    PHASE_ACROBATICS = 63981
    VAAL_PACT = 63982
    GHOST_REAVER = 63983
    MIND_OVER_MATTER = 63984
    ELDRITCH_BATTERY = 63985
    INFERNAL_BLOW = 63986
    ELEMENTAL_OVERLOAD = 63987
    PERFECT_AGONY = 63988
    WICKED_WARD = 63989
    WIND_DANCER = 63990
    PERFECT_FORM = 63991
    THE_AGNOSTIC = 63992
    DIVINE_GUIDANCE = 63993
    DIVINE_SHIELD = 63994
    DIVINE_FLESH = 63995
    DIVINE_INFERNAL = 63996
    DIVINE_GRACE = 63997
    DIVINE_JUDGEMENT = 63998
    DIVINE_WRATH = 63999
    DIVINE_PUNISHMENT = 64000
    DIVINE_RETRIBUTION = 64001
    DIVINE_VENGEANCE = 64002
    DIVINE_CRUSADE = 64003
    DIVINE_ASCENDANCY = 64004
    DIVINE_MASTERY = 64005
    DIVINE_SUPREMACY = 64006
    DIVINE_TRANSCENDENCE = 64007
    DIVINE_APOTHEOSIS = 64008
    DIVINE_OMNIPOTENCE = 64009
    DIVINE_OMNISCIENCE = 64010
    DIVINE_OMNIPRESENCE = 64011

    # Notable nodes (examples - can be expanded)
    # Life nodes
    LIFE_AND_MANA = 1
    LIFE = 2

    # Damage nodes
    INCREASED_DAMAGE = 3
    INCREASED_ELEMENTAL_DAMAGE = 4
    INCREASED_PHYSICAL_DAMAGE = 5

    @classmethod
    def get_name(cls, node_id: int) -> str | None:
        """Get name of node ID if it's a known constant.

        :param node_id: Node ID to look up.
        :return: Name of the node or None if not found.
        """
        for name, value in cls.__dict__.items():
            if isinstance(value, int) and value == node_id:
                return name
        return None

    @classmethod
    def get_id(cls, name: str) -> int | None:
        """Get node ID by name.

        :param name: Name of the node constant.
        :return: Node ID or None if not found.
        """
        return getattr(cls, name.upper(), None)


class DamageType(str, Enum):
    """Damage type constants."""

    PHYSICAL = "Physical"
    FIRE = "Fire"
    COLD = "Cold"
    LIGHTNING = "Lightning"
    CHAOS = "Chaos"
    ELEMENTAL = "Elemental"  # Fire + Cold + Lightning


class ResistanceType(str, Enum):
    """Resistance type constants."""

    FIRE = "Fire"
    COLD = "Cold"
    LIGHTNING = "Lightning"
    CHAOS = "Chaos"
    ELEMENTAL = "Elemental"  # Fire + Cold + Lightning


class SocketColor(str, Enum):
    """Socket color constants."""

    RED = "R"
    GREEN = "G"
    BLUE = "B"
    WHITE = "W"  # Prismatic socket


class ItemRarity(str, Enum):
    """Item rarity constants."""

    NORMAL = "Normal"
    MAGIC = "Magic"
    RARE = "Rare"
    UNIQUE = "Unique"


class ItemType(str, Enum):
    """Item type categories."""

    WEAPON = "Weapon"
    ARMOUR = "Armour"
    ACCESSORY = "Accessory"
    FLASK = "Flask"
    JEWEL = "Jewel"
    QUIVER = "Quiver"
    SHIELD = "Shield"


class FlaskType(str, Enum):
    """Flask type constants."""

    LIFE = "Life"
    MANA = "Mana"
    HYBRID = "Hybrid"
    UTILITY = "Utility"


class ChargeType(str, Enum):
    """Charge type constants."""

    POWER = "Power"
    FRENZY = "Frenzy"
    ENDURANCE = "Endurance"


class InfluenceType(str, Enum):
    """Item influence type constants."""

    SHAPER = "Shaper"
    ELDER = "Elder"
    CRUSADER = "Crusader"
    HUNTER = "Hunter"
    REDEEMER = "Redeemer"
    WARLORD = "Warlord"


class ModType(str, Enum):
    """Modifier type constants for items."""

    PREFIX = "prefix"
    SUFFIX = "suffix"
    IMPLICIT = "implicit"
    ENCHANT = "enchant"
    CRAFTED = "crafted"


class SkillType(str, Enum):
    """Skill type categories."""

    ATTACK = "Attack"
    SPELL = "Spell"
    MINION = "Minion"
    SUPPORT = "Support"
    AURA = "Aura"
    CURSE = "Curse"
    HERALD = "Herald"
    GUARDIAN_SKILL = "Guardian Skill"
    MOVEMENT = "Movement"
    TRAP = "Trap"
    MINE = "Mine"
    TOTEM = "Totem"
    BRAND = "Brand"


class DefenseType(str, Enum):
    """Defense type constants."""

    ARMOUR = "Armour"
    EVASION = "Evasion"
    ENERGY_SHIELD = "Energy Shield"
    WARD = "Ward"
    BLOCK = "Block"
    SPELL_BLOCK = "Spell Block"
    DODGE = "Dodge"
    SPELL_DODGE = "Spell Dodge"
    SPELL_SUPPRESSION = "Spell Suppression"

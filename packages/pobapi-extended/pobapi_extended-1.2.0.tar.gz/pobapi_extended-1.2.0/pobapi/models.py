from abc import ABC
from dataclasses import asdict, dataclass

__all__ = ["Gem", "GrantedAbility", "SkillGroup", "Tree", "Keystones", "Item", "Set"]


class Ability(ABC):
    """Abstract class that holds the data of an ability..

    :param name: Ability name.
    :param enabled: Whether the ability is in active use.
    :param level: Ability level."""

    name: str
    enabled: bool
    level: int


@dataclass
class Gem(Ability):
    """Class that holds the data of an ability granted by a skill gem.

    :param name: Skill gem name.
    :param enabled: Whether the skill gem is in active use.
    :param level: Skill gem level.
    :param quality: Skill gem quality.
    :param support: Whether the skill gem is a support gem."""

    name: str
    enabled: bool
    level: int
    quality: int
    support: bool

    def __post_init__(self):
        """Validate gem data after initialization."""
        from pobapi.model_validators import (
            ModelValidator,
            validate_gem_level,
            validate_gem_quality,
        )

        ModelValidator.validate_not_empty(self.name, "name")
        validate_gem_level(self.level, "level")
        validate_gem_quality(self.quality, "quality")


@dataclass
class GrantedAbility(Ability):
    """Class that holds the data of an ability granted by an item.

    :param name: Granted ability name.
    :param enabled: Whether the granted ability is in active use.
    :param level: Granted ability level.
    :param quality: Granted abilities cannot have any quality on them.
    :param support: Granted abilities are never support gems."""

    name: str
    enabled: bool
    level: int
    quality: int | None = None
    support: bool = False


@dataclass
class SkillGroup:
    """Class that holds a (linked) socket group.

    :param enabled: Whether the socket group is in active use.
    :param label: Socket group label assigned in Path Of Building.
    :param active: Main skill in socket group, if given.
    :param abilities: List of :class:`Gem <Gem>` or
        :class:`GrantedAbility <GrantedAbility>` objects in socket group."""

    enabled: bool
    label: str
    active: int | None
    abilities: list[Gem | GrantedAbility]


@dataclass
class Tree:
    """Class that holds a passive skill tree.

    :param url: pathofexile.com link to passive skill tree.
    :param nodes: List of passive skill tree nodes by ID.
    :param sockets: Dictionary of
        {<passive skill tree jewel socket location> : <jewel set ID>}."""

    url: str
    nodes: list[int]
    sockets: dict[int, int]


@dataclass
class Keystones:
    """Keystones(*args)
    Class that holds keystone data.

    :param acrobatics: Whether the player has Acrobatics.
    :param ancestral_bond: Whether the player has Ancestral Bond.
    :param arrow_dancing: Whether the player has Arrow Dancing.
    :param avatar_of_fire: Whether the player has Avatar of Fire.
    :param blood_magic: Whether the player has Blood Magic.
    :param chaos_inoculation: Whether the player has Chaos Inoculation.
    :param conduit: Whether the player has Conduit.
    :param crimson_dance: Whether the player has Crimson Dance.
    :param eldritch_battery: Whether the player has Eldritch Battery.
    :param elemental_equilibrium: Whether the player has Elemental Equilibrium.
    :param ghost_reaver: Whether the player has Ghost Reaver.
    :param iron_grip: Whether the player has Iron Grip.
    :param iron_reflexes: Whether the player has Iron Reflexes.
    :param mind_over_matter: Whether the player has Mind Over Matter.
    :param minion_instability: Whether the player has Minion Instability.
    :param mortal_conviction: Whether the player has Mortal Conviction.
    :param necromantic_aegis: Whether the player has Necromantic  Aegis.
    :param pain_attunement: Whether the player has Pain Attunement.
    :param perfect_agony: Whether the player has Perfect Agony.
    :param phase_acrobatics: Whether the player has Phase Acrobatics.
    :param point_blank: Whether the player has Point Blank.
    :param resolute_technique: Whether the player has Resolute Technique.
    :param runebinder: Whether the player has Runebinder.
    :param unwavering_stance: Whether the player has Unwavering Stance.
    :param vaal_pact: Whether the player has Vaal Pact.
    :param wicked_ward: Whether the player has Wicked Ward.
    :param zealots_oath: Whether the player has Zealots Oath."""

    acrobatics: bool
    ancestral_bond: bool
    arrow_dancing: bool
    avatar_of_fire: bool
    blood_magic: bool
    chaos_inoculation: bool
    conduit: bool
    crimson_dance: bool
    eldritch_battery: bool
    elemental_equilibrium: bool
    ghost_reaver: bool
    iron_grip: bool
    iron_reflexes: bool
    mind_over_matter: bool
    minion_instability: bool
    mortal_conviction: bool
    necromantic_aegis: bool
    pain_attunement: bool
    perfect_agony: bool
    phase_acrobatics: bool
    point_blank: bool
    resolute_technique: bool
    runebinder: bool
    unwavering_stance: bool
    vaal_pact: bool
    wicked_ward: bool
    zealots_oath: bool

    def __iter__(self):
        for k, v in asdict(self).items():
            if v:
                yield k


SocketGroup = tuple[str]
GroupOfSocketGroups = tuple[SocketGroup]


@dataclass
class Item:
    """Class that holds an item.

    :param rarity: Item rarity.
    :param name: Item name.
    :param base: Item base type.
    :param uid: Unique item ID for items in-game.

    .. note:: Items created in Path of Building do not have an UID.

    :param shaper: Whether the item is a Shaper base type.
    :param elder: Whether the item is an Elder base type.
    :param crafted: Whether the item has a crafted mod.
    :param quality: Item quality, if the item can have quality.
    :param sockets: Item socket groups, if the item can have sockets.

    .. note:: Example: The format used for a 5 socket chest armour with 2 socket groups
        of 3 linked blue sockets and 2 linked red sockets would be ((B, B, B), (R, R)).

    :param level_req: Required character level to equip the item.
    :param item_level: Item level.
    :param implicit: Number of item implicits, if the item can have implicits.
    :param text: Item text.

    .. note:: For items existing in-game, their item text is just copied.
        For items created with Path Of Building,
        their affix values are calculated to match in-game items in appearance."""

    rarity: str
    name: str
    base: str
    uid: str
    shaper: bool
    elder: bool
    crafted: bool
    quality: int | None
    sockets: GroupOfSocketGroups | None
    level_req: int
    item_level: int
    implicit: int | None
    text: str

    def __post_init__(self):
        """Validate item data after initialization."""
        from pobapi.model_validators import (
            ModelValidator,
            validate_item_level_req,
            validate_rarity,
        )

        validate_rarity(self.rarity, "rarity")
        ModelValidator.validate_not_empty(self.name, "name")
        ModelValidator.validate_not_empty(self.base, "base")
        validate_item_level_req(self.level_req, "level_req")
        ModelValidator.validate_positive(self.item_level, "item_level")
        if self.quality is not None:
            ModelValidator.validate_range(
                self.quality, min_value=0, max_value=30, field_name="quality"
            )

    def __str__(self):
        text = ""
        text += f"Rarity: {self.rarity}\n"
        text += f"Name: {self.name}\n"
        text += f"Base: {self.base}\n"
        if self.shaper:
            text += "Shaper Item\n"
        if self.elder:
            text += "Elder Item\n"
        if self.crafted:
            text += "Crafted Item\n"
        if self.quality:
            text += f"Quality: {self.quality}\n"
        if self.sockets:
            text += f"Sockets: {self.sockets}\n"
        text += f"LevelReq: {self.level_req}\n"
        text += f"ItemLvl: {self.item_level}\n"
        if self.implicit:
            text += f"Implicits: {self.implicit}\n"
        text += f"{self.text}"
        return text


@dataclass
class Set:
    """Set(*args)
    Class that holds an item set.

    :param weapon1: Primary weapon.
    :param weapon1_as1: Primary weapon abyssal socket 1.
    :param weapon1_as2: Primary weapon abyssal socket 1.
    :param weapon1_swap: Second primary weapon.
    :param weapon1_swap_as1: Second primary weapon abyssal socket 1.
    :param weapon1_swap_as2: Second primary weapon abyssal socket 2.
    :param weapon2: Secondary weapon.
    :param weapon2_as1: Secondary weapon abyssal socket 1.
    :param weapon2_as2: Secondary weapon abyssal socket 1.
    :param weapon2_swap: Second secondary weapon.
    :param weapon2_swap_as1: Second secondary weapon abyssal socket 1.
    :param weapon2_swap_as2: Second secondary weapon abyssal socket 2.
    :param helmet: Helmet.
    :param helmet_as1: Helmet abyssal socket 1.
    :param helmet_as2: Helmet abyssal socket 2.
    :param body_armour: Body armour.
    :param body_armour_as1: Body armour abyssal socket 1.
    :param body_armour_as2: Body armour abyssal socket 2.
    :param gloves: Gloves.
    :param gloves_as1: Gloves abyssal socket 1.
    :param gloves_as2: Gloves abyssal socket 2.
    :param boots: Boots.
    :param boots_as1: Boots abyssal socket 1.
    :param boots_as2: Boots abyssal socket 2.
    :param amulet: Amulet.
    :param ring1: Left ring.
    :param ring2: Right ring.
    :param belt: Belt.
    :param belt_as1: Belt abyssal socket 1.
    :param belt_as2: Belt abyssal socket 2.
    :param flask1: Flask bound to '1' by default.
    :param flask2: Flask bound to '2' by default.
    :param flask3: Flask bound to '3' by default.
    :param flask4: Flask bound to '4' by default.
    :param flask5: Flask bound to '5' by default."""

    weapon1: int | None
    weapon1_as1: int | None
    weapon1_as2: int | None
    weapon1_swap: int | None
    weapon1_swap_as1: int | None
    weapon1_swap_as2: int | None
    weapon2: int | None
    weapon2_as1: int | None
    weapon2_as2: int | None
    weapon2_swap: int | None
    weapon2_swap_as1: int | None
    weapon2_swap_as2: int | None
    helmet: int | None
    helmet_as1: int | None
    helmet_as2: int | None
    body_armour: int | None
    body_armour_as1: int | None
    body_armour_as2: int | None
    gloves: int | None
    gloves_as1: int | None
    gloves_as2: int | None
    boots: int | None
    boots_as1: int | None
    boots_as2: int | None
    amulet: int | None
    ring1: int | None
    ring2: int | None
    belt: int | None
    belt_as1: int | None
    belt_as2: int | None
    flask1: int | None
    flask2: int | None
    flask3: int | None
    flask4: int | None
    flask5: int | None

"""Party play calculation system for Path of Building.

This module handles party play mechanics including:
- Aura sharing (auras from party members)
- Buff sharing (buffs from party members)
- Support builds (support gem effects from party members)
"""

from dataclasses import dataclass
from typing import Any

from pobapi.calculator.modifiers import Modifier, ModifierSystem, ModifierType

__all__ = ["PartyMember", "PartyCalculator"]


@dataclass
class PartyMember:
    """Represents a party member.

    :param name: Party member name (optional).
    :param auras: List of auras active on this party member.
    :param buffs: List of buffs active on this party member.
    :param support_gems: List of support gems this party member provides.
    :param aura_effectiveness: Aura effectiveness multiplier (default 100%).
    """

    name: str = "Party Member"
    auras: list[str] | None = None
    buffs: list[str] | None = None
    support_gems: list[str] | None = None
    aura_effectiveness: float = 100.0

    def __post_init__(self):
        """Initialize default values."""
        if self.auras is None:
            self.auras = []
        if self.buffs is None:
            self.buffs = []
        if self.support_gems is None:
            self.support_gems = []


class PartyCalculator:
    """Calculator for party play mechanics.

    This class handles sharing of auras, buffs, and support effects
    from party members, replicating Path of Building's party system.
    """

    # Aura definitions with their effects
    # These match Path of Building's aura system
    AURA_EFFECTS: dict[str, list[Modifier]] = {
        "Hatred": [
            Modifier(
                stat="ColdDamage",
                value=36.0,
                mod_type=ModifierType.MORE,
                source="party:hatred",
            ),
            Modifier(
                stat="PhysicalAsExtraCold",
                value=15.0,
                mod_type=ModifierType.FLAT,
                source="party:hatred",
            ),
        ],
        "Anger": [
            Modifier(
                stat="FireDamage",
                value=36.0,
                mod_type=ModifierType.MORE,
                source="party:anger",
            ),
            Modifier(
                stat="PhysicalAsExtraFire",
                value=15.0,
                mod_type=ModifierType.FLAT,
                source="party:anger",
            ),
        ],
        "Wrath": [
            Modifier(
                stat="LightningDamage",
                value=36.0,
                mod_type=ModifierType.MORE,
                source="party:wrath",
            ),
            Modifier(
                stat="PhysicalAsExtraLightning",
                value=15.0,
                mod_type=ModifierType.FLAT,
                source="party:wrath",
            ),
        ],
        "Haste": [
            Modifier(
                stat="AttackSpeed",
                value=21.0,
                mod_type=ModifierType.INCREASED,
                source="party:haste",
            ),
            Modifier(
                stat="CastSpeed",
                value=21.0,
                mod_type=ModifierType.INCREASED,
                source="party:haste",
            ),
            Modifier(
                stat="MovementSpeed",
                value=21.0,
                mod_type=ModifierType.INCREASED,
                source="party:haste",
            ),
        ],
        "Grace": [
            Modifier(
                stat="Evasion",
                value=3000.0,
                mod_type=ModifierType.FLAT,
                source="party:grace",
            ),
        ],
        "Determination": [
            Modifier(
                stat="Armour",
                value=3000.0,
                mod_type=ModifierType.FLAT,
                source="party:determination",
            ),
        ],
        "Discipline": [
            Modifier(
                stat="EnergyShield",
                value=200.0,
                mod_type=ModifierType.FLAT,
                source="party:discipline",
            ),
        ],
        "Purity of Fire": [
            Modifier(
                stat="FireResistance",
                value=22.0,
                mod_type=ModifierType.FLAT,
                source="party:purity_of_fire",
            ),
        ],
        "Purity of Cold": [
            Modifier(
                stat="ColdResistance",
                value=22.0,
                mod_type=ModifierType.FLAT,
                source="party:purity_of_cold",
            ),
        ],
        "Purity of Lightning": [
            Modifier(
                stat="LightningResistance",
                value=22.0,
                mod_type=ModifierType.FLAT,
                source="party:purity_of_lightning",
            ),
        ],
        "Purity of Elements": [
            Modifier(
                stat="FireResistance",
                value=22.0,
                mod_type=ModifierType.FLAT,
                source="party:purity_of_elements",
            ),
            Modifier(
                stat="ColdResistance",
                value=22.0,
                mod_type=ModifierType.FLAT,
                source="party:purity_of_elements",
            ),
            Modifier(
                stat="LightningResistance",
                value=22.0,
                mod_type=ModifierType.FLAT,
                source="party:purity_of_elements",
            ),
        ],
        "Vitality": [
            Modifier(
                stat="LifeRegen",
                value=2.0,
                mod_type=ModifierType.FLAT,
                source="party:vitality",
            ),
        ],
        "Clarity": [
            Modifier(
                stat="ManaRegen",
                value=2.0,
                mod_type=ModifierType.FLAT,
                source="party:clarity",
            ),
        ],
        "Precision": [
            Modifier(
                stat="Accuracy",
                value=500.0,
                mod_type=ModifierType.FLAT,
                source="party:precision",
            ),
            Modifier(
                stat="CritChance",
                value=50.0,
                mod_type=ModifierType.INCREASED,
                source="party:precision",
            ),
        ],
        "Pride": [
            Modifier(
                stat="PhysicalDamage",
                value=39.0,
                mod_type=ModifierType.MORE,
                source="party:pride",
            ),
        ],
        "Flesh and Stone": [
            Modifier(
                stat="PhysicalDamageReduction",
                value=10.0,
                mod_type=ModifierType.FLAT,
                source="party:flesh_and_stone",
            ),
        ],
        "Malevolence": [
            Modifier(
                stat="DamageOverTime",
                value=39.0,
                mod_type=ModifierType.MORE,
                source="party:malevolence",
            ),
        ],
        "Zealotry": [
            Modifier(
                stat="SpellDamage",
                value=39.0,
                mod_type=ModifierType.MORE,
                source="party:zealotry",
            ),
            Modifier(
                stat="CritChance",
                value=1.5,
                mod_type=ModifierType.FLAT,
                source="party:zealotry",
            ),
        ],
    }

    # Buff definitions
    BUFF_EFFECTS: dict[str, list[Modifier]] = {
        "Onslaught": [
            Modifier(
                stat="AttackSpeed",
                value=20.0,
                mod_type=ModifierType.INCREASED,
                source="party:onslaught",
            ),
            Modifier(
                stat="CastSpeed",
                value=20.0,
                mod_type=ModifierType.INCREASED,
                source="party:onslaught",
            ),
            Modifier(
                stat="MovementSpeed",
                value=20.0,
                mod_type=ModifierType.INCREASED,
                source="party:onslaught",
            ),
        ],
        "Fortify": [
            Modifier(
                stat="DamageTaken",
                value=-20.0,
                mod_type=ModifierType.INCREASED,
                source="party:fortify",
            ),
        ],
        "Tailwind": [
            Modifier(
                stat="ActionSpeed",
                value=10.0,
                mod_type=ModifierType.INCREASED,
                source="party:tailwind",
            ),
        ],
        "Adrenaline": [
            Modifier(
                stat="Damage",
                value=100.0,
                mod_type=ModifierType.INCREASED,
                source="party:adrenaline",
            ),
            Modifier(
                stat="AttackSpeed",
                value=25.0,
                mod_type=ModifierType.INCREASED,
                source="party:adrenaline",
            ),
            Modifier(
                stat="CastSpeed",
                value=25.0,
                mod_type=ModifierType.INCREASED,
                source="party:adrenaline",
            ),
            Modifier(
                stat="MovementSpeed",
                value=25.0,
                mod_type=ModifierType.INCREASED,
                source="party:adrenaline",
            ),
        ],
    }

    def __init__(self, modifier_system: ModifierSystem):
        """Initialize party calculator.

        :param modifier_system: The ModifierSystem instance to use for calculations.
        """
        self.modifiers = modifier_system

    def add_party_member_auras(
        self, party_member: PartyMember, aura_effectiveness: float = 100.0
    ) -> list[Modifier]:
        """Add modifiers from party member auras.

        In Path of Exile, auras from party members are shared
        with reduced effectiveness.
        Default aura effectiveness from party members is typically 50%
        (can be modified).

        :param party_member: Party member with active auras.
        :param aura_effectiveness: Aura effectiveness multiplier (default 100%).
        :return: List of Modifier objects from party member auras.
        """
        modifiers: list[Modifier] = []

        # Default party aura effectiveness is 50% (can be modified by passives/items)
        # But we use the provided parameter for flexibility
        party_aura_effectiveness = aura_effectiveness / 100.0

        if party_member.auras is None:
            return []
        for aura_name in party_member.auras:
            aura_name_normalized = aura_name.strip()
            if aura_name_normalized in PartyCalculator.AURA_EFFECTS:
                aura_modifiers = PartyCalculator.AURA_EFFECTS[aura_name_normalized]
                for mod in aura_modifiers:
                    # Apply party aura effectiveness
                    # For MORE modifiers, effectiveness affects the value
                    # For FLAT/INCREASED modifiers, effectiveness affects the value
                    effective_value = mod.value * party_aura_effectiveness

                    modifiers.append(
                        Modifier(
                            stat=mod.stat,
                            value=effective_value,
                            mod_type=mod.mod_type,
                            source=f"party:{party_member.name}:{aura_name_normalized.lower()}",
                        )
                    )

        return modifiers

    def add_party_member_buffs(self, party_member: PartyMember) -> list[Modifier]:
        """Add modifiers from party member buffs.

        Buffs from party members are typically shared at full effectiveness.

        :param party_member: Party member with active buffs.
        :return: List of Modifier objects from party member buffs.
        """
        modifiers: list[Modifier] = []

        if party_member.buffs is None:
            return []
        for buff_name in party_member.buffs:
            buff_name_normalized = buff_name.strip()
            if buff_name_normalized in PartyCalculator.BUFF_EFFECTS:
                buff_modifiers = PartyCalculator.BUFF_EFFECTS[buff_name_normalized]
                for mod in buff_modifiers:
                    modifiers.append(
                        Modifier(
                            stat=mod.stat,
                            value=mod.value,
                            mod_type=mod.mod_type,
                            source=f"party:{party_member.name}:{buff_name_normalized.lower()}",
                        )
                    )

        return modifiers

    def add_party_member_support_effects(
        self, party_member: PartyMember, supported_skill: str | None = None
    ) -> list[Modifier]:
        """Add modifiers from party member support gems.

        Support builds can provide support gem effects to other party members.
        This is a simplified implementation - full version would parse support gem data.

        :param party_member: Party member providing support gems.
        :param supported_skill: Name of the skill being supported (optional).
        :return: List of Modifier objects from party member support gems.
        """
        modifiers: list[Modifier] = []

        # Import here to avoid circular dependency
        from pobapi.calculator.skill_modifier_parser import SkillModifierParser

        if party_member.support_gems is None:
            return []
        for support_gem_name in party_member.support_gems:
            # Parse support gem effects
            # In a full implementation, this would use actual support gem data
            support_modifiers = SkillModifierParser.parse_support_gem(
                support_gem_name, gem_level=20, supported_skill=supported_skill
            )

            # Mark these as coming from party member
            for mod in support_modifiers:
                modifiers.append(
                    Modifier(
                        stat=mod.stat,
                        value=mod.value,
                        mod_type=mod.mod_type,
                        source=f"party:{party_member.name}:support:{support_gem_name.lower()}",
                    )
                )

        return modifiers

    def process_party(
        self,
        party_members: list[PartyMember],
        aura_effectiveness: float = 50.0,
        supported_skill: str | None = None,
    ) -> list[Modifier]:
        """Process all party members and collect their shared effects.

        This is the main method for party play calculations.
        It collects all auras, buffs, and support effects from party members.

        :param party_members: List of party members.
        :param aura_effectiveness: Aura effectiveness from party members (default 50%).
        :param supported_skill: Name of skill being supported (optional).
        :return: List of all Modifier objects from party members.
        """
        all_modifiers: list[Modifier] = []

        for party_member in party_members:
            # Add auras
            aura_modifiers = self.add_party_member_auras(
                party_member, aura_effectiveness
            )
            all_modifiers.extend(aura_modifiers)

            # Add buffs
            buff_modifiers = self.add_party_member_buffs(party_member)
            all_modifiers.extend(buff_modifiers)

            # Add support effects
            support_modifiers = self.add_party_member_support_effects(
                party_member, supported_skill
            )
            all_modifiers.extend(support_modifiers)

        return all_modifiers

    def calculate_party_aura_effectiveness(
        self, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate party aura effectiveness.

        Party aura effectiveness can be modified by passives/items.
        Base effectiveness is 50% (auras from party members).

        :param context: Calculation context.
        :return: Party aura effectiveness percentage.
        """
        if context is None:
            context = {}

        # Base party aura effectiveness is 50%
        # In Path of Exile, auras from party members have 50% effectiveness by default
        base_effectiveness = 50.0

        # Get modifiers to party aura effectiveness
        # This would come from passives/items that increase
        # party aura effectiveness
        # Examples: "X% increased Effect of Auras on you" or
        # "X% increased Effect of Non-Curse Auras"
        try:
            # Use base_value=100.0 to get the percentage increase
            # Then subtract 100 to get the actual increase percentage
            calculated_value = self.modifiers.calculate_stat(
                "PartyAuraEffectiveness", 100.0, context
            )
            party_aura_effectiveness_increased = calculated_value - 100.0
        except (AttributeError, KeyError):
            # If modifier system doesn't have this stat yet, use 0
            party_aura_effectiveness_increased = 0.0

        # Calculate final effectiveness
        final_effectiveness = base_effectiveness * (
            1.0 + party_aura_effectiveness_increased / 100.0
        )

        # Note: Effectiveness can exceed 100% per PoE mechanics
        # (e.g., with high "increased Effect of Auras" modifiers)
        return final_effectiveness

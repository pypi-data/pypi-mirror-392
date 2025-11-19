"""Parser for unique item effects.

This module handles parsing and applying effects from unique items,
which often have special mechanics that go beyond simple modifiers.
"""

from pobapi.calculator.modifiers import Modifier, ModifierType
from pobapi.calculator.unique_items_extended import EXTENDED_UNIQUE_EFFECTS

__all__ = ["UniqueItemParser"]


class UniqueItemParser:
    """Parser for unique item effects.

    Unique items in Path of Exile often have special effects that
    require custom handling beyond simple modifier parsing.
    """

    # Mapping of unique item names to their special effects
    # This is a simplified implementation - full version would load from game data
    UNIQUE_EFFECTS: dict[str, list[Modifier]] = {
        # Example unique items with their effects
        "Headhunter": [
            # Headhunter steals mods from rare monsters
            # This would require special handling in the calculation engine
            Modifier(
                stat="HeadhunterEffect",
                value=1.0,
                mod_type=ModifierType.FLAG,
                source="unique:Headhunter",
            ),
        ],
        "Shavronne's Wrappings": [
            # Chaos damage does not bypass Energy Shield
            Modifier(
                stat="ChaosDamageBypassES",
                value=0.0,
                mod_type=ModifierType.FLAG,
                source="unique:ShavronnesWrappings",
            ),
        ],
        "The Blood Thorn": [
            # 100% of Physical Damage Converted to Chaos Damage
            Modifier(
                stat="PhysicalToChaos",
                value=100.0,
                mod_type=ModifierType.FLAT,
                source="unique:TheBloodThorn",
            ),
        ],
        "Atziri's Acuity": [
            # Life Leech applies to Energy Shield instead
            Modifier(
                stat="LifeLeechToEnergyShield",
                value=1.0,
                mod_type=ModifierType.FLAG,
                source="unique:AtzirisAcuity",
            ),
        ],
        "Void Battery": [
            # +1 to Maximum Power Charges per 3% Quality
            # +15-20% increased Spell Damage per Power Charge
            Modifier(
                stat="PowerCharges",
                value=1.0,
                mod_type=ModifierType.FLAT,
                source="unique:VoidBattery",
            ),
            Modifier(
                stat="SpellDamagePerPowerCharge",
                value=15.0,
                mod_type=ModifierType.INCREASED,
                source="unique:VoidBattery",
            ),
        ],
        "Crown of Eyes": [
            # Modifiers to Spell Damage apply to Attack Damage
            Modifier(
                stat="SpellDamageAppliesToAttack",
                value=1.0,
                mod_type=ModifierType.FLAG,
                source="unique:CrownOfEyes",
            ),
        ],
        "The Retch": [
            # 100% of Life Leech is applied to Enemies as Chaos Damage per second
            Modifier(
                stat="LifeLeechAsChaosDamage",
                value=100.0,
                mod_type=ModifierType.FLAT,
                source="unique:TheRetch",
            ),
        ],
        "Starforge": [
            # 400-500% increased Physical Damage
            # Your Physical Damage can Shock
            Modifier(
                stat="PhysicalDamage",
                value=450.0,
                mod_type=ModifierType.INCREASED,
                source="unique:Starforge",
            ),
            Modifier(
                stat="PhysicalDamageCanShock",
                value=1.0,
                mod_type=ModifierType.FLAG,
                source="unique:Starforge",
            ),
        ],
        "Voidforge": [
            # 300% of Physical Damage Converted to a random Element
            Modifier(
                stat="PhysicalToRandomElement",
                value=300.0,
                mod_type=ModifierType.FLAT,
                source="unique:Voidforge",
            ),
        ],
        "Doryani's Fist": [
            # Unarmed attacks deal 1000% of Base Main Hand Damage
            Modifier(
                stat="UnarmedDamage",
                value=1000.0,
                mod_type=ModifierType.INCREASED,
                source="unique:DoryanisFist",
            ),
        ],
        "Mageblood": [
            # All Flask Effects are applied during Flask Effect
            # 25-35% increased Effect of Flasks on you
            Modifier(
                stat="FlaskEffect",
                value=30.0,
                mod_type=ModifierType.INCREASED,
                source="unique:Mageblood",
            ),
            Modifier(
                stat="FlaskEffectAlwaysActive",
                value=1.0,
                mod_type=ModifierType.FLAG,
                source="unique:Mageblood",
            ),
        ],
        "Aegis Aurora": [
            # +2-5% Chance to Block Spell Damage per 5% Chance to Block Attack Damage
            # Recover Energy Shield equal to 2% of Armour when you Block
            Modifier(
                stat="SpellBlockChancePerAttackBlock",
                value=3.5,
                mod_type=ModifierType.FLAT,
                source="unique:AegisAurora",
            ),
            Modifier(
                stat="EnergyShieldOnBlock",
                value=2.0,
                mod_type=ModifierType.FLAT,
                source="unique:AegisAurora",
            ),
        ],
        "The Squire": [
            # Socketed Gems are Supported by Level 30 Cast on Critical Strike
            # Socketed Gems are Supported by Level 30 Cast when Damage Taken
            # Socketed Gems are Supported by Level 30 Spell Echo
            Modifier(
                stat="SocketedGemsSupportedByCastOnCrit",
                value=30.0,
                mod_type=ModifierType.FLAT,
                source="unique:TheSquire",
            ),
        ],
        "Ashes of the Stars": [
            # +10-20% to all Elemental Resistances
            # +20-30% to Quality of Socketed Gems
            Modifier(
                stat="FireResistance",
                value=15.0,
                mod_type=ModifierType.FLAT,
                source="unique:AshesOfTheStars",
            ),
            Modifier(
                stat="ColdResistance",
                value=15.0,
                mod_type=ModifierType.FLAT,
                source="unique:AshesOfTheStars",
            ),
            Modifier(
                stat="LightningResistance",
                value=15.0,
                mod_type=ModifierType.FLAT,
                source="unique:AshesOfTheStars",
            ),
            Modifier(
                stat="SocketedGemsQuality",
                value=25.0,
                mod_type=ModifierType.FLAT,
                source="unique:AshesOfTheStars",
            ),
        ],
        "Watcher's Eye": [
            # (Various mods based on auras - would need special handling)
            Modifier(
                stat="WatchersEyeEffect",
                value=1.0,
                mod_type=ModifierType.FLAG,
                source="unique:WatchersEye",
            ),
        ],
        "Bottled Faith": [
            # 15-20% increased Damage during Flask Effect
            # Consecrated Ground created during Flask Effect has 50% increased Effect
            Modifier(
                stat="Damage",
                value=17.5,
                mod_type=ModifierType.INCREASED,
                source="unique:BottledFaith",
                conditions={"flask_effect": True},
            ),
            Modifier(
                stat="ConsecratedGroundEffect",
                value=50.0,
                mod_type=ModifierType.INCREASED,
                source="unique:BottledFaith",
                conditions={"flask_effect": True},
            ),
        ],
        "Forbidden Shako": [
            # Socketed Gems are Supported by Level 1-35 (random) Support Gems
            # (Would need special handling for random support gems)
            Modifier(
                stat="SocketedGemsSupportedByRandom",
                value=1.0,
                mod_type=ModifierType.FLAG,
                source="unique:ForbiddenShako",
            ),
        ],
        "The Immortal Will": [
            # 20-30% increased Maximum Life
            # 10-15% increased Maximum Mana
            # 10-15% increased Maximum Energy Shield
            Modifier(
                stat="Life",
                value=25.0,
                mod_type=ModifierType.INCREASED,
                source="unique:TheImmortalWill",
            ),
            Modifier(
                stat="Mana",
                value=12.5,
                mod_type=ModifierType.INCREASED,
                source="unique:TheImmortalWill",
            ),
            Modifier(
                stat="EnergyShield",
                value=12.5,
                mod_type=ModifierType.INCREASED,
                source="unique:TheImmortalWill",
            ),
        ],
        "The Adorned": [
            # 150-200% increased Effect of Socketed Jewels
            Modifier(
                stat="SocketedJewelEffect",
                value=175.0,
                mod_type=ModifierType.INCREASED,
                source="unique:TheAdorned",
            ),
        ],
        "Original Sin": [
            # All Damage from Hits with This Weapon is Chaos Damage
            # 30-50% increased Chaos Damage
            Modifier(
                stat="AllDamageIsChaos",
                value=1.0,
                mod_type=ModifierType.FLAG,
                source="unique:OriginalSin",
            ),
            Modifier(
                stat="ChaosDamage",
                value=40.0,
                mod_type=ModifierType.INCREASED,
                source="unique:OriginalSin",
            ),
        ],
        "Replica Headhunter": [
            # Steals mods from unique monsters (similar to Headhunter)
            Modifier(
                stat="HeadhunterEffect",
                value=1.0,
                mod_type=ModifierType.FLAG,
                source="unique:ReplicaHeadhunter",
            ),
        ],
        "The Eternity Shroud": [
            # 1% increased Elemental Damage per Shaper item you have equipped
            # 10% of Non-Chaos Damage as Extra Chaos Damage per Shaper item
            Modifier(
                stat="ElementalDamagePerShaperItem",
                value=1.0,
                mod_type=ModifierType.INCREASED,
                source="unique:TheEternityShroud",
            ),
            Modifier(
                stat="NonChaosAsExtraChaosPerShaperItem",
                value=10.0,
                mod_type=ModifierType.FLAT,
                source="unique:TheEternityShroud",
            ),
        ],
        "The Ivory Tower": [
            # 10% of Maximum Mana is Converted to Maximum Energy Shield
            # Chaos Damage does not bypass Energy Shield
            Modifier(
                stat="ManaToEnergyShield",
                value=10.0,
                mod_type=ModifierType.FLAT,
                source="unique:TheIvoryTower",
            ),
            Modifier(
                stat="ChaosDamageBypassES",
                value=0.0,
                mod_type=ModifierType.FLAG,
                source="unique:TheIvoryTower",
            ),
        ],
        "The Covenant": [
            # Socketed Gems are Supported by Level 29 Added Chaos Damage
            # Socketed Gems have 30% increased Mana Cost
            Modifier(
                stat="SocketedGemsSupportedByAddedChaosDamage",
                value=29.0,
                mod_type=ModifierType.FLAT,
                source="unique:TheCovenant",
            ),
            Modifier(
                stat="SocketedGemsManaCost",
                value=30.0,
                mod_type=ModifierType.INCREASED,
                source="unique:TheCovenant",
            ),
        ],
        "Atziri's Reflection": [
            # +20-30% to all Elemental Resistances
            # Reflects Curses back to their Caster
            Modifier(
                stat="FireResistance",
                value=25.0,
                mod_type=ModifierType.FLAT,
                source="unique:AtzirisReflection",
            ),
            Modifier(
                stat="ColdResistance",
                value=25.0,
                mod_type=ModifierType.FLAT,
                source="unique:AtzirisReflection",
            ),
            Modifier(
                stat="LightningResistance",
                value=25.0,
                mod_type=ModifierType.FLAT,
                source="unique:AtzirisReflection",
            ),
            Modifier(
                stat="ReflectCurses",
                value=1.0,
                mod_type=ModifierType.FLAG,
                source="unique:AtzirisReflection",
            ),
        ],
        "The Taming": [
            # 20-30% increased Elemental Damage
            # 10-15% increased Attack and Cast Speed
            Modifier(
                stat="ElementalDamage",
                value=25.0,
                mod_type=ModifierType.INCREASED,
                source="unique:TheTaming",
            ),
            Modifier(
                stat="AttackSpeed",
                value=12.5,
                mod_type=ModifierType.INCREASED,
                source="unique:TheTaming",
            ),
            Modifier(
                stat="CastSpeed",
                value=12.5,
                mod_type=ModifierType.INCREASED,
                source="unique:TheTaming",
            ),
        ],
        "The Three Dragons": [
            # Your Fire Damage can Freeze but cannot Ignite
            # Your Cold Damage can Ignite but cannot Freeze
            # Your Lightning Damage can Freeze but cannot Shock
            Modifier(
                stat="FireDamageCanFreeze",
                value=1.0,
                mod_type=ModifierType.FLAG,
                source="unique:TheThreeDragons",
            ),
            Modifier(
                stat="ColdDamageCanIgnite",
                value=1.0,
                mod_type=ModifierType.FLAG,
                source="unique:TheThreeDragons",
            ),
            Modifier(
                stat="LightningDamageCanFreeze",
                value=1.0,
                mod_type=ModifierType.FLAG,
                source="unique:TheThreeDragons",
            ),
        ],
        "The Perfect Form": [
            # +15-25% to all Elemental Resistances
            # 30-40% increased Evasion Rating
            Modifier(
                stat="FireResistance",
                value=20.0,
                mod_type=ModifierType.FLAT,
                source="unique:ThePerfectForm",
            ),
            Modifier(
                stat="ColdResistance",
                value=20.0,
                mod_type=ModifierType.FLAT,
                source="unique:ThePerfectForm",
            ),
            Modifier(
                stat="LightningResistance",
                value=20.0,
                mod_type=ModifierType.FLAT,
                source="unique:ThePerfectForm",
            ),
            Modifier(
                stat="Evasion",
                value=35.0,
                mod_type=ModifierType.INCREASED,
                source="unique:ThePerfectForm",
            ),
        ],
        "The Brass Dome": [
            # +5% to maximum Elemental Resistances
            # 15-20% increased Armour
            Modifier(
                stat="MaxFireResistance",
                value=5.0,
                mod_type=ModifierType.FLAT,
                source="unique:TheBrassDome",
            ),
            Modifier(
                stat="MaxColdResistance",
                value=5.0,
                mod_type=ModifierType.FLAT,
                source="unique:TheBrassDome",
            ),
            Modifier(
                stat="MaxLightningResistance",
                value=5.0,
                mod_type=ModifierType.FLAT,
                source="unique:TheBrassDome",
            ),
            Modifier(
                stat="Armour",
                value=17.5,
                mod_type=ModifierType.INCREASED,
                source="unique:TheBrassDome",
            ),
        ],
    }

    # Merge extended unique effects
    UNIQUE_EFFECTS.update(EXTENDED_UNIQUE_EFFECTS)

    @staticmethod
    def parse_unique_item(
        item_name: str, item_text: str, skip_regular_parsing: bool = False
    ) -> list[Modifier]:
        """Parse a unique item and extract its special effects.

        :param item_name: Name of the unique item.
        :param item_text: Full text of the unique item.
        :param skip_regular_parsing: If True, skip parsing regular modifiers
            from item text to avoid recursion (they should be parsed by caller).
        :return: List of Modifier objects from the unique item.
        """
        modifiers: list[Modifier] = []

        # Check if this unique has special effects in hardcoded database
        item_name_normalized = item_name.lower().replace("'", "").replace(" ", "")
        for unique_name, unique_mods in UniqueItemParser.UNIQUE_EFFECTS.items():
            unique_name_normalized = (
                unique_name.lower().replace("'", "").replace(" ", "")
            )
            if item_name_normalized == unique_name_normalized:
                modifiers.extend(unique_mods)
                break

        # Try to load from GameDataLoader if available
        try:
            from pobapi.calculator.game_data import GameDataLoader

            # Use a singleton instance or create new one
            # For now, create a new instance (could be optimized with caching)
            loader = GameDataLoader()
            # Try to load unique items data (will use cached if already loaded)
            unique_item_data = loader.load_unique_item_data()
            if unique_item_data:
                unique_item = loader.get_unique_item(item_name)
                if unique_item:
                    # Parse explicit mods from unique item data
                    from pobapi.parsers.item_modifier import ItemModifierParser

                    if unique_item.explicit_mods:
                        for mod_text in unique_item.explicit_mods:
                            mods = ItemModifierParser.parse_line(
                                mod_text, source=f"unique:{item_name}:data"
                            )
                            modifiers.extend(mods)
        except (ImportError, AttributeError):
            # GameDataLoader not available or error loading data
            pass

        # Also parse regular modifiers from item text
        # (unique items still have regular modifiers)
        # But only if not skipping to avoid recursion
        if not skip_regular_parsing:
            from pobapi.parsers.item_modifier import ItemModifierParser

            # Parse lines directly to avoid recursion
            lines = item_text.split("\n")
            for line in lines:
                # Skip rarity and name lines
                if "Rarity:" in line or line.strip() == item_name:
                    continue
                line_mods = ItemModifierParser.parse_line(
                    line, source=f"unique:{item_name}"
                )
                modifiers.extend(line_mods)

        return modifiers

    @staticmethod
    def is_unique_item(item_text: str) -> bool:
        """Check if an item is a unique item.

        :param item_text: Item text to check.
        :return: True if item is unique.
        """
        # Unique items have "Rarity: UNIQUE" in their text
        return "Rarity: UNIQUE" in item_text.upper() or "Rarity: UNIQUE" in item_text

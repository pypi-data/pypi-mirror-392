"""Extended unique items database.

This module contains additional unique items to expand the database to 100+ items.
Items are organized by category for easier maintenance.
"""

from pobapi.calculator.modifiers import Modifier, ModifierType

__all__ = ["EXTENDED_UNIQUE_EFFECTS"]

# Extended unique items database (70+ additional items)
# Organized by category for easier maintenance

EXTENDED_UNIQUE_EFFECTS: dict[str, list[Modifier]] = {
    # === BELTS ===
    "Bisco's Collar": [
        Modifier(
            stat="ItemQuantity",
            value=50.0,
            mod_type=ModifierType.INCREASED,
            source="unique:BiscosCollar",
        ),
    ],
    "Bisco's Leash": [
        Modifier(
            stat="ItemRarity",
            value=50.0,
            mod_type=ModifierType.INCREASED,
            source="unique:BiscosLeash",
        ),
    ],
    "Perandus Blazon": [
        Modifier(
            stat="ItemQuantity",
            value=20.0,
            mod_type=ModifierType.INCREASED,
            source="unique:PerandusBlazon",
        ),
    ],
    "Soulthirst": [
        Modifier(
            stat="SoulEater",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:Soulthirst",
        ),
    ],
    "The Nomad": [
        Modifier(
            stat="Life",
            value=30.0,
            mod_type=ModifierType.INCREASED,
            source="unique:TheNomad",
        ),
        Modifier(
            stat="Mana",
            value=30.0,
            mod_type=ModifierType.INCREASED,
            source="unique:TheNomad",
        ),
    ],
    "Wurm's Molt": [
        Modifier(
            stat="LifeLeech",
            value=2.0,
            mod_type=ModifierType.FLAT,
            source="unique:WurmsMolt",
        ),
        Modifier(
            stat="ManaLeech",
            value=2.0,
            mod_type=ModifierType.FLAT,
            source="unique:WurmsMolt",
        ),
    ],
    # === BOOTS ===
    "Atziri's Step": [
        Modifier(
            stat="SpellDodgeChance",
            value=20.0,
            mod_type=ModifierType.FLAT,
            source="unique:AtzirisStep",
        ),
    ],
    "Goldwyrm": [
        Modifier(
            stat="ItemQuantity",
            value=20.0,
            mod_type=ModifierType.INCREASED,
            source="unique:Goldwyrm",
        ),
    ],
    "Kaom's Roots": [
        Modifier(
            stat="CannotBeSlowedBelowBaseSpeed",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:KaomsRoots",
        ),
        Modifier(
            stat="Life",
            value=100.0,
            mod_type=ModifierType.INCREASED,
            source="unique:KaomsRoots",
        ),
    ],
    "Seven-League Step": [
        Modifier(
            stat="MovementSpeed",
            value=50.0,
            mod_type=ModifierType.INCREASED,
            source="unique:SevenLeagueStep",
        ),
    ],
    "The Stampede": [
        Modifier(
            stat="MovementSpeed",
            value=30.0,
            mod_type=ModifierType.INCREASED,
            source="unique:TheStampede",
        ),
        Modifier(
            stat="CannotBeSlowedBelowBaseSpeed",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:TheStampede",
        ),
    ],
    # === GLOVES ===
    "Atziri's Acuity": [
        Modifier(
            stat="LifeLeechToEnergyShield",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:AtzirisAcuity",
        ),
    ],
    "Facebreaker": [
        Modifier(
            stat="UnarmedPhysicalDamage",
            value=600.0,
            mod_type=ModifierType.INCREASED,
            source="unique:Facebreaker",
        ),
    ],
    "Grip of the Council": [
        Modifier(
            stat="MinionDamage",
            value=30.0,
            mod_type=ModifierType.INCREASED,
            source="unique:GripOfTheCouncil",
        ),
    ],
    "Maligaro's Virtuosity": [
        Modifier(
            stat="CritChance",
            value=50.0,
            mod_type=ModifierType.INCREASED,
            source="unique:MaligarosVirtuosity",
        ),
        Modifier(
            stat="CritMultiplier",
            value=20.0,
            mod_type=ModifierType.INCREASED,
            source="unique:MaligarosVirtuosity",
        ),
    ],
    "Shadows and Dust": [
        Modifier(
            stat="FrenzyCharges",
            value=1.0,
            mod_type=ModifierType.FLAT,
            source="unique:ShadowsAndDust",
        ),
    ],
    "Southbound": [
        Modifier(
            stat="CannotKillEnemiesBelowLowLife",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:Southbound",
        ),
        Modifier(
            stat="ColdDamage",
            value=40.0,
            mod_type=ModifierType.INCREASED,
            source="unique:Southbound",
        ),
    ],
    # === HELMETS ===
    "Abyssus": [
        Modifier(
            stat="PhysicalDamage",
            value=40.0,
            mod_type=ModifierType.MORE,
            source="unique:Abyssus",
        ),
        Modifier(
            stat="PhysicalDamageTaken",
            value=40.0,
            mod_type=ModifierType.INCREASED,
            source="unique:Abyssus",
        ),
    ],
    "Alberon's Warpath": [
        Modifier(
            stat="StrengthToAddedChaosDamage",
            value=1.0,
            mod_type=ModifierType.FLAT,
            source="unique:AlberonsWarpath",
        ),
    ],
    "Crown of Thorns": [
        Modifier(
            stat="PhysicalDamageReflected",
            value=30.0,
            mod_type=ModifierType.FLAT,
            source="unique:CrownOfThorns",
        ),
    ],
    "Devoto's Devotion": [
        Modifier(
            stat="MovementSpeed",
            value=20.0,
            mod_type=ModifierType.INCREASED,
            source="unique:DevotosDevotion",
        ),
        Modifier(
            stat="AttackSpeed",
            value=16.0,
            mod_type=ModifierType.INCREASED,
            source="unique:DevotosDevotion",
        ),
    ],
    "Lightpoacher": [
        Modifier(
            stat="SpiritBurstOnKill",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:Lightpoacher",
        ),
    ],
    "The Baron": [
        Modifier(
            stat="MinionLife",
            value=2.0,
            mod_type=ModifierType.INCREASED,
            source="unique:TheBaron",
        ),
        Modifier(
            stat="StrengthToMinionLife",
            value=1.0,
            mod_type=ModifierType.FLAT,
            source="unique:TheBaron",
        ),
    ],
    "The Formless Inferno": [
        Modifier(
            stat="FireResistanceToArmour",
            value=1.0,
            mod_type=ModifierType.FLAT,
            source="unique:TheFormlessInferno",
        ),
    ],
    "The Gull": [
        Modifier(
            stat="ShrineEffect",
            value=100.0,
            mod_type=ModifierType.INCREASED,
            source="unique:TheGull",
        ),
    ],
    "The Vertex": [
        Modifier(
            stat="SpellDamage",
            value=30.0,
            mod_type=ModifierType.INCREASED,
            source="unique:TheVertex",
        ),
        Modifier(
            stat="ManaReservation",
            value=-15.0,
            mod_type=ModifierType.INCREASED,
            source="unique:TheVertex",
        ),
    ],
    # === RINGS ===
    "Andvarius": [
        Modifier(
            stat="ItemRarity",
            value=80.0,
            mod_type=ModifierType.INCREASED,
            source="unique:Andvarius",
        ),
        Modifier(
            stat="AllResistances",
            value=-20.0,
            mod_type=ModifierType.FLAT,
            source="unique:Andvarius",
        ),
    ],
    "Berek's Grip": [
        Modifier(
            stat="LightningDamageLeechedAsLife",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:BereksGrip",
        ),
    ],
    "Berek's Pass": [
        Modifier(
            stat="FireDamageLeechedAsLife",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:BereksPass",
        ),
    ],
    "Berek's Respite": [
        Modifier(
            stat="ColdDamageLeechedAsLife",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:BereksRespite",
        ),
    ],
    "Call of the Brotherhood": [
        Modifier(
            stat="LightningToCold",
            value=50.0,
            mod_type=ModifierType.FLAT,
            source="unique:CallOfTheBrotherhood",
        ),
    ],
    "Doedre's Damning": [
        Modifier(
            stat="CurseLimit",
            value=1.0,
            mod_type=ModifierType.FLAT,
            source="unique:DoedresDamning",
        ),
    ],
    "Emberwake": [
        Modifier(
            stat="IgniteDuration",
            value=-50.0,
            mod_type=ModifierType.INCREASED,
            source="unique:Emberwake",
        ),
        Modifier(
            stat="CanHaveMultipleIgnites",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:Emberwake",
        ),
    ],
    "Kaom's Sign": [
        Modifier(
            stat="EnduranceCharges",
            value=1.0,
            mod_type=ModifierType.FLAT,
            source="unique:KaomsSign",
        ),
    ],
    "Le Heup of All": [
        Modifier(
            stat="Damage",
            value=10.0,
            mod_type=ModifierType.INCREASED,
            source="unique:LeHeupOfAll",
        ),
        Modifier(
            stat="ItemQuantity",
            value=10.0,
            mod_type=ModifierType.INCREASED,
            source="unique:LeHeupOfAll",
        ),
        Modifier(
            stat="ItemRarity",
            value=10.0,
            mod_type=ModifierType.INCREASED,
            source="unique:LeHeupOfAll",
        ),
    ],
    "Malachai's Artifice": [
        Modifier(
            stat="SocketedGemsSupportedByElementalEquilibrium",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:MalachaisArtifice",
        ),
    ],
    "Mark of the Shaper": [
        Modifier(
            stat="SpellDamage",
            value=25.0,
            mod_type=ModifierType.INCREASED,
            source="unique:MarkOfTheShaper",
        ),
    ],
    "Mark of the Elder": [
        Modifier(
            stat="AttackDamage",
            value=25.0,
            mod_type=ModifierType.INCREASED,
            source="unique:MarkOfTheElder",
        ),
    ],
    "Pyre": [
        Modifier(
            stat="ColdToFire",
            value=50.0,
            mod_type=ModifierType.FLAT,
            source="unique:Pyre",
        ),
    ],
    "The Taming": [
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
    "Ventor's Gamble": [
        Modifier(
            stat="ItemQuantity",
            value=10.0,
            mod_type=ModifierType.INCREASED,
            source="unique:VentorsGamble",
        ),
        Modifier(
            stat="ItemRarity",
            value=10.0,
            mod_type=ModifierType.INCREASED,
            source="unique:VentorsGamble",
        ),
    ],
    # === AMULETS ===
    "Astramentis": [
        Modifier(
            stat="AllAttributes",
            value=116.0,
            mod_type=ModifierType.FLAT,
            source="unique:Astramentis",
        ),
    ],
    "Carnage Heart": [
        Modifier(
            stat="PhysicalDamageLeechedAsLife",
            value=2.0,
            mod_type=ModifierType.FLAT,
            source="unique:CarnageHeart",
        ),
        Modifier(
            stat="PhysicalDamageLeechedAsMana",
            value=2.0,
            mod_type=ModifierType.FLAT,
            source="unique:CarnageHeart",
        ),
    ],
    "Eye of Chayula": [
        Modifier(
            stat="ChaosResistance",
            value=20.0,
            mod_type=ModifierType.FLAT,
            source="unique:EyeOfChayula",
        ),
        Modifier(
            stat="CannotBeStunned",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:EyeOfChayula",
        ),
    ],
    "Presence of Chayula": [
        Modifier(
            stat="ChaosResistance",
            value=20.0,
            mod_type=ModifierType.FLAT,
            source="unique:PresenceOfChayula",
        ),
        Modifier(
            stat="CannotBeStunned",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:PresenceOfChayula",
        ),
        Modifier(
            stat="Life",
            value=20.0,
            mod_type=ModifierType.INCREASED,
            source="unique:PresenceOfChayula",
        ),
    ],
    "The Anvil": [
        Modifier(
            stat="BlockChance",
            value=8.0,
            mod_type=ModifierType.FLAT,
            source="unique:TheAnvil",
        ),
        Modifier(
            stat="SpellBlockChance",
            value=8.0,
            mod_type=ModifierType.FLAT,
            source="unique:TheAnvil",
        ),
        Modifier(
            stat="AttackSpeed",
            value=-20.0,
            mod_type=ModifierType.INCREASED,
            source="unique:TheAnvil",
        ),
    ],
    "The Ignomon": [
        Modifier(
            stat="FireDamage",
            value=30.0,
            mod_type=ModifierType.INCREASED,
            source="unique:TheIgnomon",
        ),
        Modifier(
            stat="Accuracy",
            value=200.0,
            mod_type=ModifierType.INCREASED,
            source="unique:TheIgnomon",
        ),
    ],
    "The Primordial Chain": [
        Modifier(
            stat="MinionLimit",
            value=2.0,
            mod_type=ModifierType.FLAT,
            source="unique:ThePrimordialChain",
        ),
        Modifier(
            stat="MinionDamage",
            value=50.0,
            mod_type=ModifierType.INCREASED,
            source="unique:ThePrimordialChain",
        ),
    ],
    "Xoph's Blood": [
        Modifier(
            stat="FireResistance",
            value=20.0,
            mod_type=ModifierType.FLAT,
            source="unique:XophsBlood",
        ),
        Modifier(
            stat="AvatarOfFire",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:XophsBlood",
        ),
    ],
    # === WEAPONS ===
    "Atziri's Disfavour": [
        Modifier(
            stat="PhysicalDamage",
            value=200.0,
            mod_type=ModifierType.INCREASED,
            source="unique:AtzirisDisfavour",
        ),
        Modifier(
            stat="MeleeSplash",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:AtzirisDisfavour",
        ),
    ],
    "Bino's Kitchen Knife": [
        Modifier(
            stat="PoisonOnHit",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:BinosKitchenKnife",
        ),
        Modifier(
            stat="PoisonSpreadOnKill",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:BinosKitchenKnife",
        ),
    ],
    "Doomfletch": [
        Modifier(
            stat="PhysicalDamageAsElemental",
            value=100.0,
            mod_type=ModifierType.FLAT,
            source="unique:Doomfletch",
        ),
    ],
    "Doomfletch Prism": [
        Modifier(
            stat="PhysicalDamageAsElemental",
            value=100.0,
            mod_type=ModifierType.FLAT,
            source="unique:DoomfletchPrism",
        ),
    ],
    "Frostbreath": [
        Modifier(
            stat="ColdDamage",
            value=100.0,
            mod_type=ModifierType.INCREASED,
            source="unique:Frostbreath",
        ),
        Modifier(
            stat="FreezeDuration",
            value=50.0,
            mod_type=ModifierType.INCREASED,
            source="unique:Frostbreath",
        ),
    ],
    "Hegemony's Era": [
        Modifier(
            stat="PowerCharges",
            value=1.0,
            mod_type=ModifierType.FLAT,
            source="unique:HegemonysEra",
        ),
        Modifier(
            stat="SpellDamagePerPowerCharge",
            value=8.0,
            mod_type=ModifierType.INCREASED,
            source="unique:HegemonysEra",
        ),
    ],
    "Kongor's Undying Rage": [
        Modifier(
            stat="CritChance",
            value=100.0,
            mod_type=ModifierType.INCREASED,
            source="unique:KongorsUndyingRage",
        ),
        Modifier(
            stat="CannotLeech",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:KongorsUndyingRage",
        ),
    ],
    "Lioneye's Glare": [
        Modifier(
            stat="HitChance",
            value=100.0,
            mod_type=ModifierType.FLAT,
            source="unique:LioneyesGlare",
        ),
    ],
    "Mjolner": [
        Modifier(
            stat="LightningSpellsCastOnHit",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:Mjolner",
        ),
    ],
    "Ngamahu's Flame": [
        Modifier(
            stat="FireSpellsCastOnHit",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:NgamahusFlame",
        ),
    ],
    "Oro's Sacrifice": [
        Modifier(
            stat="FireDamage",
            value=100.0,
            mod_type=ModifierType.INCREASED,
            source="unique:OrosSacrifice",
        ),
        Modifier(
            stat="FrenzyChargesOnIgnite",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:OrosSacrifice",
        ),
    ],
    "Queen's Decree": [
        Modifier(
            stat="MinionDamage",
            value=50.0,
            mod_type=ModifierType.INCREASED,
            source="unique:QueensDecree",
        ),
        Modifier(
            stat="MinionLife",
            value=50.0,
            mod_type=ModifierType.INCREASED,
            source="unique:QueensDecree",
        ),
    ],
    "Reach of the Council": [
        Modifier(
            stat="ProjectileDamage",
            value=50.0,
            mod_type=ModifierType.INCREASED,
            source="unique:ReachOfTheCouncil",
        ),
    ],
    "The Cauteriser": [
        Modifier(
            stat="FireDamage",
            value=100.0,
            mod_type=ModifierType.INCREASED,
            source="unique:TheCauteriser",
        ),
        Modifier(
            stat="IgniteChance",
            value=20.0,
            mod_type=ModifierType.FLAT,
            source="unique:TheCauteriser",
        ),
    ],
    "The Scourge": [
        Modifier(
            stat="MinionDamage",
            value=100.0,
            mod_type=ModifierType.INCREASED,
            source="unique:TheScourge",
        ),
        Modifier(
            stat="MinionAttackSpeed",
            value=30.0,
            mod_type=ModifierType.INCREASED,
            source="unique:TheScourge",
        ),
    ],
    "Touch of Anguish": [
        Modifier(
            stat="ColdDamage",
            value=50.0,
            mod_type=ModifierType.INCREASED,
            source="unique:TouchOfAnguish",
        ),
        Modifier(
            stat="FrenzyChargesOnKill",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:TouchOfAnguish",
        ),
    ],
    "Trypanon": [
        Modifier(
            stat="CritChance",
            value=100.0,
            mod_type=ModifierType.FLAT,
            source="unique:Trypanon",
        ),
        Modifier(
            stat="AttackSpeed",
            value=-30.0,
            mod_type=ModifierType.INCREASED,
            source="unique:Trypanon",
        ),
    ],
    "Varunastra": [
        Modifier(
            stat="OneHandedMeleeDamage",
            value=40.0,
            mod_type=ModifierType.INCREASED,
            source="unique:Varunastra",
        ),
    ],
    "Wings of Entropy": [
        Modifier(
            stat="BlockChance",
            value=6.0,
            mod_type=ModifierType.FLAT,
            source="unique:WingsOfEntropy",
        ),
        Modifier(
            stat="DualWieldBlock",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:WingsOfEntropy",
        ),
    ],
    # === SHIELDS ===
    "Aegis Aurora": [
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
    "Lioneye's Remorse": [
        Modifier(
            stat="BlockChance",
            value=8.0,
            mod_type=ModifierType.FLAT,
            source="unique:LioneyesRemorse",
        ),
        Modifier(
            stat="Armour",
            value=100.0,
            mod_type=ModifierType.INCREASED,
            source="unique:LioneyesRemorse",
        ),
    ],
    "Rathpith Globe": [
        Modifier(
            stat="SpellBlockChance",
            value=30.0,
            mod_type=ModifierType.FLAT,
            source="unique:RathpithGlobe",
        ),
        Modifier(
            stat="LifeToSpellBlock",
            value=1.0,
            mod_type=ModifierType.FLAT,
            source="unique:RathpithGlobe",
        ),
    ],
    "The Surrender": [
        Modifier(
            stat="BlockChance",
            value=8.0,
            mod_type=ModifierType.FLAT,
            source="unique:TheSurrender",
        ),
        Modifier(
            stat="LifeOnBlock",
            value=250.0,
            mod_type=ModifierType.FLAT,
            source="unique:TheSurrender",
        ),
    ],
    # === BODY ARMOUR ===
    "Belly of the Beast": [
        Modifier(
            stat="Life",
            value=40.0,
            mod_type=ModifierType.INCREASED,
            source="unique:BellyOfTheBeast",
        ),
    ],
    "Carcass Jack": [
        Modifier(
            stat="AreaOfEffect",
            value=20.0,
            mod_type=ModifierType.INCREASED,
            source="unique:CarcassJack",
        ),
        Modifier(
            stat="AreaDamage",
            value=20.0,
            mod_type=ModifierType.INCREASED,
            source="unique:CarcassJack",
        ),
    ],
    "Cherrubim's Maleficence": [
        Modifier(
            stat="PhysicalDamageLeechedAsLife",
            value=2.0,
            mod_type=ModifierType.FLAT,
            source="unique:CherrubimsMaleficence",
        ),
        Modifier(
            stat="PhysicalDamageLeechedAsMana",
            value=2.0,
            mod_type=ModifierType.FLAT,
            source="unique:CherrubimsMaleficence",
        ),
    ],
    "Cloak of Defiance": [
        Modifier(
            stat="MindOverMatter",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:CloakOfDefiance",
        ),
        Modifier(
            stat="Mana",
            value=40.0,
            mod_type=ModifierType.INCREASED,
            source="unique:CloakOfDefiance",
        ),
    ],
    "Kaom's Heart": [
        Modifier(
            stat="Life",
            value=100.0,
            mod_type=ModifierType.INCREASED,
            source="unique:KaomsHeart",
        ),
        Modifier(
            stat="NoSockets",
            value=1.0,
            mod_type=ModifierType.FLAG,
            source="unique:KaomsHeart",
        ),
    ],
    "Lightning Coil": [
        Modifier(
            stat="PhysicalDamageTakenAsLightning",
            value=30.0,
            mod_type=ModifierType.FLAT,
            source="unique:LightningCoil",
        ),
    ],
    "Loreweave": [
        Modifier(
            stat="MaxResistances",
            value=5.0,
            mod_type=ModifierType.FLAT,
            source="unique:Loreweave",
        ),
        Modifier(
            stat="MinResistances",
            value=5.0,
            mod_type=ModifierType.FLAT,
            source="unique:Loreweave",
        ),
    ],
    "Perfect Form": [
        Modifier(
            stat="FireResistance",
            value=20.0,
            mod_type=ModifierType.FLAT,
            source="unique:PerfectForm",
        ),
        Modifier(
            stat="ColdResistance",
            value=20.0,
            mod_type=ModifierType.FLAT,
            source="unique:PerfectForm",
        ),
        Modifier(
            stat="LightningResistance",
            value=20.0,
            mod_type=ModifierType.FLAT,
            source="unique:PerfectForm",
        ),
        Modifier(
            stat="Evasion",
            value=35.0,
            mod_type=ModifierType.INCREASED,
            source="unique:PerfectForm",
        ),
    ],
    "Queen of the Forest": [
        Modifier(
            stat="MovementSpeedPerEvasion",
            value=0.01,
            mod_type=ModifierType.FLAT,
            source="unique:QueenOfTheForest",
        ),
    ],
    "The Restless Ward": [
        Modifier(
            stat="EnduranceCharges",
            value=1.0,
            mod_type=ModifierType.FLAT,
            source="unique:TheRestlessWard",
        ),
        Modifier(
            stat="FrenzyCharges",
            value=1.0,
            mod_type=ModifierType.FLAT,
            source="unique:TheRestlessWard",
        ),
        Modifier(
            stat="PowerCharges",
            value=1.0,
            mod_type=ModifierType.FLAT,
            source="unique:TheRestlessWard",
        ),
    ],
    "Vis Mortis": [
        Modifier(
            stat="MinionDamage",
            value=30.0,
            mod_type=ModifierType.INCREASED,
            source="unique:VisMortis",
        ),
        Modifier(
            stat="MinionLife",
            value=30.0,
            mod_type=ModifierType.INCREASED,
            source="unique:VisMortis",
        ),
    ],
}

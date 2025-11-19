"""Parser for extracting modifiers from configuration settings.

This module parses configuration settings (buffs, curses, conditions, etc.)
and converts them to modifiers, replicating Path of Building's config system.
"""

from typing import Any

from pobapi.calculator.modifiers import Modifier, ModifierType

__all__ = ["ConfigModifierParser"]


class ConfigModifierParser:
    """Parser for extracting modifiers from configuration settings.

    This class processes configuration settings and converts them to Modifier objects.
    Configuration includes buffs, curses, enemy settings, conditions, etc.
    """

    @staticmethod
    def parse_config(config: Any) -> list[Modifier]:
        """
        Build a list of Modifier objects described by the provided build configuration.

        The parser inspects known flags and numeric fields on `config` and
        converts enabled buffs, charges, auras, curses, and conditional
        flags into corresponding Modifier instances; missing attributes
        are ignored.

        Parameters:
            config (Any): Configuration object containing build flags and
                optional numeric fields (e.g., max_power_charges) used to
                derive modifiers.

        Returns:
            list[Modifier]: Modifier instances derived from `config`; an
                empty list if no applicable flags are present.
        """
        modifiers: list[Modifier] = []

        try:
            # Buffs
            if config.onslaught:
                modifiers.append(
                    Modifier(
                        stat="AttackSpeed",
                        value=20.0,
                        mod_type=ModifierType.INCREASED,
                        source="config:onslaught",
                    )
                )
                modifiers.append(
                    Modifier(
                        stat="CastSpeed",
                        value=20.0,
                        mod_type=ModifierType.INCREASED,
                        source="config:onslaught",
                    )
                )
                modifiers.append(
                    Modifier(
                        stat="MovementSpeed",
                        value=20.0,
                        mod_type=ModifierType.INCREASED,
                        source="config:onslaught",
                    )
                )

            if config.fortify:
                modifiers.append(
                    Modifier(
                        stat="DamageTaken",
                        value=-20.0,
                        mod_type=ModifierType.INCREASED,
                        source="config:fortify",
                    )
                )

            if config.tailwind:
                modifiers.append(
                    Modifier(
                        stat="ActionSpeed",
                        value=10.0,
                        mod_type=ModifierType.INCREASED,
                        source="config:tailwind",
                    )
                )

            if config.adrenaline:
                modifiers.append(
                    Modifier(
                        stat="Damage",
                        value=100.0,
                        mod_type=ModifierType.INCREASED,
                        source="config:adrenaline",
                    )
                )
                modifiers.append(
                    Modifier(
                        stat="AttackSpeed",
                        value=25.0,
                        mod_type=ModifierType.INCREASED,
                        source="config:adrenaline",
                    )
                )
                modifiers.append(
                    Modifier(
                        stat="CastSpeed",
                        value=25.0,
                        mod_type=ModifierType.INCREASED,
                        source="config:adrenaline",
                    )
                )
                modifiers.append(
                    Modifier(
                        stat="MovementSpeed",
                        value=25.0,
                        mod_type=ModifierType.INCREASED,
                        source="config:adrenaline",
                    )
                )

            # Charges
            if hasattr(config, "use_power_charges") and config.use_power_charges:
                power_charges = getattr(config, "max_power_charges", 3)
                modifiers.append(
                    Modifier(
                        stat="CritChance",
                        value=power_charges * 50.0,
                        mod_type=ModifierType.INCREASED,
                        source="config:power_charges",
                    )
                )

            if hasattr(config, "use_frenzy_charges") and config.use_frenzy_charges:
                frenzy_charges = getattr(config, "max_frenzy_charges", 3)
                modifiers.append(
                    Modifier(
                        stat="AttackSpeed",
                        value=frenzy_charges * 4.0,
                        mod_type=ModifierType.INCREASED,
                        source="config:frenzy_charges",
                    )
                )
                modifiers.append(
                    Modifier(
                        stat="CastSpeed",
                        value=frenzy_charges * 4.0,
                        mod_type=ModifierType.INCREASED,
                        source="config:frenzy_charges",
                    )
                )
                modifiers.append(
                    Modifier(
                        stat="Damage",
                        value=frenzy_charges * 4.0,
                        mod_type=ModifierType.INCREASED,
                        source="config:frenzy_charges",
                    )
                )

            if (
                hasattr(config, "use_endurance_charges")
                and config.use_endurance_charges
            ):
                endurance_charges = getattr(config, "max_endurance_charges", 3)
                modifiers.append(
                    Modifier(
                        stat="PhysicalDamageReduction",
                        value=endurance_charges * 4.0,
                        mod_type=ModifierType.FLAT,
                        source="config:endurance_charges",
                    )
                )
                modifiers.append(
                    Modifier(
                        stat="FireResistance",
                        value=endurance_charges * 4.0,
                        mod_type=ModifierType.FLAT,
                        source="config:endurance_charges",
                    )
                )
                modifiers.append(
                    Modifier(
                        stat="ColdResistance",
                        value=endurance_charges * 4.0,
                        mod_type=ModifierType.FLAT,
                        source="config:endurance_charges",
                    )
                )
                modifiers.append(
                    Modifier(
                        stat="LightningResistance",
                        value=endurance_charges * 4.0,
                        mod_type=ModifierType.FLAT,
                        source="config:endurance_charges",
                    )
                )

            # Auras and buffs
            if hasattr(config, "has_hatred") and config.has_hatred:
                # Hatred: 36% more cold damage, 15% of physical as extra cold
                modifiers.append(
                    Modifier(
                        stat="ColdDamage",
                        value=36.0,
                        mod_type=ModifierType.MORE,
                        source="config:hatred",
                    )
                )
                modifiers.append(
                    Modifier(
                        stat="PhysicalAsExtraCold",
                        value=15.0,
                        mod_type=ModifierType.FLAT,
                        source="config:hatred",
                    )
                )

            if hasattr(config, "has_anger") and config.has_anger:
                # Anger: 36% more fire damage, 15% of physical as extra fire
                modifiers.append(
                    Modifier(
                        stat="FireDamage",
                        value=36.0,
                        mod_type=ModifierType.MORE,
                        source="config:anger",
                    )
                )
                modifiers.append(
                    Modifier(
                        stat="PhysicalAsExtraFire",
                        value=15.0,
                        mod_type=ModifierType.FLAT,
                        source="config:anger",
                    )
                )

            if hasattr(config, "has_wrath") and config.has_wrath:
                # Wrath: 36% more lightning damage, 15% of physical as extra lightning
                modifiers.append(
                    Modifier(
                        stat="LightningDamage",
                        value=36.0,
                        mod_type=ModifierType.MORE,
                        source="config:wrath",
                    )
                )
                modifiers.append(
                    Modifier(
                        stat="PhysicalAsExtraLightning",
                        value=15.0,
                        mod_type=ModifierType.FLAT,
                        source="config:wrath",
                    )
                )

            if hasattr(config, "has_haste") and config.has_haste:
                # Haste: 21% increased attack/cast/movement speed
                modifiers.append(
                    Modifier(
                        stat="AttackSpeed",
                        value=21.0,
                        mod_type=ModifierType.INCREASED,
                        source="config:haste",
                    )
                )
                modifiers.append(
                    Modifier(
                        stat="CastSpeed",
                        value=21.0,
                        mod_type=ModifierType.INCREASED,
                        source="config:haste",
                    )
                )
                modifiers.append(
                    Modifier(
                        stat="MovementSpeed",
                        value=21.0,
                        mod_type=ModifierType.INCREASED,
                        source="config:haste",
                    )
                )

            if hasattr(config, "has_grace") and config.has_grace:
                # Grace: 3000+ evasion rating
                modifiers.append(
                    Modifier(
                        stat="Evasion",
                        value=3000.0,
                        mod_type=ModifierType.FLAT,
                        source="config:grace",
                    )
                )

            if hasattr(config, "has_determination") and config.has_determination:
                # Determination: 3000+ armour
                modifiers.append(
                    Modifier(
                        stat="Armour",
                        value=3000.0,
                        mod_type=ModifierType.FLAT,
                        source="config:determination",
                    )
                )

            if hasattr(config, "has_discipline") and config.has_discipline:
                # Discipline: 200+ energy shield
                modifiers.append(
                    Modifier(
                        stat="EnergyShield",
                        value=200.0,
                        mod_type=ModifierType.FLAT,
                        source="config:discipline",
                    )
                )

            # Curses (simplified - full implementation would check enemy level)
            if hasattr(config, "has_flammability") and config.has_flammability:
                # Flammability: -44% fire resistance
                modifiers.append(
                    Modifier(
                        stat="EnemyFireResistance",
                        value=-44.0,
                        mod_type=ModifierType.FLAT,
                        source="config:flammability",
                    )
                )

            if hasattr(config, "has_frostbite") and config.has_frostbite:
                # Frostbite: -44% cold resistance
                modifiers.append(
                    Modifier(
                        stat="EnemyColdResistance",
                        value=-44.0,
                        mod_type=ModifierType.FLAT,
                        source="config:frostbite",
                    )
                )

            if hasattr(config, "has_conductivity") and config.has_conductivity:
                # Conductivity: -44% lightning resistance
                modifiers.append(
                    Modifier(
                        stat="EnemyLightningResistance",
                        value=-44.0,
                        mod_type=ModifierType.FLAT,
                        source="config:conductivity",
                    )
                )

            if hasattr(config, "has_enfeeble") and config.has_enfeeble:
                # Enfeeble: -30% damage dealt
                modifiers.append(
                    Modifier(
                        stat="EnemyDamage",
                        value=-30.0,
                        mod_type=ModifierType.INCREASED,
                        source="config:enfeeble",
                    )
                )

            if hasattr(config, "has_vulnerability") and config.has_vulnerability:
                # Vulnerability: +25% physical damage taken
                modifiers.append(
                    Modifier(
                        stat="EnemyPhysicalDamageTaken",
                        value=25.0,
                        mod_type=ModifierType.INCREASED,
                        source="config:vulnerability",
                    )
                )

            # Conditions
            if hasattr(config, "on_full_life") and config.on_full_life:
                # Many items/skills have "on full life" modifiers
                # This would be handled by conditional modifiers
                modifiers.append(
                    Modifier(
                        stat="OnFullLife",
                        value=1.0,
                        mod_type=ModifierType.FLAG,
                        source="config:on_full_life",
                    )
                )

            if hasattr(config, "on_low_life") and config.on_low_life:
                # "On low life" conditions
                modifiers.append(
                    Modifier(
                        stat="OnLowLife",
                        value=1.0,
                        mod_type=ModifierType.FLAG,
                        source="config:on_low_life",
                    )
                )

            if (
                hasattr(config, "on_full_energy_shield")
                and config.on_full_energy_shield
            ):
                modifiers.append(
                    Modifier(
                        stat="OnFullEnergyShield",
                        value=1.0,
                        mod_type=ModifierType.FLAG,
                        source="config:on_full_energy_shield",
                    )
                )

            if hasattr(config, "on_full_mana") and config.on_full_mana:
                modifiers.append(
                    Modifier(
                        stat="OnFullMana",
                        value=1.0,
                        mod_type=ModifierType.FLAG,
                        source="config:on_full_mana",
                    )
                )

            # Enemy settings affect calculations but don't create modifiers
            # They affect how damage is calculated (resistances, etc.)

        except AttributeError:
            # If config doesn't have expected attributes, skip
            pass

        return modifiers

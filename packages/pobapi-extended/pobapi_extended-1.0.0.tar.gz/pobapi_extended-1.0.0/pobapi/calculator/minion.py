"""Minion calculation system for Path of Building.

This module handles all minion-related calculations including:
- Minion damage calculations
- Minion defense calculations (life, resistances, etc.)
- Minion attack/cast speed
- Minion modifiers from player
"""

from dataclasses import dataclass
from typing import Any

from pobapi.calculator.modifiers import ModifierSystem, ModifierType

__all__ = ["MinionStats", "MinionCalculator"]


@dataclass
class MinionStats:
    """Minion statistics.

    :param damage_physical: Physical damage.
    :param damage_fire: Fire damage.
    :param damage_cold: Cold damage.
    :param damage_lightning: Lightning damage.
    :param damage_chaos: Chaos damage.
    :param life: Minion life.
    :param energy_shield: Minion energy shield.
    :param armour: Minion armour.
    :param evasion: Minion evasion.
    :param attack_speed: Minion attack speed multiplier.
    :param cast_speed: Minion cast speed multiplier.
    :param movement_speed: Minion movement speed multiplier.
    :param crit_chance: Minion critical strike chance.
    :param crit_multiplier: Minion critical strike multiplier.
    :param accuracy: Minion accuracy rating.
    :param fire_resistance: Minion fire resistance.
    :param cold_resistance: Minion cold resistance.
    :param lightning_resistance: Minion lightning resistance.
    :param chaos_resistance: Minion chaos resistance.
    :param dps: Total minion DPS.
    """

    damage_physical: float = 0.0
    damage_fire: float = 0.0
    damage_cold: float = 0.0
    damage_lightning: float = 0.0
    damage_chaos: float = 0.0
    life: float = 0.0
    energy_shield: float = 0.0
    armour: float = 0.0
    evasion: float = 0.0
    attack_speed: float = 1.0
    cast_speed: float = 1.0
    movement_speed: float = 1.0
    crit_chance: float = 5.0  # Base 5%
    crit_multiplier: float = 150.0  # Base 150%
    accuracy: float = 0.0
    fire_resistance: float = 0.0
    cold_resistance: float = 0.0
    lightning_resistance: float = 0.0
    chaos_resistance: float = 0.0
    dps: float = 0.0

    @property
    def total_damage(self) -> float:
        """Get total damage across all types."""
        return (
            self.damage_physical
            + self.damage_fire
            + self.damage_cold
            + self.damage_lightning
            + self.damage_chaos
        )


class MinionCalculator:
    """Calculator for minion statistics.

    This class calculates minion damage, defense, and other stats
    based on player modifiers that affect minions.
    """

    def __init__(self, modifier_system: ModifierSystem):
        """Initialize minion calculator.

        :param modifier_system: The ModifierSystem instance to use for calculations.
        """
        self.modifiers = modifier_system

    def calculate_minion_damage(
        self,
        base_damage: dict[str, float] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, float]:
        """Calculate minion damage by type.

        :param base_damage: Base damage by type (optional).
        :param context: Calculation context.
        :return: Dictionary mapping damage type -> damage value.
        """
        if context is None:
            context = {}
        if base_damage is None:
            base_damage = {}

        # Calculate damage for each type
        damage_types = ["Physical", "Fire", "Cold", "Lightning", "Chaos"]
        result: dict[str, float] = {}

        for dmg_type in damage_types:
            base = base_damage.get(dmg_type, 0.0)

            # Get minion damage flat modifiers (type-specific)
            minion_damage_flat = self.modifiers.calculate_stat(
                f"Minion{dmg_type}Damage", base, context
            )

            # Apply general minion damage multipliers (increased/more)
            # This applies to all damage types
            minion_damage_increased = self.modifiers.calculate_stat(
                "MinionDamage", 0.0, context
            )

            # Apply type-specific minion damage increased
            type_specific_increased = self.modifiers.calculate_stat(
                f"Minion{dmg_type}Damage", 0.0, context
            )
            # Subtract the flat part to get only increased
            type_specific_increased = type_specific_increased - minion_damage_flat

            # Calculate final damage
            # Base + flat modifiers
            total = minion_damage_flat

            # Apply increased modifiers (additive)
            increased_total = minion_damage_increased + type_specific_increased
            if increased_total != 0.0:
                total = total * (1.0 + increased_total / 100.0)

            # Apply more/less modifiers (multiplicative)
            # Get MORE/LESS modifiers directly and sum their values
            more_mods = [
                m
                for m in self.modifiers.get_modifiers("MinionDamageMore", context)
                if m.mod_type == ModifierType.MORE
            ]
            less_mods = [
                m
                for m in self.modifiers.get_modifiers("MinionDamageLess", context)
                if m.mod_type == ModifierType.LESS
            ]
            more_total = sum(m.value for m in more_mods)
            less_total = sum(m.value for m in less_mods)

            if more_total != 0.0 or less_total != 0.0:
                more_mult = 1.0 + (more_total - less_total) / 100.0
                total = total * more_mult

            result[dmg_type] = max(0.0, total)

        return result

    def calculate_minion_life(
        self, base_life: float = 0.0, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate minion life.

        :param base_life: Base minion life.
        :param context: Calculation context.
        :return: Total minion life.
        """
        if context is None:
            context = {}

        # Get minion life modifiers
        minion_life_flat = self.modifiers.calculate_stat(
            "MinionLife", base_life, context
        )

        # Apply increased modifiers
        minion_life_increased = self.modifiers.calculate_stat(
            "MinionLife", 0.0, context
        )

        # Calculate final life
        total = minion_life_flat
        if minion_life_increased != 0.0:
            total = total * (1.0 + minion_life_increased / 100.0)

        # Apply more/less modifiers
        more_mods = [
            m
            for m in self.modifiers.get_modifiers("MinionLifeMore", context)
            if m.mod_type == ModifierType.MORE
        ]
        less_mods = [
            m
            for m in self.modifiers.get_modifiers("MinionLifeLess", context)
            if m.mod_type == ModifierType.LESS
        ]
        more_total = sum(m.value for m in more_mods)
        less_total = sum(m.value for m in less_mods)

        if more_total != 0.0 or less_total != 0.0:
            more_mult = 1.0 + (more_total - less_total) / 100.0
            total = total * more_mult

        return max(0.0, total)

    def calculate_minion_energy_shield(
        self, base_es: float = 0.0, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate minion energy shield.

        :param base_es: Base minion energy shield.
        :param context: Calculation context.
        :return: Total minion energy shield.
        """
        if context is None:
            context = {}

        # Get minion ES modifiers
        minion_es_flat = self.modifiers.calculate_stat(
            "MinionEnergyShield", base_es, context
        )

        # Apply increased modifiers
        minion_es_increased = self.modifiers.calculate_stat(
            "MinionEnergyShield", 0.0, context
        )

        # Calculate final ES
        total = minion_es_flat
        if minion_es_increased != 0.0:
            total = total * (1.0 + minion_es_increased / 100.0)

        # Apply more/less modifiers
        more_mods = [
            m
            for m in self.modifiers.get_modifiers("MinionEnergyShieldMore", context)
            if m.mod_type == ModifierType.MORE
        ]
        less_mods = [
            m
            for m in self.modifiers.get_modifiers("MinionEnergyShieldLess", context)
            if m.mod_type == ModifierType.LESS
        ]
        more_total = sum(m.value for m in more_mods)
        less_total = sum(m.value for m in less_mods)

        if more_total != 0.0 or less_total != 0.0:
            more_mult = 1.0 + (more_total - less_total) / 100.0
            total = total * more_mult

        return max(0.0, total)

    def calculate_minion_attack_speed(
        self, base_speed: float = 1.0, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate minion attack speed multiplier.

        :param base_speed: Base attack speed.
        :param context: Calculation context.
        :return: Final attack speed multiplier.
        """
        if context is None:
            context = {}

        # Get minion attack speed modifiers
        minion_attack_speed_increased = self.modifiers.calculate_stat(
            "MinionAttackSpeed", 0.0, context
        )

        # Calculate final speed
        total = base_speed
        if minion_attack_speed_increased != 0.0:
            total = total * (1.0 + minion_attack_speed_increased / 100.0)

        # Apply more/less modifiers
        more_mods = [
            m
            for m in self.modifiers.get_modifiers("MinionAttackSpeedMore", context)
            if m.mod_type == ModifierType.MORE
        ]
        less_mods = [
            m
            for m in self.modifiers.get_modifiers("MinionAttackSpeedLess", context)
            if m.mod_type == ModifierType.LESS
        ]
        more_total = sum(m.value for m in more_mods)
        less_total = sum(m.value for m in less_mods)

        if more_total != 0.0 or less_total != 0.0:
            more_mult = 1.0 + (more_total - less_total) / 100.0
            total = total * more_mult

        return max(0.0, total)

    def calculate_minion_cast_speed(
        self, base_speed: float = 1.0, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate minion cast speed multiplier.

        :param base_speed: Base cast speed.
        :param context: Calculation context.
        :return: Final cast speed multiplier.
        """
        if context is None:
            context = {}

        # Get minion cast speed modifiers
        minion_cast_speed_increased = self.modifiers.calculate_stat(
            "MinionCastSpeed", 0.0, context
        )

        # Calculate final speed
        total = base_speed
        if minion_cast_speed_increased != 0.0:
            total = total * (1.0 + minion_cast_speed_increased / 100.0)

        # Apply more/less modifiers
        more_mods = [
            m
            for m in self.modifiers.get_modifiers("MinionCastSpeedMore", context)
            if m.mod_type == ModifierType.MORE
        ]
        less_mods = [
            m
            for m in self.modifiers.get_modifiers("MinionCastSpeedLess", context)
            if m.mod_type == ModifierType.LESS
        ]
        more_total = sum(m.value for m in more_mods)
        less_total = sum(m.value for m in less_mods)

        if more_total != 0.0 or less_total != 0.0:
            more_mult = 1.0 + (more_total - less_total) / 100.0
            total = total * more_mult

        return max(0.0, total)

    def calculate_minion_movement_speed(
        self, base_speed: float = 1.0, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate minion movement speed multiplier.

        :param base_speed: Base movement speed.
        :param context: Calculation context.
        :return: Final movement speed multiplier.
        """
        if context is None:
            context = {}

        # Get minion movement speed modifiers
        minion_movement_speed_increased = self.modifiers.calculate_stat(
            "MinionMovementSpeed", 0.0, context
        )

        # Calculate final speed
        total = base_speed
        if minion_movement_speed_increased != 0.0:
            total = total * (1.0 + minion_movement_speed_increased / 100.0)

        # Apply more/less modifiers
        more_mods = [
            m
            for m in self.modifiers.get_modifiers("MinionMovementSpeedMore", context)
            if m.mod_type == ModifierType.MORE
        ]
        less_mods = [
            m
            for m in self.modifiers.get_modifiers("MinionMovementSpeedLess", context)
            if m.mod_type == ModifierType.LESS
        ]
        more_total = sum(m.value for m in more_mods)
        less_total = sum(m.value for m in less_mods)

        if more_total != 0.0 or less_total != 0.0:
            more_mult = 1.0 + (more_total - less_total) / 100.0
            total = total * more_mult

        return max(0.0, total)

    def calculate_minion_crit_chance(
        self, base_chance: float = 5.0, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate minion critical strike chance.

        :param base_chance: Base crit chance (default 5%).
        :param context: Calculation context.
        :return: Final crit chance.
        """
        if context is None:
            context = {}

        # Get minion crit chance modifiers (applies flat + increased)
        minion_crit_chance_total = self.modifiers.calculate_stat(
            "MinionCritChance", base_chance, context
        )

        # Get only increased modifiers to avoid double application
        increased_mods = [
            m
            for m in self.modifiers.get_modifiers("MinionCritChance", context)
            if m.mod_type == ModifierType.INCREASED
        ]
        increased_total = sum(m.value for m in increased_mods)

        # Calculate final crit chance
        # If we have increased modifiers, we need to recalculate
        # to avoid double application
        if increased_total != 0.0:
            # Get flat modifiers separately
            flat_mods = [
                m
                for m in self.modifiers.get_modifiers("MinionCritChance", context)
                if m.mod_type == ModifierType.FLAT
            ]
            flat_total = sum(m.value for m in flat_mods)
            # Recalculate: base + flat, then apply increased
            total = (base_chance + flat_total) * (1.0 + increased_total / 100.0)
        else:
            total = minion_crit_chance_total

        # Cap at 100%
        return min(100.0, max(0.0, total))

    def calculate_minion_crit_multiplier(
        self, base_multiplier: float = 150.0, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate minion critical strike multiplier.

        :param base_multiplier: Base crit multiplier (default 150%).
        :param context: Calculation context.
        :return: Final crit multiplier.
        """
        if context is None:
            context = {}

        # Get minion crit multiplier modifiers (applies flat + increased)
        minion_crit_mult_total = self.modifiers.calculate_stat(
            "MinionCritMultiplier", base_multiplier, context
        )

        # Get only increased modifiers to avoid double application
        increased_mods = [
            m
            for m in self.modifiers.get_modifiers("MinionCritMultiplier", context)
            if m.mod_type == ModifierType.INCREASED
        ]
        increased_total = sum(m.value for m in increased_mods)

        # Calculate final crit multiplier
        # If we have increased modifiers, we need to recalculate
        # to avoid double application
        if increased_total != 0.0:
            # Get flat modifiers separately
            flat_mods = [
                m
                for m in self.modifiers.get_modifiers("MinionCritMultiplier", context)
                if m.mod_type == ModifierType.FLAT
            ]
            flat_total = sum(m.value for m in flat_mods)
            # Recalculate: base + flat, then apply increased
            total = (base_multiplier + flat_total) * (1.0 + increased_total / 100.0)
        else:
            total = minion_crit_mult_total

        return max(100.0, total)  # Minimum 100%

    def calculate_minion_resistances(
        self, context: dict[str, Any] | None = None
    ) -> dict[str, float]:
        """Calculate minion resistances.

        :param context: Calculation context.
        :return: Dictionary mapping resistance type -> resistance value.
        """
        if context is None:
            context = {}

        resistances = {
            "fire": self.modifiers.calculate_stat("MinionFireResistance", 0.0, context),
            "cold": self.modifiers.calculate_stat("MinionColdResistance", 0.0, context),
            "lightning": self.modifiers.calculate_stat(
                "MinionLightningResistance", 0.0, context
            ),
            "chaos": self.modifiers.calculate_stat(
                "MinionChaosResistance", 0.0, context
            ),
        }

        return resistances

    def calculate_minion_dps(
        self,
        base_damage: dict[str, float] | None = None,
        base_attack_speed: float = 1.0,
        context: dict[str, Any] | None = None,
    ) -> float:
        """Calculate minion DPS.

        :param base_damage: Base damage by type.
        :param base_attack_speed: Base attack speed.
        :param context: Calculation context.
        :return: Total minion DPS.
        """
        if context is None:
            context = {}

        # Calculate damage
        damage = self.calculate_minion_damage(base_damage, context)
        total_damage = sum(damage.values())

        # Calculate attack speed
        attack_speed = self.calculate_minion_attack_speed(base_attack_speed, context)

        # Calculate crit multiplier
        crit_chance = self.calculate_minion_crit_chance(context=context) / 100.0
        crit_multiplier = self.calculate_minion_crit_multiplier(context=context) / 100.0

        # Calculate average damage per hit (with crits)
        avg_damage_per_hit = total_damage * (
            1.0 - crit_chance + crit_chance * crit_multiplier
        )

        # Calculate DPS
        dps = avg_damage_per_hit * attack_speed

        return max(0.0, dps)

    def calculate_all_minion_stats(
        self,
        base_damage: dict[str, float] | None = None,
        base_life: float = 0.0,
        base_es: float = 0.0,
        base_attack_speed: float = 1.0,
        base_cast_speed: float = 1.0,
        context: dict[str, Any] | None = None,
    ) -> MinionStats:
        """Calculate all minion statistics.

        :param base_damage: Base damage by type.
        :param base_life: Base minion life.
        :param base_es: Base minion energy shield.
        :param base_attack_speed: Base attack speed.
        :param base_cast_speed: Base cast speed.
        :param context: Calculation context.
        :return: MinionStats object with all calculated stats.
        """
        if context is None:
            context = {}

        # Calculate damage
        damage = self.calculate_minion_damage(base_damage, context)

        # Calculate defense
        life = self.calculate_minion_life(base_life, context)
        es = self.calculate_minion_energy_shield(base_es, context)

        # Calculate speeds
        attack_speed = self.calculate_minion_attack_speed(base_attack_speed, context)
        cast_speed = self.calculate_minion_cast_speed(base_cast_speed, context)
        movement_speed = self.calculate_minion_movement_speed(context=context)

        # Calculate crit stats
        crit_chance = self.calculate_minion_crit_chance(context=context)
        crit_multiplier = self.calculate_minion_crit_multiplier(context=context)

        # Calculate resistances
        resistances = self.calculate_minion_resistances(context)

        # Calculate DPS
        dps = self.calculate_minion_dps(base_damage, base_attack_speed, context)

        # Get other stats
        accuracy = self.modifiers.calculate_stat("MinionAccuracy", 0.0, context)
        armour = self.modifiers.calculate_stat("MinionArmour", 0.0, context)
        evasion = self.modifiers.calculate_stat("MinionEvasion", 0.0, context)

        return MinionStats(
            damage_physical=damage.get("Physical", 0.0),
            damage_fire=damage.get("Fire", 0.0),
            damage_cold=damage.get("Cold", 0.0),
            damage_lightning=damage.get("Lightning", 0.0),
            damage_chaos=damage.get("Chaos", 0.0),
            life=life,
            energy_shield=es,
            armour=armour,
            evasion=evasion,
            attack_speed=attack_speed,
            cast_speed=cast_speed,
            movement_speed=movement_speed,
            crit_chance=crit_chance,
            crit_multiplier=crit_multiplier,
            accuracy=accuracy,
            fire_resistance=resistances.get("fire", 0.0),
            cold_resistance=resistances.get("cold", 0.0),
            lightning_resistance=resistances.get("lightning", 0.0),
            chaos_resistance=resistances.get("chaos", 0.0),
            dps=dps,
        )

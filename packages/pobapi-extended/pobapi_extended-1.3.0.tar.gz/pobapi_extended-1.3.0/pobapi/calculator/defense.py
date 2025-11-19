"""Defensive calculation system for Path of Building.

This module handles all defensive calculations including:
- Life/Mana/Energy Shield totals
- Armour and physical damage reduction
- Evasion and evade chance
- Block, dodge, spell suppression
- Maximum hit taken
- Effective Health Pool (EHP)
"""

from dataclasses import dataclass
from typing import Any

from pobapi.calculator.modifiers import ModifierSystem
from pobapi.types import DamageType

__all__ = ["DefenseStats", "DefenseCalculator"]


@dataclass
class DefenseStats:
    """Defensive statistics.

    :param life: Total life.
    :param mana: Total mana.
    :param energy_shield: Total energy shield.
    :param armour: Armour rating.
    :param evasion: Evasion rating.
    :param block_chance: Block chance.
    :param spell_block_chance: Spell block chance.
    :param spell_suppression_chance: Spell suppression chance.
    :param fire_resistance: Fire resistance.
    :param cold_resistance: Cold resistance.
    :param lightning_resistance: Lightning resistance.
    :param chaos_resistance: Chaos resistance.
    """

    life: float = 0.0
    mana: float = 0.0
    energy_shield: float = 0.0
    armour: float = 0.0
    evasion: float = 0.0
    block_chance: float = 0.0
    spell_block_chance: float = 0.0
    spell_suppression_chance: float = 0.0
    fire_resistance: float = 0.0
    cold_resistance: float = 0.0
    lightning_resistance: float = 0.0
    chaos_resistance: float = 0.0


class DefenseCalculator:
    """Calculator for defensive stats.

    This class replicates Path of Building's defensive calculation system.
    """

    def __init__(self, modifier_system: ModifierSystem):
        """Initialize defense calculator.

        :param modifier_system: Modifier system to use for calculations.
        """
        self.modifiers = modifier_system

    def calculate_life(self, context: dict[str, Any] | None = None) -> float:
        """
        Compute total life after applying modifiers.

        Parameters:
            context (dict[str, Any] | None): Optional calculation context
                providing base values and additional state used by modifiers
                (defaults to an empty dict).

        Returns:
            float: Total life after modifiers have been applied.
        """
        if context is None:
            context = {}

        # Base life from character class and level
        base_life = context.get("base_life", 0.0)

        # Calculate with modifiers
        return self.modifiers.calculate_stat("Life", base_life, context)

    def calculate_mana(self, context: dict[str, Any] | None = None) -> float:
        """
        Compute total mana based on the provided base mana and active modifiers.

        Parameters:
            context (dict[str, Any] | None): Optional calculation context.
                May include the key `base_mana` (float) which defaults to
                0.0 when absent.

        Returns:
            total_mana (float): Mana value after applying modifiers.
        """
        if context is None:
            context = {}

        base_mana = context.get("base_mana", 0.0)
        return self.modifiers.calculate_stat("Mana", base_mana, context)

    def calculate_energy_shield(self, context: dict[str, Any] | None = None) -> float:
        """
        Calculate total energy shield after applying modifiers.

        Parameters:
            context (dict[str, Any] | None): Optional calculation context.
                If provided, the function will read "base_energy_shield"
                from this mapping as the base value (defaults to 0.0).

        Returns:
            Total energy shield value after modifiers have been applied.
        """
        if context is None:
            context = {}

        base_es = context.get("base_energy_shield", 0.0)
        return self.modifiers.calculate_stat("EnergyShield", base_es, context)

    def calculate_armour(self, context: dict[str, Any] | None = None) -> float:
        """
        Compute total armour rating after applying configured modifiers.

        Parameters:
            context (dict[str, Any] | None): Optional calculation context
                that may provide `base_armour` and other keys used by the
                modifier system.

        Returns:
            float: Total armour rating.
        """
        if context is None:
            context = {}

        base_armour = context.get("base_armour", 0.0)
        return self.modifiers.calculate_stat("Armour", base_armour, context)

    def calculate_physical_damage_reduction(
        self, hit_damage: float, context: dict[str, Any] | None = None
    ) -> float:
        """Calculate physical damage reduction from armour.

        Path of Exile uses the formula:
        DR = Armour / (Armour + 10 * HitDamage)

        :param hit_damage: Physical hit damage.
        :param context: Current calculation context.
        :return: Physical damage reduction (0.0 to 1.0).
        """
        if context is None:
            context = {}

        armour = self.calculate_armour(context)

        if armour == 0.0 or hit_damage == 0.0:
            return 0.0

        # PoE armour formula
        reduction = armour / (armour + 10.0 * hit_damage)

        # Cap at 90% (hard cap in PoE)
        return min(reduction, 0.9)

    def calculate_evasion(self, context: dict[str, Any] | None = None) -> float:
        """
        Compute total evasion rating after applying configured modifiers.

        Parameters:
            context (dict[str, Any] | None): Calculation context that may
                provide "base_evasion" and other modifier inputs. If
                omitted, a default empty context is used.

        Returns:
            float: Total evasion rating after modifiers.
        """
        if context is None:
            context = {}

        base_evasion = context.get("base_evasion", 0.0)
        return self.modifiers.calculate_stat("Evasion", base_evasion, context)

    def calculate_evade_chance(
        self, enemy_accuracy: float, context: dict[str, Any] | None = None
    ) -> float:
        """
        Calculate the chance to evade an incoming hit against an enemy accuracy rating.

        Uses the Path of Exile formula: EvadeChance = 1 - (EnemyAccuracy /
        (EnemyAccuracy + Evasion / 5)). If enemy_accuracy is 0, returns
        1.0. The result is capped at 0.95.

        Parameters:
            enemy_accuracy (float): Enemy accuracy rating used in the formula.
            context (dict[str, Any] | None): Optional calculation context.

        Returns:
            float: Evade chance as a value between 0.0 and 1.0, capped at 0.95.
        """
        if context is None:
            context = {}

        evasion = self.calculate_evasion(context)

        if enemy_accuracy == 0.0:
            return 1.0

        # PoE evasion formula
        evade_chance = 1.0 - (enemy_accuracy / (enemy_accuracy + evasion / 5.0))

        # Cap at 95% (hard cap in PoE)
        return min(evade_chance, 0.95)

    def _calculate_quadratic_discriminant(self, a: float, b: float, c: float) -> float:
        """Calculate discriminant for quadratic equation: b^2 - 4ac.

        This method is extracted to allow testing of edge cases (e.g.,
        negative discriminant) that are mathematically unreachable with
        correct formula but serve as safety fallbacks.

        Args:
            a: Coefficient of x^2 term.
            b: Coefficient of x term.
            c: Constant term.

        Returns:
            Discriminant value: b^2 - 4ac.
        """
        return b * b - 4.0 * a * c

    def calculate_maximum_hit_taken(
        self, damage_type: str | DamageType, context: dict[str, Any] | None = None
    ) -> float:
        """
        Compute the maximum single hit that will deplete the character's
        life and energy shield for the given damage type.

        The returned value represents the largest incoming hit which, after
        applying defenses for the specified damage type, reduces the sum of
        Life and Energy Shield to zero. For "Physical", the calculation
        accounts for armour-based damage reduction; for "Fire", "Cold",
        "Lightning", and "Chaos", the calculation accounts for the
        corresponding resistance (capped at 75% before use). If an unknown
        damage type is provided, the raw life + energy shield pool is
        returned.

        Parameters:
            damage_type (Union[str, DamageType]): One of "Physical",
                "Fire", "Cold", "Lightning", or "Chaos", or DamageType enum.
            context (dict[str, Any] | None): Optional calculation context
                forwarded to modifier lookups.

        Returns:
            float: Maximum single-hit damage that will reduce life + energy
                shield to zero.
        """
        if context is None:
            context = {}

        # Convert enum to string if needed
        if isinstance(damage_type, DamageType):
            damage_type = damage_type.value

        life = self.calculate_life(context)
        es = self.calculate_energy_shield(context)
        total_pool = life + es

        if damage_type in (DamageType.PHYSICAL.value, "Physical"):
            # Physical damage reduction from armour
            # We need to solve: HitDamage * (1 - DR) = TotalPool
            # Where DR = Armour / (Armour + 10 * HitDamage)
            # Rearranging: HitDamage = TotalPool / (1 - Armour /
            #                                        (Armour + 10 * HitDamage))
            # This is a quadratic equation:
            # HitDamage = TotalPool * (Armour + 10 * HitDamage) /
            #             (10 * HitDamage)
            # Solving: HitDamage * 10 * HitDamage =
            #          TotalPool * (Armour + 10 * HitDamage)
            # 10 * HitDamage^2 = TotalPool * Armour + TotalPool * 10 * HitDamage
            # 10 * HitDamage^2 - TotalPool * 10 * HitDamage - TotalPool * Armour = 0
            # Using quadratic formula: x = (-b + sqrt(b^2 - 4ac)) / 2a
            # where a = 10, b = -TotalPool * 10, c = -TotalPool * Armour

            armour = self.calculate_armour(context)
            if armour == 0.0:
                return total_pool

            # Solve quadratic equation for maximum hit
            # 10x^2 - 10*TotalPool*x - TotalPool*Armour = 0
            a = 10.0
            b = -10.0 * total_pool
            c = -total_pool * armour

            # Calculate discriminant: b^2 - 4ac
            # For our formula: discriminant = (-10*total_pool)^2
            # - 4*10*(-total_pool*armour)
            #                  = 100*total_pool^2 + 40*total_pool*armour
            # This is always positive for positive total_pool and armour
            # The check for negative discriminant is a safety fallback for edge cases
            discriminant = self._calculate_quadratic_discriminant(a, b, c)
            if discriminant < 0:
                # Fallback to approximation (mathematically unreachable
                # with correct formula, but kept as safety fallback for
                # floating point errors or edge cases)
                return total_pool * 2.0

            max_hit = (-b + (discriminant**0.5)) / (2.0 * a)

            # Verify the result
            actual_reduction = self.calculate_physical_damage_reduction(
                max_hit, context
            )
            actual_damage_taken = max_hit * (1.0 - actual_reduction)

            # If close enough, return; otherwise refine
            if abs(actual_damage_taken - total_pool) < 0.1:
                return float(max_hit)

            # Refine using iterative method
            for _ in range(10):  # Max 10 iterations
                reduction = self.calculate_physical_damage_reduction(max_hit, context)
                damage_taken = max_hit * (1.0 - reduction)
                if abs(damage_taken - total_pool) < 0.01:
                    break
                # Adjust max_hit
                max_hit = total_pool / (1.0 - reduction)

            return float(max_hit)

        elif damage_type in (
            DamageType.FIRE.value,
            DamageType.COLD.value,
            DamageType.LIGHTNING.value,
            DamageType.CHAOS.value,
        ):
            # Elemental/Chaos damage with resistance
            resistance_stat = f"{damage_type}Resistance"
            resistance = float(
                self.modifiers.calculate_stat(resistance_stat, 0.0, context)
            )

            # Resistance is capped at 75% by default, but can be overcapped
            resistance = min(resistance, 75.0) / 100.0

            # Maximum hit = TotalPool / (1 - Resistance)
            return float(total_pool / (1.0 - resistance))

        return total_pool

    def calculate_effective_health_pool(
        self, context: dict[str, Any] | None = None
    ) -> float:
        """
        Compute the effective health pool (EHP) by combining life, energy
        shield, and average elemental resistances.

        Calculates base pool as life + energy shield, then averages
        Fire/Cold/Lightning/Chaos resistances (each capped at 75% before
        averaging) and scales the base pool by 1 / (1 - average_resistance).
        If the averaged resistance is greater than or equal to 100%, a
        reasonable cap (base_pool * 10) is returned.

        Parameters:
            context (dict[str, Any] | None): Optional calculation context
                with temporary overrides for modifiers.

        Returns:
            float: The effective health pool.
        """
        if context is None:
            context = {}

        # Get base pool
        life = self.calculate_life(context)
        es = self.calculate_energy_shield(context)
        base_pool = life + es

        # Get average resistances (for mixed damage)
        fire_res = (
            min(self.modifiers.calculate_stat("FireResistance", 0.0, context), 75.0)
            / 100.0
        )
        cold_res = (
            min(self.modifiers.calculate_stat("ColdResistance", 0.0, context), 75.0)
            / 100.0
        )
        lightning_res = (
            min(
                self.modifiers.calculate_stat("LightningResistance", 0.0, context), 75.0
            )
            / 100.0
        )
        chaos_res = (
            min(self.modifiers.calculate_stat("ChaosResistance", 0.0, context), 75.0)
            / 100.0
        )

        avg_resistance = (fire_res + cold_res + lightning_res + chaos_res) / 4.0

        # EHP = BasePool / (1 - AverageResistance)
        if avg_resistance >= 1.0:
            # Cap at reasonable value if resistance >= 100%
            ehp = base_pool * 10.0
        else:
            ehp = base_pool / (1.0 - avg_resistance)

        return ehp

    def calculate_life_regen(self, context: dict[str, Any] | None = None) -> float:
        """Calculate life regeneration per second.

        :param context: Current calculation context.
        :return: Life regeneration per second.
        """
        if context is None:
            context = {}

        # Base regen from modifiers
        base_regen = self.modifiers.calculate_stat("LifeRegen", 0.0, context)

        # Percentage-based regen (e.g., "X% of Life regenerated per second")
        life = self.calculate_life(context)
        percent_regen = self.modifiers.calculate_stat("LifeRegenPercent", 0.0, context)
        percent_regen_value = life * (percent_regen / 100.0)

        return base_regen + percent_regen_value

    def calculate_mana_regen(self, context: dict[str, Any] | None = None) -> float:
        """
        Compute mana regenerated per second by summing flat `ManaRegen`
        and percentage-based `ManaRegenPercent` applied to total mana.

        Parameters:
            context (dict[str, Any] | None): Calculation context used for
                modifier lookups; defaults to an empty dict.

        Returns:
            Mana regeneration per second.
        """
        if context is None:
            context = {}

        # Base regen from modifiers
        base_regen = self.modifiers.calculate_stat("ManaRegen", 0.0, context)

        # Percentage-based regen
        mana = self.calculate_mana(context)
        percent_regen = self.modifiers.calculate_stat("ManaRegenPercent", 0.0, context)
        percent_regen_value = mana * (percent_regen / 100.0)

        return base_regen + percent_regen_value

    def calculate_energy_shield_regen(
        self, context: dict[str, Any] | None = None
    ) -> float:
        """
        Compute energy shield regeneration per second as the sum of flat
        regeneration and percent-based regeneration of current energy
        shield.

        Returns:
            Energy shield regeneration per second.
        """
        if context is None:
            context = {}

        # Base regen from modifiers
        base_regen = self.modifiers.calculate_stat("EnergyShieldRegen", 0.0, context)

        # Percentage-based regen
        es = self.calculate_energy_shield(context)
        percent_regen = self.modifiers.calculate_stat(
            "EnergyShieldRegenPercent", 0.0, context
        )
        percent_regen_value = es * (percent_regen / 100.0)

        return base_regen + percent_regen_value

    def calculate_leech_rates(
        self, context: dict[str, Any] | None = None
    ) -> dict[str, float]:
        """
        Compute per-second leech rates for life, mana, and energy shield,
        applying per-second caps.

        Parameters:
            context (dict[str, Any] | None): Optional calculation context
                used when resolving modifiers.

        Returns:
            dict[str, float]: Mapping with keys:
                - "life_leech_rate": life leech amount per second (capped
                    at the life leech cap).
                - "mana_leech_rate": mana leech amount per second (capped
                    at the mana leech cap).
                - "energy_shield_leech_rate": energy shield leech amount
                    per second (capped at the ES leech cap).
        """
        if context is None:
            context = {}

        # Get leech rate modifiers
        life_leech_rate = self.modifiers.calculate_stat(
            "LifeLeechRatePerHit", 0.0, context
        )
        mana_leech_rate = self.modifiers.calculate_stat(
            "ManaLeechRatePerHit", 0.0, context
        )
        es_leech_rate = self.modifiers.calculate_stat(
            "EnergyShieldLeechRatePerHit", 0.0, context
        )

        # Leech is capped at 10% of maximum per second (default)
        # But can be modified by "X% of Maximum Life/Mana/ES per second to Maximum"
        life = self.calculate_life(context)
        mana = self.calculate_mana(context)
        es = self.calculate_energy_shield(context)

        # Calculate leech caps
        life_leech_cap = life * 0.10  # 10% per second default
        mana_leech_cap = mana * 0.10
        es_leech_cap = es * 0.10

        # Apply leech cap modifiers
        life_leech_cap_mult = (
            self.modifiers.calculate_stat("LifeLeechCapMultiplier", 100.0, context)
            / 100.0
        )
        mana_leech_cap_mult = (
            self.modifiers.calculate_stat("ManaLeechCapMultiplier", 100.0, context)
            / 100.0
        )
        es_leech_cap_mult = (
            self.modifiers.calculate_stat(
                "EnergyShieldLeechCapMultiplier", 100.0, context
            )
            / 100.0
        )

        life_leech_cap *= life_leech_cap_mult
        mana_leech_cap *= mana_leech_cap_mult
        es_leech_cap *= es_leech_cap_mult

        return {
            "life_leech_rate": min(life_leech_rate, life_leech_cap),
            "mana_leech_rate": min(mana_leech_rate, mana_leech_cap),
            "energy_shield_leech_rate": min(es_leech_rate, es_leech_cap),
        }

    def calculate_all_defenses(
        self, context: dict[str, Any] | None = None
    ) -> DefenseStats:
        """
        Aggregate all defensive statistics into a DefenseStats instance.

        Parameters:
            context (dict[str, Any] | None): Optional calculation context
                used when querying modifiers; defaults to an empty dict.

        Returns:
            DefenseStats: Populated with life, mana, energy_shield, armour,
                evasion, block_chance, spell_block_chance,
                spell_suppression_chance, fire_resistance, cold_resistance,
                lightning_resistance, and chaos_resistance.
        """
        if context is None:
            context = {}

        return DefenseStats(
            life=self.calculate_life(context),
            mana=self.calculate_mana(context),
            energy_shield=self.calculate_energy_shield(context),
            armour=self.calculate_armour(context),
            evasion=self.calculate_evasion(context),
            block_chance=self.modifiers.calculate_stat("BlockChance", 0.0, context),
            spell_block_chance=self.modifiers.calculate_stat(
                "SpellBlockChance", 0.0, context
            ),
            spell_suppression_chance=self.modifiers.calculate_stat(
                "SpellSuppressionChance", 0.0, context
            ),
            fire_resistance=self.modifiers.calculate_stat(
                "FireResistance", 0.0, context
            ),
            cold_resistance=self.modifiers.calculate_stat(
                "ColdResistance", 0.0, context
            ),
            lightning_resistance=self.modifiers.calculate_stat(
                "LightningResistance", 0.0, context
            ),
            chaos_resistance=self.modifiers.calculate_stat(
                "ChaosResistance", 0.0, context
            ),
        )

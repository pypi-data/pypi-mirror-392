from dataclasses import dataclass

__all__ = ["Stats"]


@dataclass
class Stats:
    """Stats(*args)
    Class that holds character stat-sheet data.

    :param average_hit: Average hit damage.
    :param average_damage: Average hit damage after accuracy check.
    :param cast_speed: Spell cast speed.
    :param attack_speed: Attack speed.
    :param trap_throwing_speed: Trap throwing speed.
    :param trap_cooldown: Trap throwing cooldown.
    :param mine_laying_speed: Mine laying speed.
    :param totem_placement_speed: Totem placement speed.
    :param pre_effective_crit_chance:
        Crit chance as displayed in-game (doesn't factor in accuracy and luck).
    :param crit_chance: Effective crit chance, factors in accuracy and luck.
    :param crit_multiplier: Critical strike multiplier.
    :param hit_chance: Chance to hit with attacks.
    :param total_dps: Total Damage per second.
    :param total_dot: Total damage over time (per second).
    :param bleed_dps: Bleeding damage per second.
    :param ignite_dps: Ignite damage per second.
    :param ignite_damage: Ignite hit damage.
    :param total_dps_with_ignite: Total damage per second including ignite damage.
    :param average_damage_with_ignite: Average hit damage including ignite.
    :param poison_dps: Poison damage per second.
    :param poison_damage: Poison hit damage.
    :param total_dps_with_poison: Total damage per second including poison damage.
    :param average_damage_with_poison: Average hit damage including poison.
    :param decay_dps: Decay damage per second.
    :param skill_cooldown: Skill cooldown time.
    :param area_of_effect_radius: Area of effect radius.
    :param mana_cost: Mana cost of skill.
    :param mana_cost_per_second: Mana cost per second.
    :param strength: Strength attribute.
    :param strength_required: Required strength.
    :param dexterity: Dexterity attribute.
    :param dexterity_required: Required dexterity.
    :param intelligence: Intelligence attribute.
    :param intelligence_required: Intelligence required.
    :param life: Life points.
    :param life_increased: Percent increased life.
    :param life_unreserved: Unreserved life points.
    :param life_unreserved_percent: Percent unreserved life.
    :param life_regen: Flat life regeneration.
    :param life_leech_rate_per_hit: Percent life leeched per hit.
    :param life_leech_gain_per_hit: Flat life leeched per hit.
    :param mana: Mana points.
    :param mana_increased: Percent increased mana.
    :param mana_unreserved: Unreserved mana points.
    :param mana_unreserved_percent: Percent unreserved mana.
    :param mana_regen: Flat mana regeneration.
    :param mana_leech_rate_per_hit: Percent mana leeched per hit.
    :param mana_leech_gain_per_hit: Flat mana leeched per hit.
    :param total_degen: Total life degeneration.
    :param net_life_regen: Net life regeneration.
    :param net_mana_regen: Net mana regeneration.
    :param energy_shield: Energy shield.
    :param energy_shield_increased: Percent increased energy shield.
    :param energy_shield_regen: Flat energy shield regeneration.
    :param energy_shield_leech_rate_per_hit: Percent energy shield leeched per hit.
    :param energy_shield_leech_gain_per_hit: Flat energy shield leeched per hit.
    :param evasion: Evasion rating.
    :param evasion_increased: Percent increased evasion rating.
    :param melee_evade_chance: Chance to evade melee attacks.
    :param projectile_evade_chance: Chance to evade projectiles.
    :param armour: Armour.
    :param armour_increased: Percent increased armour.
    :param physical_damage_reduction: Physical damage reduction.
    :param effective_movement_speed_modifier: Effective movement speed modifier.
    :param block_chance: Chance to block attacks.
    :param spell_block_chance: Chance to block spells.
    :param spell_suppression_chance: Chance to suppress spell damage.
    :param attack_dodge_chance: Chance to dodge attacks.
    :param spell_dodge_chance: Chance to dodge spells.
    :param fire_resistance: Fire resistance.
    :param cold_resistance: Cold resistance.
    :param lightning_resistance: Lightning resistance.
    :param chaos_resistance: Chaos resistance.
    :param fire_resistance_over_cap: Overcapped fire resistance.
    :param cold_resistance_over_cap: Overcapped cold resistance
    :param lightning_resistance_over_cap: Overcapped lightning resistance.
    :param chaos_resistance_over_cap: Overcapped chaos resistance.
    :param power_charges: Power charges.
    :param power_charges_maximum: Maximum power charges.
    :param frenzy_charges: Frenzy charges.
    :param frenzy_charges_maximum: Maximum frenzy charges.
    :param endurance_charges: Endurance charges.
    :param endurance_charges_maximum: Maximum endurance charges.
    :param active_totem_limit: Maximum active totems.
    :param active_minion_limit: Maximum number of minions.
    :param rage: Current rage value.
    :param physical_maximum_hit_taken: Maximum physical hit that can be taken.
    :param fire_maximum_hit_taken: Maximum fire hit that can be taken.
    :param cold_maximum_hit_taken: Maximum cold hit that can be taken.
    :param lightning_maximum_hit_taken: Maximum lightning hit that can be taken.
    :param chaos_maximum_hit_taken: Maximum chaos hit that can be taken.
    :param total_effective_health_pool: Total effective health pool (EHP)."""

    average_hit: float | None = None
    average_damage: float | None = None
    cast_speed: float | None = None
    attack_speed: float | None = None
    trap_throwing_speed: float | None = None
    trap_cooldown: float | None = None
    mine_laying_speed: float | None = None
    totem_placement_speed: float | None = None
    pre_effective_crit_chance: float | None = None
    crit_chance: float | None = None
    crit_multiplier: float | None = None
    hit_chance: int | None = None
    total_dps: float | None = None
    total_dot: float | None = None
    bleed_dps: float | None = None
    ignite_dps: float | None = None
    ignite_damage: float | None = None
    total_dps_with_ignite: float | None = None
    average_damage_with_ignite: float | None = None
    poison_dps: float | None = None
    poison_damage: float | None = None
    total_dps_with_poison: float | None = None
    average_damage_with_poison: float | None = None
    decay_dps: float | None = None
    skill_cooldown: float | None = None
    area_of_effect_radius: float | None = None
    mana_cost: float | None = None
    mana_cost_per_second: float | None = None
    strength: float | None = None
    strength_required: float | None = None
    dexterity: float | None = None
    dexterity_required: float | None = None
    intelligence: float | None = None
    intelligence_required: float | None = None
    life: float | None = None
    life_increased: float | None = None
    life_unreserved: float | None = None
    life_unreserved_percent: float | None = None
    life_regen: float | None = None
    life_leech_rate_per_hit: float | None = None
    life_leech_gain_per_hit: float | None = None
    mana: float | None = None
    mana_increased: float | None = None
    mana_unreserved: float | None = None
    mana_unreserved_percent: float | None = None
    mana_regen: float | None = None
    mana_leech_rate_per_hit: float | None = None
    mana_leech_gain_per_hit: float | None = None
    total_degen: float | None = None
    net_life_regen: float | None = None
    net_mana_regen: float | None = None
    energy_shield: float | None = None
    energy_shield_increased: float | None = None
    energy_shield_regen: float | None = None
    energy_shield_leech_rate_per_hit: float | None = None
    energy_shield_leech_gain_per_hit: float | None = None
    evasion: float | None = None
    evasion_increased: float | None = None
    melee_evade_chance: float | None = None
    projectile_evade_chance: float | None = None
    armour: float | None = None
    armour_increased: float | None = None
    physical_damage_reduction: float | None = None
    effective_movement_speed_modifier: float | None = None
    block_chance: float | None = None
    spell_block_chance: float | None = None
    spell_suppression_chance: float | None = None
    attack_dodge_chance: float | None = None
    spell_dodge_chance: float | None = None
    fire_resistance: float | None = None
    cold_resistance: float | None = None
    lightning_resistance: float | None = None
    chaos_resistance: float | None = None
    fire_resistance_over_cap: float | None = None
    cold_resistance_over_cap: float | None = None
    lightning_resistance_over_cap: float | None = None
    chaos_resistance_over_cap: float | None = None
    power_charges: float | None = None
    power_charges_maximum: float | None = None
    frenzy_charges: float | None = None
    frenzy_charges_maximum: float | None = None
    endurance_charges: float | None = None
    endurance_charges_maximum: float | None = None
    active_totem_limit: float | None = None
    active_minion_limit: float | None = None
    rage: float | None = None
    physical_maximum_hit_taken: float | None = None
    fire_maximum_hit_taken: float | None = None
    cold_maximum_hit_taken: float | None = None
    lightning_maximum_hit_taken: float | None = None
    chaos_maximum_hit_taken: float | None = None
    total_effective_health_pool: float | None = None

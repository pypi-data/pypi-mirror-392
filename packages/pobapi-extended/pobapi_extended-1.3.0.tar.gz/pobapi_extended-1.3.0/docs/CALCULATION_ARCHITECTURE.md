# Path of Building Calculation Architecture

## Overview

This document explains how Path of Building performs calculations and how our API extracts the calculated results.

## How Path of Building Calculates Data

Path of Building is a Lua-based application that performs comprehensive calculations for Path of Exile builds. The calculation engine is located in the [PathOfBuildingCommunity/PathOfBuilding](https://github.com/PathOfBuildingCommunity/PathOfBuilding) repository.

### Calculation Process in Path of Building

1. **Input Collection**: PoB collects data from:
   - Passive skill tree (allocated nodes)
   - Items (equipped gear with all modifiers)
   - Skills and support gems
   - Configuration settings (enemy level, conditions, buffs, etc.)
   - Keystones and notable passives

2. **Modifier Processing**: PoB processes all modifiers in a specific order:
   - Base stats from character class
   - Passive tree modifiers
   - Item modifiers
   - Skill gem modifiers
   - Support gem modifiers
   - Configuration modifiers (auras, buffs, curses, etc.)

3. **Calculation Engine**: The Lua calculation engine:
   - Applies "increased" and "more" modifiers correctly
   - Handles multiplicative and additive bonuses
   - Calculates DPS considering:
     - Base damage
     - Attack/cast speed
     - Critical strike chance and multiplier
     - Accuracy and hit chance
     - Damage conversion
     - Damage over time (DoT) effects
   - Calculates defensive stats:
     - Life/Mana/Energy Shield totals
     - Armour and physical damage reduction
     - Evasion and evade chance
     - Resistances and overcapping
     - Block, dodge, and spell suppression
     - Maximum hit taken calculations
     - Effective Health Pool (EHP)

4. **Result Export**: PoB exports calculated results to XML format with `<PlayerStat>` elements containing:
   - Stat name (e.g., "TotalDPS", "Life", "Armour")
   - Calculated value (as a string)

## How Our API Extracts Calculations

Our API **does not perform calculations**. Instead, it extracts **already calculated values** from Path of Building's XML export.

### Extraction Process

1. **XML Parsing**: We parse the XML export from Path of Building
   ```xml
   <Build>
       <PlayerStat stat="TotalDPS" value="927263.0"/>
       <PlayerStat stat="Life" value="3580.0"/>
       <PlayerStat stat="Armour" value="512.0"/>
       <!-- ... more stats ... -->
   </Build>
   ```

2. **Stat Mapping**: We use `STATS_MAP` in `pobapi/constants.py` to map PoB's internal stat names to our API field names:
   ```python
   STATS_MAP = {
       "TotalDPS": "total_dps",
       "Life": "life",
       "Armour": "armour",
       # ... more mappings ...
   }
   ```

3. **Stats Object Building**: `StatsBuilder` in `pobapi/builders.py`:
   - Finds all `<PlayerStat>` elements in the XML
   - Maps stat names using `STATS_MAP`
   - Converts string values to floats
   - Creates a `Stats` dataclass instance with all extracted values

### Example Flow

```python
# 1. Path of Building calculates everything internally (Lua)
# 2. PoB exports to XML with PlayerStat elements
# 3. Our API extracts:

xml = """<Build>
    <PlayerStat stat="TotalDPS" value="927263.0"/>
    <PlayerStat stat="Life" value="3580.0"/>
</Build>"""

# 4. StatsBuilder processes:
build_element = xml.find("Build")
for player_stat in build_element.findall("PlayerStat"):
    stat_name = player_stat.get("stat")  # "TotalDPS"
    stat_value = player_stat.get("value")  # "927263.0"

    # Map to our field name
    field_name = STATS_MAP.get(stat_name)  # "total_dps"

    # Convert and store
    kwargs[field_name] = float(stat_value)

# 5. Create Stats object
stats = Stats(**kwargs)
# stats.total_dps = 927263.0
# stats.life = 3580.0
```

## What We Extract vs. What PoB Calculates

### What Path of Building Calculates (in Lua)

Path of Building performs complex calculations including:

- **DPS Calculations**:
  - Base damage from skills and weapons
  - Damage multipliers from support gems
  - Critical strike calculations
  - Damage conversion (physical → elemental, etc.)
  - Damage over time (ignite, poison, bleed, decay)
  - Combined DPS with all DoT effects

- **Defensive Calculations**:
  - Life/Mana/ES totals with all modifiers
  - Armour and physical damage reduction
  - Evasion and evade chance
  - Block, dodge, spell suppression
  - Resistance calculations and overcapping
  - Maximum hit taken (per damage type)
  - Effective Health Pool (EHP)

- **Speed Calculations**:
  - Attack speed (considering all modifiers)
  - Cast speed
  - Movement speed
  - Trap/mine/totem speeds

- **Resource Calculations**:
  - Mana cost and reservation
  - Life/Mana/ES regeneration
  - Leech rates
  - Net recovery

### What Our API Extracts

Our API extracts **all calculated values** that Path of Building exports:

- ✅ All DPS values (total, DoT, with ignite/poison)
- ✅ All defensive stats (life, armour, evasion, resistances)
- ✅ All speed values (attack, cast, movement)
- ✅ All resource values (mana cost, regen, leech)
- ✅ Maximum hit taken calculations
- ✅ Effective Health Pool
- ✅ All attributes and requirements
- ✅ All charges and limits

## Stat Categories

### Offensive Stats
- `total_dps` - Total damage per second
- `average_hit` - Average hit damage
- `average_damage` - Average damage after accuracy
- `crit_chance` - Critical strike chance
- `crit_multiplier` - Critical strike multiplier
- `total_dot` - Total damage over time
- `ignite_dps`, `poison_dps`, `bleed_dps` - DoT types
- `total_dps_with_ignite`, `total_dps_with_poison` - Combined DPS

### Defensive Stats
- `life`, `mana`, `energy_shield` - Resource pools
- `armour`, `evasion` - Defense ratings
- `physical_damage_reduction` - Physical mitigation
- `block_chance`, `spell_block_chance` - Block chances
- `spell_suppression_chance` - Spell suppression
- `melee_evade_chance`, `projectile_evade_chance` - Evade chances
- `fire_resistance`, `cold_resistance`, `lightning_resistance`, `chaos_resistance` - Resistances
- `*_resistance_over_cap` - Overcapped resistances

### Defensive Calculations (Situational)
- `physical_maximum_hit_taken` - Max physical hit survivable
- `fire_maximum_hit_taken` - Max fire hit survivable
- `cold_maximum_hit_taken` - Max cold hit survivable
- `lightning_maximum_hit_taken` - Max lightning hit survivable
- `chaos_maximum_hit_taken` - Max chaos hit survivable
- `total_effective_health_pool` - Total EHP

### Speed Stats
- `attack_speed` - Attacks per second
- `cast_speed` - Casts per second
- `trap_throwing_speed` - Trap throwing time
- `mine_laying_speed` - Mine laying time
- `totem_placement_speed` - Totem placement time
- `effective_movement_speed_modifier` - Movement speed multiplier

### Resource Stats
- `mana_cost` - Mana cost per use
- `mana_cost_per_second` - Mana cost per second
- `life_regen`, `mana_regen`, `energy_shield_regen` - Regeneration
- `life_leech_rate_per_hit`, `mana_leech_rate_per_hit` - Leech rates
- `life_unreserved`, `mana_unreserved` - Unreserved amounts
- `life_unreserved_percent`, `mana_unreserved_percent` - Unreserved percentages

## Configuration Impact on Calculations

Path of Building's calculations depend heavily on configuration settings:

- **Enemy Level**: Affects monster stats, resistance penalties
- **Conditions**: Stationary, moving, full life, low life, etc.
- **Buffs**: Onslaught, fortify, phasing, etc.
- **Curses**: Applied curses affect enemy resistances
- **Charges**: Power, frenzy, endurance charges
- **Situational**: Hit recently, killed recently, etc.

All these settings are extracted via the `Config` object and affect what values Path of Building calculates and exports.

## Key Points

1. **We don't calculate**: Our API extracts pre-calculated values from PoB's XML export
2. **PoB does all calculations**: The Lua engine in Path of Building performs all complex calculations
3. **Complete extraction**: We extract all calculated stats that PoB exports
4. **Configuration matters**: Different config settings produce different calculated values
5. **Real-time accuracy**: Values reflect the exact state of the build in Path of Building

## References

- [Path of Building GitHub Repository](https://github.com/PathOfBuildingCommunity/PathOfBuilding)
- [Path of Building Website](https://pathofbuilding.community)
- Our API's `STATS_MAP` in `pobapi/constants.py` shows all extractable stats
- Our `StatsBuilder` in `pobapi/builders.py` shows the extraction process

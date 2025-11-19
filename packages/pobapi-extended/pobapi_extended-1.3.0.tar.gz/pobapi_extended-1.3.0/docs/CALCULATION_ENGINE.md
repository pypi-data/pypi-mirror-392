# Path of Building Calculation Engine (Python Port)

## Overview

This document describes the Python-based calculation engine that replicates Path of Building's Lua calculation system. This is a work-in-progress port that aims to provide identical calculations to Path of Building.

## Architecture

The calculation engine is organized into several modules:

### Core Modules

1. **`pobapi.calculator.modifiers`** - Modifier System
   - Handles parsing and applying modifiers
   - Supports all modifier types: flat, increased, more, less, base, multiplier, flag
   - Applies modifiers in correct order (matching PoB)

2. **`pobapi.calculator.damage`** - Damage Calculator
   - Calculates base damage from skills/weapons
   - Handles damage conversion
   - Handles "extra damage" modifiers (e.g., X% of Physical as Extra Fire)
   - Calculates DPS with crits, accuracy, etc.
   - Handles damage over time (DoT)
   - Calculates damage against enemy with resistances and penetration

3. **`pobapi.calculator.defense`** - Defense Calculator
   - Calculates Life/Mana/Energy Shield
   - Calculates Armour and physical damage reduction
   - Calculates Evasion and evade chance
   - Calculates Maximum Hit Taken
   - Calculates Effective Health Pool (EHP)
   - Calculates regeneration and leech

4. **`pobapi.calculator.resource`** - Resource Calculator
   - Calculates mana cost and reservation
   - Calculates unreserved resources
   - Calculates net recovery

5. **`pobapi.calculator.skill_stats`** - Skill Stats Calculator
   - Calculates Area of Effect radius
   - Calculates projectile count and speed
   - Calculates skill cooldowns

6. **`pobapi.calculator.engine`** - Main Calculation Engine
   - Orchestrates all calculations
   - Loads modifiers from all sources
   - Produces final Stats object

### Parser Modules

7. **`pobapi.calculator.item_modifier_parser`** - Item Modifier Parser
   - Parses item text to extract modifiers
   - Supports many modifier patterns (see below)

8. **`pobapi.calculator.passive_tree_parser`** - Passive Tree Parser
   - Parses passive tree nodes
   - Handles keystone effects (20+ keystones)
   - Supports jewel sockets

9. **`pobapi.calculator.skill_modifier_parser`** - Skill Modifier Parser
   - Parses skill gems and support gems
   - Supports 30+ support gems with their effects
   - Handles gem level scaling

10. **`pobapi.calculator.config_modifier_parser`** - Config Modifier Parser
    - Parses configuration settings
    - Handles buffs (Onslaught, Fortify, Tailwind, Adrenaline)
    - Handles auras (Hatred, Anger, Wrath, Haste, Grace, Determination, Discipline)
    - Handles curses (Flammability, Frostbite, Conductivity, Enfeeble, Vulnerability)
    - Handles charges (Power, Frenzy, Endurance)
    - Handles conditions (On Full Life, On Low Life, etc.)

## Current Status

### ✅ Implemented

- **Modifier System**: Complete modifier system (flat, increased, more, less, base, multiplier, flag)
- **Damage Calculations**:
  - Base damage calculations
  - Damage conversion
  - "Extra damage" modifiers (X% of Physical as Extra Fire, etc.)
  - DPS with crits, accuracy, hit chance
  - DoT calculations (Ignite, Poison, Bleed, Decay)
  - Total DPS with DoT
  - Damage against enemy with resistances and penetration
- **Defensive Calculations**:
  - Life/Mana/Energy Shield totals
  - Physical damage reduction (accurate formula)
  - Evasion and evade chance
  - Maximum hit taken (all damage types, with accurate physical calculation)
  - Effective Health Pool (EHP)
  - Regeneration (Life, Mana, ES)
  - Leech rates with caps
  - Net recovery calculations
- **Resource Calculations**:
  - Mana cost (per use and per second)
  - Life/Mana reservation
  - Unreserved resources
  - Net recovery
- **Skill Stats**:
  - Area of Effect radius
  - Projectile count and speed
  - Skill cooldowns
  - Trap/Mine/Totem speeds
- **Parsers**:
  - Item modifier parser (extended with many patterns, including conditional modifiers)
  - Unique item parser (special effects for unique items)
  - Passive tree parser (with keystone support for 20+ keystones)
  - Skill modifier parser (30+ support gems)
  - Config modifier parser (buffs, auras, curses, charges, conditions)
- **Conditional Modifiers**: Full support for conditional modifiers (on_full_life, on_low_life, enemy conditions, etc.)
- **Per-Attribute Modifiers**: Support for modifiers that scale with attributes (e.g., "1% increased Damage per 10 Strength")
- **Penetration & Resistance Reduction**: Accurate calculation of penetration and resistance reduction with proper order of operations
- **Integration**: Full integration with CalculationEngine
- **Enemy Configuration**: Support for enemy resistances and physical damage reduction

### ✅ Completed

- ✅ Full passive tree node data loading from game files (via `GameDataLoader.load_passive_tree_data()`)
- ✅ Full skill gem data loading from game files (via `GameDataLoader.load_skill_gem_data()`)
- ✅ Full unique item data loading from game files (via `GameDataLoader.load_unique_item_data()`)
- ✅ Expansion of unique item database to 100+ items (29 base + 84 extended)
- ✅ Complete jewel socket integration in CalculationEngine
- ✅ Proper item_id to items mapping for jewel sockets

### ❌ Not Yet Implemented

- Complete passive tree node data from game files
- Complete skill gem data from game files
- Support gem data from game files
- Unique item effects
- Complete keystone effects
- All edge cases and special mechanics
- Full configuration system integration

## Usage

```python
from pobapi import PathOfBuildingAPI, CalculationEngine
from pobapi import from_import_code

# Load build
build = from_import_code(import_code)

# Create calculation engine
engine = CalculationEngine()

# Load build data into engine
engine.load_build(build)

# Calculate stats with context
context = {
    "base_life": 100.0,
    "base_mana": 50.0,
    "base_energy_shield": 0.0,
    "base_armour": 0.0,
    "base_evasion": 0.0,
    "enemy_fire_resist": 0.0,
    "enemy_cold_resist": 0.0,
    "enemy_lightning_resist": 0.0,
    "enemy_chaos_resist": 0.0,
}
stats = engine.calculate_all_stats(context, build_data=build)
```

## Item Modifier Parser

The `ItemModifierParser` currently supports these patterns:

- `+X to Y` - Flat modifiers
- `X% increased Y` - Increased modifiers
- `X% more Y` - More modifiers
- `X% reduced Y` - Reduced modifiers
- `X% less Y` - Less modifiers
- `Adds X to Y Z Damage` - Added damage
- `X to Y Z Damage` - Base damage (weapons)
- `+X to maximum Y` - Maximum stat modifiers
- `X% of Y converted to Z` - Damage conversion
- `+X to all Y` - All resistances, etc.
- `X% to all Y` - Percentage to all
- `X% chance to Y` - Chance modifiers
- `X% chance to Y when Z` - Conditional chance modifiers
- `X% chance to Y on Z` - Conditional chance modifiers
- `X% chance to Y if Z` - Conditional chance modifiers
- `Socketed gems have X` - Socketed modifiers
- `X% increased Y per Z` - Per-attribute modifiers (e.g., "1% increased Damage per 10 Strength")
- `X per Y` - Per-level/per-charge modifiers

**Unique Items**: The engine also supports parsing unique item effects through `UniqueItemParser`, which handles special mechanics for unique items. Currently supports **100+ unique items** (29 base + 84 extended) including:

**Popular Build-Enabling Uniques:**
- Headhunter / Replica Headhunter (mod stealing)
- Mageblood (flask effects always active)
- The Squire (support gems for shield)
- Ashes of the Stars (gem quality)
- Watcher's Eye (aura-specific mods)
- Forbidden Shako (random support gems)

**Defensive Uniques:**
- Shavronne's Wrappings (chaos damage doesn't bypass ES)
- The Brass Dome (+5% max resistances)
- Aegis Aurora (ES on block)
- The Ivory Tower (mana to ES conversion)
- Atziri's Reflection (reflects curses)

**Offensive Uniques:**
- Crown of Eyes (spell damage applies to attacks)
- Starforge (physical damage can shock)
- Voidforge (physical to random element)
- Original Sin (all damage is chaos)
- The Eternity Shroud (shaper item scaling)

**Utility Uniques:**
- The Adorned (jewel effect scaling)
- The Taming (elemental damage and speed)
- The Three Dragons (damage type ailment changes)
- The Perfect Form (evasion and resistances)
- And many more...

More patterns can be added as needed.

## Support Gems

The `SkillModifierParser` supports 30+ support gems including:

- **Damage**: Added Fire Damage, Elemental Focus, Controlled Destruction, Melee Physical, Brutality
- **Speed**: Faster Attacks, Faster Casting, Multistrike, Spell Echo
- **Projectiles**: GMP, LMP, Vicious Projectiles
- **Crit**: Increased Critical Strikes, Increased Critical Damage
- **DoT**: Deadly Ailments, Unbound Ailments
- **Conditional**: Hypothermia, Immolate, Shock
- **Utility**: Inspiration, Infused Channelling, Concentrated Effect, Intensify
- **Awakened**: Awakened Added Fire, Awakened Elemental Focus

## Keystones

The `PassiveTreeParser` supports 20+ keystones including:

- Acrobatics, Chaos Inoculation, Iron Reflexes, Elemental Overload
- Pain Attunement, Mind Over Matter, Blood Magic, Resolute Technique
- Unwavering Stance, Vaal Pact, Ghost Reaver, Zealot's Oath
- Ancestral Bond, Avatar of Fire, Point Blank, Phase Acrobatics
- Arrow Dancing, Eldritch Battery, Elemental Equilibrium, Perfect Agony, Crimson Dance

## Penetration & Resistance Reduction

The `PenetrationCalculator` handles penetration and resistance reduction mechanics:

- **Resistance Reduction**: Applied first (e.g., from curses like Flammability)
- **Penetration**: Applied after reduction (e.g., from support gems, passives)
- **Order of Operations**:
  1. Base resistance (e.g., 75%)
  2. Apply resistance reduction (e.g., -44% from curse)
  3. Apply penetration (e.g., -37% from support gem)
  4. Cap at -200% minimum

The calculator correctly applies these mechanics in `DamageCalculator.calculate_damage_against_enemy()`.

## Per-Attribute Modifiers

The engine now supports modifiers that scale with attributes:

- **"X% increased Y per Z Strength/Dexterity/Intelligence"**: Automatically calculated based on current attribute values
- **Attribute Context**: Attributes are calculated early and added to context for "per attribute" calculations
- **Dynamic Calculation**: Modifiers are recalculated based on current attribute values

## Notes

This is a **massive undertaking**. Path of Building's calculation engine contains:
- 50,000+ lines of Lua code
- Hundreds of unique item effects
- Thousands of passive tree nodes
- Complex modifier interactions
- Many edge cases and special rules

**Current approach**: The engine structure is in place with extended parsers. Full implementation will require:
1. Detailed study of PoB's Lua code
2. Parsing of game data files (nodes.json, gems, etc.)
3. Implementation of all mechanics
4. Extensive testing and validation

**Recommendation**: For production use, continue using Path of Building's XML export (current approach) until the Python engine reaches feature parity.

## Example Usage

See `utils/example_calculation_engine.py` for a complete example of how to use the calculation engine.

Basic usage:

```python
from pobapi import CalculationEngine, from_import_code

# Load build
build = from_import_code(import_code)

# Create and initialize engine
engine = CalculationEngine()
engine.load_build(build)

# Calculate stats
context = {
    "base_life": 100.0,
    "base_mana": 50.0,
    # ... more context ...
}
stats = engine.calculate_all_stats(context, build_data=build)
```

## Conditional Modifiers

The engine supports conditional modifiers that depend on game state:

- **Life-based**: `on_full_life`, `on_low_life` (35% threshold)
- **Mana-based**: `on_full_mana`, `on_low_mana`
- **Energy Shield-based**: `on_full_energy_shield`, `on_low_energy_shield`
- **Enemy conditions**: `enemy_is_shocked`, `enemy_is_frozen`, `enemy_is_ignited`, `enemy_is_chilled`, `enemy_is_poisoned`
- **Distance**: `projectile_distance` (close/medium/far)

Conditions are evaluated by the `ConditionEvaluator` class and can be set in the calculation context.

## References

- [Path of Building Repository](https://github.com/PathOfBuildingCommunity/PathOfBuilding)
- [Path of Building Calculation Architecture](./CALCULATION_ARCHITECTURE.md)

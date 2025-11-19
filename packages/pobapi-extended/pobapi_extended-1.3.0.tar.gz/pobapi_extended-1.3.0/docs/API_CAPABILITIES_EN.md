# Path of Building API - Capabilities

## What can be extracted from import code

### 1. Basic build information
- **Character class** (`class_name`): Witch, Ranger, Duelist, etc.
- **Ascendancy** (`ascendancy_name`): Elementalist, Deadeye, etc.
- **Level** (`level`): 1-100
- **Bandit choice** (`bandit`): None, Alira, Oak, Kraityn

### 2. Character statistics (`stats`)
- Life
- Mana
- Energy Shield
- Armour
- Evasion
- Total DPS (total damage per second)
- Average Hit (average damage per hit)
- And many other statistics (over 100 fields)

### 3. Build configuration (`config`)
- Enemy Level
- Resistance Penalty
- Stationary (whether enemy is stationary)
- And many other settings (over 200 fields)

### 4. Skill groups (`skill_groups`)
For each group:
- Enabled (whether enabled)
- Label
- Active (index of active skill)
- Abilities (list of abilities):
  - Name
  - Level
  - Quality (for gems)
  - Support (whether it's a support gem)
  - Enabled (whether enabled)

### 5. Active skill (`active_skill`)
- Main skill name
- Level
- Quality
- Whether it's a support gem

### 6. Items (`items`)
For each item:
- Name
- Base (base type)
- Rarity (Normal, Magic, Rare, Unique)
- Item Level
- Quality
- Sockets
- Text (full item text with modifiers)

### 7. Passive skill tree (`trees`)
For each tree:
- URL (pathofexile.com link)
- Nodes (list of node IDs)
- Sockets (jewel socket locations)

### 8. Keystones (`keystones`)
- List of keystone names

### 9. Item sets (`item_sets`)
For each item set:
- Weapon slots (weapon1, weapon2, weapon1_swap, weapon2_swap)
- Armour slots (helmet, body_armour, gloves, boots)
- Accessory slots (amulet, ring1, ring2, belt)
- Flask slots (flask1-5)

### 10. Build notes (`notes`)
- Author's notes and comments

## Usage examples

### Basic usage

```python
from pobapi import from_url

# Load build from pastebin URL
build = from_url("https://pastebin.com/...")

# Access basic information
print(f"Class: {build.class_name}")
print(f"Level: {build.level}")
print(f"Life: {build.stats.life}")

# Access items
for item in build.items:
    print(f"{item.name}: {item.base}")

# Access skill groups
for group in build.skill_groups:
    print(f"Group: {group.label}")
    for ability in group.abilities:
        print(f"  - {ability.name} (Level {ability.level})")
```

### Using calculation engine

```python
from pobapi import from_url
from pobapi.calculator.engine import CalculationEngine

# Load build
build = from_url("https://pastebin.com/...")

# Create calculation engine
engine = CalculationEngine()

# Load build data
engine.load_build(build)

# Calculate all stats
stats = engine.calculate_all_stats(build_data=build)

# Access calculated stats
print(f"Total DPS: {stats.total_dps}")
print(f"Life: {stats.life}")
print(f"Armour: {stats.armour}")
```

### Modifying builds

```python
from pobapi import from_url, models
from pobapi.types import ItemSlot, PassiveNodeID

# Load build
build = from_url("https://pastebin.com/...")

# Add passive tree node
build.add_node(PassiveNodeID.ELEMENTAL_EQUILIBRIUM)

# Equip an item
item = models.Item(
    rarity="Rare",
    name="Test Helmet",
    base="Iron Helmet",
    uid="",
    shaper=False,
    elder=False,
    crafted=False,
    quality=None,
    sockets=None,
    level_req=1,
    item_level=80,
    implicit=None,
    text="+50 to maximum Life",
)
build.equip_item(item, ItemSlot.HELMET)

# Add a skill gem
gem = models.Gem(
    name="Fireball",
    level=20,
    quality=0,
    enabled=True,
    support=False,
)
build.add_skill(gem, "Main")

# Export modified build
xml_bytes = build.to_xml()
import_code = build.to_import_code()
```

## API Reference

See the full API documentation at [Read the Docs](https://pobapi.readthedocs.io).

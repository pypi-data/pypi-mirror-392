# Build Creation Capabilities

## Current Status

### ✅ What is ALREADY implemented:

1. **Reading builds:**
   - `PathOfBuildingAPI` - load from XML/import code/URL
   - Parse all build data (items, tree, skills, config)

2. **Data models:**
   - `models.Item` - can create items manually
   - `models.Tree` - can create trees manually
   - `models.Gem` - can create gems manually
   - `models.SkillGroup` - can create skill groups manually
   - `models.Set` - can create item sets manually

3. **Build creation:**
   - ✅ `create_build()` - factory function to create new builds
   - ✅ `BuildBuilder` - fluent interface for building
   - ✅ `set_class()` - set character class and ascendancy
   - ✅ `set_level()` - set character level
   - ✅ `set_bandit()` - set bandit choice
   - ✅ `create_tree()` - create passive skill tree
   - ✅ `allocate_node()` - allocate passive tree nodes
   - ✅ `add_item()` - add items to build
   - ✅ `equip_item()` - equip items in slots
   - ✅ `create_item_set()` - create item sets
   - ✅ `add_skill()` - add skill gems
   - ✅ `build()` - create `PathOfBuildingAPI` instance

4. **Build modification:**
   - ✅ `add_node()` - add passive tree nodes
   - ✅ `remove_node()` - remove passive tree nodes
   - ✅ `equip_item()` - equip items (on existing builds)
   - ✅ `add_skill()` - add skill gems (on existing builds)

5. **Build export:**
   - ✅ `to_xml()` - export to XML format
   - ✅ `to_import_code()` - export to import code format

6. **Calculations:**
   - `CalculationEngine` - accepts build and calculates statistics
   - Can pass any data that matches the interface

7. **Item crafting:**
   - `ItemCraftingAPI` - create items with modifiers
   - Generate item text

## Usage Examples

### Creating a new build from scratch

```python
from pobapi import create_build, models
from pobapi.types import CharacterClass, Ascendancy, ItemSlot, PassiveNodeID

# Create a new build
builder = create_build()

# Set character class and level
builder.set_class(CharacterClass.WITCH, Ascendancy.NECROMANCER)
builder.set_level(90)

# Create passive skill tree
builder.create_tree()

# Allocate passive nodes
builder.allocate_node(PassiveNodeID.MINION_INSTABILITY)
builder.allocate_node(PassiveNodeID.ELEMENTAL_EQUILIBRIUM)

# Create item set
builder.create_item_set()

# Add and equip an item
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
item_index = builder.add_item(item)
builder.equip_item(item_index, ItemSlot.HELMET)

# Add skill gems
gem = models.Gem(
    name="Arc",
    level=20,
    quality=0,
    enabled=True,
    support=False,
)
builder.add_skill(gem, "Main")

# Build the PathOfBuildingAPI instance
build = builder.build()

# Export the build
xml_bytes = build.to_xml()
import_code = build.to_import_code()
```

### Modifying an existing build

```python
from pobapi import from_url
from pobapi.types import PassiveNodeID, ItemSlot

# Load existing build
build = from_url("https://pastebin.com/...")

# Modify the build
build.add_node(PassiveNodeID.ELEMENTAL_EQUILIBRIUM)
build.remove_node(PassiveNodeID.MINION_INSTABILITY)

# Add new item
new_item = models.Item(...)
build.equip_item(new_item, ItemSlot.BELT)

# Add new skill
new_gem = models.Gem(...)
build.add_skill(new_gem, "Auras")

# Export modified build
modified_xml = build.to_xml()
modified_code = build.to_import_code()
```

### Using CalculationEngine with created builds

```python
from pobapi import create_build
from pobapi.calculator.engine import CalculationEngine

# Create build
builder = create_build()
builder.set_class(CharacterClass.WITCH, Ascendancy.NECROMANCER)
builder.set_level(90)
# ... add items, skills, etc.
build = builder.build()

# Calculate stats
engine = CalculationEngine()
engine.load_build(build)
stats = engine.calculate_all_stats(build_data=build)

print(f"Life: {stats.life}")
print(f"DPS: {stats.total_dps}")
```

## BuildBuilder API Reference

### Core Methods

- `set_class(class_name, ascendancy_name=None)` - Set character class and ascendancy
- `set_level(level)` - Set character level (1-100)
- `set_bandit(bandit)` - Set bandit choice (None, "Alira", "Oak", "Kraityn")
- `create_tree()` - Create a new passive skill tree
- `allocate_node(node_id)` - Allocate a passive tree node
- `add_item(item)` - Add an item to the build
- `equip_item(item_index, slot, item_set_index=0)` - Equip an item in a slot
- `create_item_set()` - Create a new empty item set
- `add_skill(gem, group_label="Main")` - Add a skill gem to a group
- `build()` - Create `PathOfBuildingAPI` instance

### PathOfBuildingAPI Modification Methods

- `add_node(node_id, tree_index=0)` - Add a passive tree node
- `remove_node(node_id, tree_index=0)` - Remove a passive tree node
- `equip_item(item, slot, item_set_index=0)` - Equip an item
- `add_skill(gem, group_label="Main")` - Add a skill gem

### Export Methods

- `to_xml()` - Export build to XML bytes
- `to_import_code()` - Export build to import code string

## Validation

The library includes validation for:
- Character class and ascendancy combinations
- Item slot assignments
- Passive tree node IDs
- Skill gem levels and quality
- Build structure integrity

## Limitations

1. **Passive tree URL**: When creating a new tree, you may need to provide a valid passive tree URL from pathofexile.com
2. **Item text generation**: For crafted items, you may need to manually generate the item text
3. **Complex item sockets**: Socket groups may need manual configuration
4. **Build validation**: Some edge cases may not be fully validated

## Future Improvements

- Automatic passive tree URL generation
- Enhanced item text generation
- More comprehensive validation
- Build templates and presets
- Import/export to other formats

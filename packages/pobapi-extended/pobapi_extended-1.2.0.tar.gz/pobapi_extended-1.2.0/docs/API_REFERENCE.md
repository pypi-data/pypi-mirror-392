# Complete API Reference

This document provides a comprehensive reference for all public APIs in the pob-api-extended library.

## Table of Contents

1. [PathOfBuildingAPI](#pathofbuildingapi)
2. [BuildBuilder](#buildbuilder)
3. [BuildModifier](#buildmodifier)
4. [Factory Functions](#factory-functions)
5. [Data Models](#data-models)
6. [Type Definitions](#type-definitions)
7. [Exceptions](#exceptions)
8. [Utilities](#utilities)

---

## PathOfBuildingAPI

The main class for working with Path of Building builds.

### Initialization

```python
PathOfBuildingAPI(xml: bytes | Element, parser: BuildParser | None = None)
```

**Parameters:**
- `xml`: XML content as bytes or lxml Element
- `parser`: Optional custom parser implementation (defaults to `DefaultBuildParser`)

**Raises:**
- `ParsingError`: If XML parsing fails
- `ValidationError`: If XML structure is invalid

**Example:**
```python
from pobapi import PathOfBuildingAPI

# From bytes
xml_bytes = b"<?xml version='1.0'?>..."
build = PathOfBuildingAPI(xml_bytes)

# From Element
from lxml.etree import fromstring
element = fromstring(xml_bytes)
build = PathOfBuildingAPI(element)
```

### Properties

#### Basic Information

##### `class_name: str`
Character class (e.g., "Witch", "Ranger", "Duelist").

##### `ascendancy_name: str | None`
Ascendancy class if ascended (e.g., "Elementalist", "Deadeye"), `None` otherwise.

##### `level: int`
Character level (1-100).

##### `bandit: str | None`
Bandit choice: `"Alira"`, `"Oak"`, `"Kraityn"`, or `None`.

#### Skills

##### `skill_groups: list[SkillGroup]`
List of all skill groups (skill setups) in the build.

##### `active_skill_group: SkillGroup`
The currently active skill group.

##### `active_skill: Gem | GrantedAbility | None`
The currently active skill gem or granted ability.

##### `skill_gems: list[Gem]`
List of all skill gems in the build (convenience property).

#### Passive Tree

##### `trees: list[Tree]`
List of all passive skill trees in the build.

##### `active_skill_tree: Tree`
The currently active passive skill tree.

##### `keystones: Keystones`
Keystone nodes allocated in the passive tree.

#### Items

##### `items: list[Item]`
List of all items in the build.

##### `item_sets: list[Set]`
List of all item sets (equipment configurations).

##### `active_item_set: Set`
The currently active item set.

##### `second_weapon_set: bool`
Whether the second weapon set is active.

#### Statistics and Configuration

##### `stats: Stats`
Character statistics namespace. Contains over 100 calculated stats including:
- Life, Mana, Energy Shield
- Armour, Evasion
- DPS, Average Hit
- Resistances
- And many more

##### `config: Config`
Build configuration namespace. Contains over 200 configuration options including:
- Enemy level and stats
- Player conditions
- Skill conditions
- Damage calculations
- And many more

#### Other

##### `notes: str`
Build notes/description.

### Methods

#### Build Modification

##### `add_node(node_id: int, tree_index: int = 0) -> None`
Add a passive tree node to the build.

**Parameters:**
- `node_id`: Node ID (can use `PassiveNodeID` enum or integer)
- `tree_index`: Index of tree (default: 0)

**Raises:**
- `ValidationError`: If tree_index is invalid

**Example:**
```python
from pobapi import PassiveNodeID

build.add_node(PassiveNodeID.ELEMENTAL_EQUILIBRIUM)
build.add_node(39085, tree_index=0)
```

##### `remove_node(node_id: int, tree_index: int = 0) -> None`
Remove a passive tree node from the build.

**Parameters:**
- `node_id`: Node ID to remove
- `tree_index`: Index of tree (default: 0)

**Raises:**
- `ValidationError`: If tree_index is invalid

##### `equip_item(item: Item, slot: ItemSlot | str, item_set_index: int = 0) -> int`
Equip an item in a specific slot.

**Parameters:**
- `item`: Item to equip
- `slot`: Slot name (can use `ItemSlot` enum or string)
- `item_set_index`: Index of item set (default: 0)

**Returns:**
- Index of the item in the items list

**Raises:**
- `ValidationError`: If slot or item_set_index is invalid

**Example:**
```python
from pobapi import ItemSlot
from pobapi.models import Item

item = Item(...)
index = build.equip_item(item, ItemSlot.HELMET)
index = build.equip_item(item, "Helmet")  # Also works
```

##### `add_skill(gem: Gem, group_label: str | None = None) -> None`
Add a skill gem to the build.

**Parameters:**
- `gem`: Skill gem to add
- `group_label`: Optional label for skill group (creates new group if not exists)

**Example:**
```python
from pobapi.models import Gem

gem = Gem(name="Fireball", level=20, quality=20, enabled=True)
build.add_skill(gem, group_label="Main Skill")
```

#### Export

##### `to_xml() -> bytes`
Export the build to XML format.

**Returns:**
- XML bytes representing the build

**Example:**
```python
xml_bytes = build.to_xml()
with open("build.xml", "wb") as f:
    f.write(xml_bytes)
```

##### `to_import_code() -> str`
Export the build to import code format (for sharing).

**Returns:**
- Import code string

**Example:**
```python
import_code = build.to_import_code()
print(f"Share this code: {import_code}")
```

---

## BuildBuilder

Fluent interface for creating new builds programmatically.

### Initialization

```python
BuildBuilder()
```

**Example:**
```python
from pobapi import create_build

builder = create_build()
```

### Methods

#### Character Setup

##### `set_class(class_name: CharacterClass | str, ascendancy_name: Ascendancy | str | None = None) -> BuildBuilder`
Set character class and ascendancy.

**Parameters:**
- `class_name`: Character class (enum or string)
- `ascendancy_name`: Optional ascendancy (enum or string)

**Returns:**
- Self for method chaining

**Example:**
```python
from pobapi import CharacterClass, Ascendancy

builder.set_class(CharacterClass.WITCH, Ascendancy.ELEMENTALIST)
builder.set_class("Witch", "Elementalist")  # Also works
```

##### `set_level(level: int) -> BuildBuilder`
Set character level.

**Parameters:**
- `level`: Character level (1-100)

**Returns:**
- Self for method chaining

##### `set_bandit(bandit: BanditChoice | str | None) -> BuildBuilder`
Set bandit choice.

**Parameters:**
- `bandit`: Bandit choice (enum, string, or None)

**Returns:**
- Self for method chaining

#### Passive Tree

##### `create_tree(tree_index: int = 0) -> BuildBuilder`
Create a passive skill tree.

**Parameters:**
- `tree_index`: Index of tree (default: 0)

**Returns:**
- Self for method chaining

##### `allocate_node(node_id: int, tree_index: int = 0) -> BuildBuilder`
Allocate a passive tree node.

**Parameters:**
- `node_id`: Node ID
- `tree_index`: Index of tree (default: 0)

**Returns:**
- Self for method chaining

#### Items

##### `add_item(item: Item) -> BuildBuilder`
Add an item to the build.

**Parameters:**
- `item`: Item to add

**Returns:**
- Self for method chaining

##### `equip_item(item: Item, slot: ItemSlot | str, item_set_index: int = 0) -> BuildBuilder`
Add and equip an item in a slot.

**Parameters:**
- `item`: Item to equip
- `slot`: Slot name
- `item_set_index`: Index of item set (default: 0)

**Returns:**
- Self for method chaining

##### `create_item_set(item_set_index: int = 0) -> BuildBuilder`
Create an item set.

**Parameters:**
- `item_set_index`: Index of item set (default: 0)

**Returns:**
- Self for method chaining

#### Skills

##### `add_skill(gem: Gem, group_label: str | None = None) -> BuildBuilder`
Add a skill gem.

**Parameters:**
- `gem`: Skill gem to add
- `group_label`: Optional group label

**Returns:**
- Self for method chaining

#### Build

##### `build() -> PathOfBuildingAPI`
Create the PathOfBuildingAPI instance from the builder.

**Returns:**
- PathOfBuildingAPI instance

**Example:**
```python
from pobapi import create_build, CharacterClass, Ascendancy, PassiveNodeID
from pobapi.models import Item, Gem

build = (
    create_build()
    .set_class(CharacterClass.WITCH, Ascendancy.ELEMENTALIST)
    .set_level(90)
    .allocate_node(PassiveNodeID.ELEMENTAL_EQUILIBRIUM)
    .add_item(Item(...))
    .add_skill(Gem(name="Fireball", level=20))
    .build()
)
```

---

## BuildModifier

Internal class for modifying existing builds. Used by `PathOfBuildingAPI` methods.

**Note:** This class is typically not used directly. Use `PathOfBuildingAPI` methods instead.

---

## Factory Functions

### `from_url(url: str, timeout: float = 6.0) -> PathOfBuildingAPI`

Load a build from a pastebin.com URL.

**Parameters:**
- `url`: pastebin.com URL
- `timeout`: Request timeout in seconds (default: 6.0)

**Returns:**
- PathOfBuildingAPI instance

**Raises:**
- `InvalidURLError`: If URL is invalid
- `NetworkError`: If network request fails
- `ParsingError`: If XML parsing fails

**Example:**
```python
from pobapi import from_url

build = from_url("https://pastebin.com/abc123")
```

### `from_import_code(import_code: str, timeout: float = 6.0) -> PathOfBuildingAPI`

Load a build from an import code.

**Parameters:**
- `import_code`: Path of Building import code
- `timeout`: Request timeout in seconds (default: 6.0)

**Returns:**
- PathOfBuildingAPI instance

**Raises:**
- `InvalidImportCodeError`: If import code is invalid
- `ParsingError`: If XML parsing fails

**Example:**
```python
from pobapi import from_import_code

import_code = "eNrFk..."
build = from_import_code(import_code)
```

### `create_build() -> BuildBuilder`

Create a new empty build using BuildBuilder.

**Returns:**
- BuildBuilder instance

**Example:**
```python
from pobapi import create_build

builder = create_build()
```

---

## Data Models

### Item

Represents an item in the build.

**Fields:**
- `rarity: str` - Item rarity (Normal, Magic, Rare, Unique)
- `name: str` - Item name
- `base: str` - Base type name
- `uid: str` - Unique ID
- `shaper: bool` - Is Shaper item
- `elder: bool` - Is Elder item
- `crafted: bool` - Is crafted
- `quality: int | None` - Quality (0-23)
- `sockets: tuple | None` - Socket groups
- `level_req: int` - Level requirement
- `item_level: int` - Item level
- `implicit: int` - Number of implicit mods
- `text: str` - Full item text

### Gem

Represents a skill gem.

**Fields:**
- `name: str` - Gem name
- `level: int` - Gem level (1-21)
- `quality: int | None` - Quality (0-23)
- `enabled: bool` - Is enabled
- `support: bool` - Is support gem

### GrantedAbility

Represents a granted ability (from items, etc.).

**Fields:**
- `name: str` - Ability name
- `level: int` - Level
- `enabled: bool` - Is enabled

### SkillGroup

Represents a skill group (skill setup).

**Fields:**
- `enabled: bool` - Is enabled
- `label: str` - Group label
- `active: int | None` - Index of active skill
- `abilities: list[Gem | GrantedAbility]` - List of abilities

### Tree

Represents a passive skill tree.

**Fields:**
- `nodes: list[int]` - List of allocated node IDs
- `url: str` - Tree URL

### Set

Represents an item set (equipment configuration).

**Fields:**
- `weapon1: int | None` - Weapon 1 item index
- `weapon1_swap: int | None` - Weapon 1 swap item index
- `weapon2: int | None` - Weapon 2 item index
- `weapon2_swap: int | None` - Weapon 2 swap item index
- `helmet: int | None` - Helmet item index
- `body_armour: int | None` - Body armour item index
- `gloves: int | None` - Gloves item index
- `boots: int | None` - Boots item index
- `amulet: int | None` - Amulet item index
- `ring1: int | None` - Ring 1 item index
- `ring2: int | None` - Ring 2 item index
- `belt: int | None` - Belt item index
- `flask1: int | None` - Flask 1 item index
- `flask2: int | None` - Flask 2 item index
- `flask3: int | None` - Flask 3 item index
- `flask4: int | None` - Flask 4 item index
- `flask5: int | None` - Flask 5 item index

### Stats

Namespace for character statistics. Contains over 100 properties including:

**Defense:**
- `life`, `mana`, `energy_shield`
- `armour`, `evasion`, `ward`
- `fire_resist`, `cold_resist`, `lightning_resist`, `chaos_resist`

**Offense:**
- `total_dps`, `average_hit`
- `fire_damage`, `cold_damage`, `lightning_damage`, `chaos_damage`
- `attack_speed`, `cast_speed`

**And many more...**

### Config

Namespace for build configuration. Contains over 200 properties including:

**Enemy Configuration:**
- `enemy_level`, `enemy_physical_damage_reduction`
- `enemy_fire_resist`, `enemy_cold_resist`, etc.

**Player Conditions:**
- `on_full_life`, `on_low_life`
- `has_energy_shield`, `is_stationary`, `is_moving`

**And many more...**

---

## Type Definitions

### CharacterClass

Enum for character classes:
- `DUELIST`
- `MARAUDER`
- `RANGER`
- `SCOION`
- `SHADOW`
- `TEMPLAR`
- `WITCH`

### Ascendancy

Enum for ascendancy classes:
- `SLAYER`, `GLADIATOR`, `CHAMPION` (Duelist)
- `JUGGERNAUT`, `BERSERKER`, `CHIEFTAIN` (Marauder)
- `DEADEYE`, `RAIDER`, `PATHFINDER` (Ranger)
- `ASSASSIN`, `TRICKSTER`, `SABOTEUR` (Shadow)
- `INQUISITOR`, `HIEROPHANT`, `GUARDIAN` (Templar)
- `OCCULTIST`, `ELEMENTALIST`, `NECROMANCER` (Witch)

### ItemSlot

Enum for item slots:
- `WEAPON1`, `WEAPON1_SWAP`
- `WEAPON2`, `WEAPON2_SWAP`
- `HELMET`, `BODY_ARMOUR`, `GLOVES`, `BOOTS`
- `AMULET`, `RING1`, `RING2`, `BELT`
- `FLASK1`, `FLASK2`, `FLASK3`, `FLASK4`, `FLASK5`

### BanditChoice

Enum for bandit choices:
- `ALIRA`
- `OAK`
- `KRAITYN`
- `NONE`

### PassiveNodeID

Enum with common passive node IDs:
- `ELEMENTAL_EQUILIBRIUM`
- `ANCESTRAL_BOND`
- And many more...

### SkillName

Enum with common skill gem names.

---

## Exceptions

### PobAPIError

Base exception for all API errors.

### ParsingError

Raised when XML parsing fails.

### ValidationError

Raised when input validation fails.

### InvalidURLError

Raised when URL is invalid.

### InvalidImportCodeError

Raised when import code is invalid.

### NetworkError

Raised when network requests fail.

---

## Utilities

### Cache Management

#### `clear_cache() -> None`

Clear all caches.

#### `get_cache() -> dict`

Get cache statistics.

---

## Complete Example

```python
from pobapi import (
    PathOfBuildingAPI,
    from_url,
    from_import_code,
    create_build,
    CharacterClass,
    Ascendancy,
    ItemSlot,
    PassiveNodeID,
)
from pobapi.models import Item, Gem

# Load from URL
build = from_url("https://pastebin.com/abc123")

# Load from import code
build = from_import_code("eNrFk...")

# Access properties
print(f"Class: {build.class_name}")
print(f"Ascendancy: {build.ascendancy_name}")
print(f"Level: {build.level}")

# Access items
for item in build.items:
    print(f"Item: {item.name} ({item.rarity})")

# Access skills
for group in build.skill_groups:
    print(f"Skill Group: {group.label}")
    for ability in group.abilities:
        print(f"  - {ability.name} (Level {ability.level})")

# Access stats
print(f"Life: {build.stats.life}")
print(f"DPS: {build.stats.total_dps}")

# Modify build
build.add_node(PassiveNodeID.ELEMENTAL_EQUILIBRIUM)
build.equip_item(item, ItemSlot.HELMET)

# Export
xml_bytes = build.to_xml()
import_code = build.to_import_code()

# Create new build
new_build = (
    create_build()
    .set_class(CharacterClass.WITCH, Ascendancy.ELEMENTALIST)
    .set_level(90)
    .allocate_node(PassiveNodeID.ELEMENTAL_EQUILIBRIUM)
    .add_skill(Gem(name="Fireball", level=20, quality=20, enabled=True))
    .build()
)
```

---

## See Also

- [API Capabilities](API_CAPABILITIES_EN.md) - Overview of what can be extracted
- [Build Creation Capabilities](BUILD_CREATION_CAPABILITIES_EN.md) - Guide to creating builds
- [Architecture](ARCHITECTURE.md) - Project architecture
- [Class Diagram](CLASS_DIAGRAM.md) - Complete class diagrams


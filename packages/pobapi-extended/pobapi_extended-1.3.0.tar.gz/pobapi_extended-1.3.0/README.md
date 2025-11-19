# Path of Building API Extended (pobapi-extended)

[![Maintenance](https://img.shields.io/maintenance/yes/2024)](https://github.com/ppoelzl/PathOfBuildingAPI)
[![Read the Docs](https://readthedocs.org/projects/pobapi/badge)](https://pobapi.readthedocs.io)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pobapi-extended)](https://pypi.org/project/pobapi-extended/)
[![PyPI - Version](https://img.shields.io/pypi/v/pobapi-extended)](https://pypi.org/project/pobapi-extended/)
[![PyPI - Status](https://img.shields.io/pypi/status/pobapi-extended)](https://pypi.org/project/pobapi-extended/)
[![PyPI - Format](https://img.shields.io/pypi/format/pobapi-extended)](https://pypi.org/project/pobapi-extended/)
[![License](https://img.shields.io/pypi/l/pobapi-extended)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

API for Path of Building's build sharing format for builds in Path of Exile.

## Background

Path Of Building API provides a comprehensive toolbox for processing [Path of Building](https://github.com/PathOfBuildingCommunity/PathOfBuilding) pastebins. It is aimed at community developers:

* looking to add Path of Building functionality to their apps.
* upgrading from existing solutions.

### Benefits from using this library:

* Focus on your app's core competences
* Spend your free time on unique features
* Backwards-compatibility as PoB's export format changes
* Tested and secure codebase

## Features

* Look up and process:
    * Character stats (DPS, life, etc.)
    * Skill trees
    * Skills, skill groups and links
    * Gear and item sets
    * Path of Building configuration settings
    * Build author's notes
* Exposes all of Path of Building's relevant stats and attributes in a simple and pythonic way.
* Automatically calculates mod values on theorycrafted items.
* Low memory footprint through dataclasses and dynamically generated attributes.

## Installation

```bash
pip install pobapi-extended
```

Or using uv:

```bash
uv add pobapi-extended
```

## Dependencies

* Python 3.12+
* [lxml](https://pypi.org/project/lxml/) (>=4.6.2)
* [requests](https://pypi.org/project/requests/) (>=2.25.1)
* [lupa](https://pypi.org/project/lupa/) (>=2.6)
* [six](https://pypi.org/project/six/) (>=1.17.0)

> **Note:** The library previously used `dataslots` and `unstdlib`, but has been migrated to standard Python `dataclasses` and custom decorators (Python 3.12+).

## Usage

```python
import pobapi

# From pastebin URL
url = "https://pastebin.com/bQRjfedq"
build = pobapi.from_url(url)
print(build.ascendancy_name)  # Elementalist
print(build.stats.life)  # 6911

# From import code
import_code = "your-import-code-here"
build = pobapi.from_import_code(import_code)

# Access build data
print(build.class_name)
print(build.level)
print(build.bandit)

# Access stats
print(build.stats.total_dps)
print(build.stats.life)
print(build.stats.mana)

# Access items
for item in build.items:
    if item.name == "Inpulsa's Broken Heart":
        print(item)

# Access skills
for skill_group in build.skill_groups:
    print(skill_group.label)
    for ability in skill_group.abilities:
        print(f"  {ability.name} (Level {ability.level})")

# Access skill tree
tree = build.active_skill_tree
print(f"Tree URL: {tree.url}")
print(f"Nodes: {len(tree.nodes)}")

# Access configuration
config = build.config
print(f"Enemy level: {config.enemy_level}")
print(f"Onslaught: {config.onslaught}")
```

## Async Support

For async applications, use the factory with an async HTTP client:

```python
import aiohttp
from pobapi.factory import BuildFactory
from pobapi.interfaces import AsyncHTTPClient

class AioHTTPClient(AsyncHTTPClient):
    async def get(self, url: str, timeout: float = 6.0) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                return await response.text()

factory = BuildFactory(async_http_client=AioHTTPClient())
build = await factory.async_from_url("https://pastebin.com/...")
```

## Caching

Caching is automatically enabled for:
- Import code decoding (1 hour TTL)
- Skill tree parsing (24 hours TTL)

You can manage the cache:

```python
from pobapi import clear_cache, get_cache

# Get cache statistics
cache = get_cache()
stats = cache.stats()

# Clear cache
clear_cache()
```

## Error Handling

The library provides custom exceptions:

```python
from pobapi.exceptions import (
    InvalidImportCodeError,
    InvalidURLError,
    NetworkError,
    ParsingError,
    ValidationError,
)

try:
    build = pobapi.from_url("invalid-url")
except InvalidURLError as e:
    print(f"Invalid URL: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
```

## Documentation

Full documentation available at [Read the Docs](https://pobapi.readthedocs.io).

## License

MIT License - see LICENSE.txt for details.

## Roadmap

* Support corruptions
* Support enchantments

## Feedback

Please open a [GitHub issue](https://github.com/ppoelzl/PathOfBuildingAPI/issues) in this repository for any feedback you may have.

## Contributing

Setup repository using [Git](https://git-scm.com/) (recommended):

```bash
git clone https://github.com/ppoelzl/PathOfBuildingAPI.git
```

Install dev dependencies using [uv](https://github.com/astral-sh/uv) (recommended):

```bash
uv sync
```

Or using pip:

```bash
pip install -e ".[dev]"
```

If you have any questions about contributing, please open a [GitHub issue](https://github.com/ppoelzl/PathOfBuildingAPI/issues). Pull requests are gladly accepted. Check out the [Developer Guide](https://pobapi.readthedocs.io/dev.html) for more info.

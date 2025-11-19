"""Shared fixtures and utilities for tests."""

import pytest
from lxml.etree import fromstring

# Import commonly used types to make them available in all tests
from pobapi.types import DamageType  # noqa: F401


@pytest.fixture(scope="module")
def build():
    """Create a PathOfBuildingAPI instance from test data file."""
    from pathlib import Path

    from pobapi import api

    test_file = Path(__file__).parent.parent / "data" / "test_code.txt"
    with open(test_file) as f:
        code = f.read()
    return api.from_import_code(code)


@pytest.fixture
def sample_xml_root():
    """Create a sample XML root element for testing."""
    xml_str = """<?xml version="1.0"?>
    <PathOfBuilding>
        <Build className="Scion" ascendClassName="Ascendant" level="1"
               bandit="Alira" mainSocketGroup="1">
            <PlayerStat stat="Life" value="163"/>
            <PlayerStat stat="Mana" value="60"/>
        </Build>
        <Skills>
            <Skill enabled="true" label="Test label" mainActiveSkill="1">
                <Ability name="Arc" enabled="true" level="20" quality="1"
                         gemId="1" skillId="Arc"/>
            </Skill>
        </Skills>
        <Items>
            <Item variant="1">
                Rarity: Unique
                Inpulsa's Broken Heart
                Sadist Garb
                Quality: 20
                Sockets: R-G-B B-B-B
                LevelReq: 68
                Item Level: 71
                Implicits: 2
                +64 to maximum Life
            </Item>
            <ItemSet>
                <Slot name="Body Armour" itemId="1"/>
                <Slot name="Helmet" itemId="2"/>
            </ItemSet>
        </Items>
        <Config>
            <Input name="enemyLevel" number="84"/>
            <Input name="conditionStationary" boolean="true"/>
        </Config>
        <Tree activeSpec="1">
            <Spec>
                <URL>https://www.pathofexile.com/passive-skill-tree/AAAABAABAJitGFbaYij62E1odILHlKD56A==</URL>
                <Socket nodeId="1" itemId="1"/>
            </Spec>
        </Tree>
    </PathOfBuilding>"""
    return fromstring(xml_str.encode())


@pytest.fixture
def sample_xml():
    """Create a sample XML string for testing."""
    return """<?xml version="1.0"?>
    <PathOfBuilding>
        <Build className="Scion" ascendClassName="Ascendant" level="1"
               bandit="Alira" mainSocketGroup="1">
            <PlayerStat stat="Life" value="163"/>
            <PlayerStat stat="Mana" value="60"/>
        </Build>
        <Skills>
            <Skill enabled="true" label="Test" mainActiveSkill="1">
                <Ability name="Arc" enabled="true" level="20" quality="1"
                         gemId="1" skillId="Arc"/>
            </Skill>
        </Skills>
        <Items>
            <Item>
                Rarity: Unique
                Test Item
                Test Base
                LevelReq: 1
                Item Level: 1
            </Item>
            <ItemSet>
                <Slot name="Body Armour" itemId="1"/>
            </ItemSet>
        </Items>
        <Config>
            <Input name="enemyLevel" number="84"/>
        </Config>
        <Tree activeSpec="1">
            <Spec>
                <URL>https://www.pathofexile.com/passive-skill-tree/AAAABAABAJitGFbaYij62E1odILHlKD56A==</URL>
            </Spec>
        </Tree>
    </PathOfBuilding>"""


@pytest.fixture
def minimal_xml():
    """Create minimal valid XML for testing."""
    return """<?xml version="1.0"?>
    <PathOfBuilding>
        <Build className="Scion" level="1"/>
        <Skills/>
        <Items/>
        <Tree/>
    </PathOfBuilding>"""


@pytest.fixture
def mock_async_http_client():
    """Create a mock async HTTP client for testing."""
    from tests.unit.test_async_util import MockAsyncHTTPClient

    return MockAsyncHTTPClient


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client for testing."""
    from tests.unit.test_factory import MockHTTPClient

    return MockHTTPClient


# Calculator fixtures
@pytest.fixture
def modifier_system():
    """Create a ModifierSystem instance for testing."""
    from pobapi.calculator.modifiers import ModifierSystem

    return ModifierSystem()


@pytest.fixture
def damage_calculator(modifier_system):
    """Create a DamageCalculator instance for testing."""
    from pobapi.calculator.damage import DamageCalculator

    return DamageCalculator(modifier_system)


@pytest.fixture
def defense_calculator(modifier_system):
    """Create a DefenseCalculator instance for testing."""
    from pobapi.calculator.defense import DefenseCalculator

    return DefenseCalculator(modifier_system)


@pytest.fixture
def resource_calculator(modifier_system):
    """Create a ResourceCalculator instance for testing."""
    from pobapi.calculator.resource import ResourceCalculator

    return ResourceCalculator(modifier_system)


@pytest.fixture
def skill_stats_calculator(modifier_system):
    """Create a SkillStatsCalculator instance for testing."""
    from pobapi.calculator.skill_stats import SkillStatsCalculator

    return SkillStatsCalculator(modifier_system)


@pytest.fixture
def minion_calculator(modifier_system):
    """Create a MinionCalculator instance for testing."""
    from pobapi.calculator.minion import MinionCalculator

    return MinionCalculator(modifier_system)


@pytest.fixture
def party_calculator(modifier_system):
    """Create a PartyCalculator instance for testing."""
    from pobapi.calculator.party import PartyCalculator

    return PartyCalculator(modifier_system)


@pytest.fixture
def penetration_calculator(modifier_system):
    """Create a PenetrationCalculator instance for testing."""
    from pobapi.calculator.penetration import PenetrationCalculator

    return PenetrationCalculator(modifier_system)


# Mock objects fixtures
@pytest.fixture
def mock_jewel():
    """Create a mock jewel item."""
    from types import SimpleNamespace

    def _create_jewel(name="Crimson Jewel", text="+10% to Fire Resistance", **kwargs):
        jewel = SimpleNamespace(name=name, text=text)
        for key, value in kwargs.items():
            setattr(jewel, key, value)
        return jewel

    return _create_jewel


@pytest.fixture
def mock_build():
    """Create a mock build object."""
    from dataclasses import dataclass
    from typing import Any

    @dataclass
    class MockBuild:
        """Mock build data for testing."""

        active_skill_tree: Any = None
        items: list[Any] = None
        skill_groups: list[Any] = None
        config: Any = None
        party_members: list[Any] = None

        def __post_init__(self):
            """Initialize default values."""
            if self.items is None:
                self.items = []
            if self.skill_groups is None:
                self.skill_groups = []
            if self.party_members is None:
                self.party_members = []

    return MockBuild


@pytest.fixture
def mock_tree():
    """Create a mock tree object."""
    from dataclasses import dataclass

    @dataclass
    class MockTree:
        """Mock skill tree for testing."""

        nodes: list[int] = None
        sockets: dict[int, int] = None

        def __post_init__(self):
            """Initialize default values."""
            if self.nodes is None:
                self.nodes = []
            if self.sockets is None:
                self.sockets = {}

    return MockTree


@pytest.fixture
def mock_item():
    """Create a mock item object."""
    from dataclasses import dataclass

    @dataclass
    class MockItem:
        """Mock item for testing."""

        name: str = "Test Item"
        text: str = "+10 to Strength"

    return MockItem


@pytest.fixture
def mock_skill_group():
    """Create a mock skill group object."""
    from dataclasses import dataclass
    from typing import Any

    @dataclass
    class MockSkillGroup:
        """Mock skill group for testing."""

        abilities: list[Any] = None
        enabled: bool = True
        active: int | None = None

        def __post_init__(self):
            """Initialize default values."""
            if self.abilities is None:
                self.abilities = []

    return MockSkillGroup


@pytest.fixture
def mock_config():
    """Create a mock config object."""
    from dataclasses import dataclass

    @dataclass
    class MockConfig:
        """Mock config for testing."""

        onslaught: bool = False
        fortify: bool = False
        tailwind: bool = False
        adrenaline: bool = False
        use_power_charges: bool = False
        max_power_charges: int = 3
        use_frenzy_charges: bool = False
        max_frenzy_charges: int = 3
        use_endurance_charges: bool = False
        max_endurance_charges: int = 3
        has_hatred: bool = False
        has_anger: bool = False
        has_wrath: bool = False
        has_haste: bool = False
        has_grace: bool = False
        has_determination: bool = False
        has_discipline: bool = False
        has_flammability: bool = False
        has_frostbite: bool = False
        has_conductivity: bool = False
        has_enfeeble: bool = False
        has_vulnerability: bool = False
        on_full_life: bool = False
        on_low_life: bool = False
        on_full_energy_shield: bool = False
        on_full_mana: bool = False
        enemy_level: int = 80
        enemy_fire_resist: float | None = None
        enemy_cold_resist: float | None = None
        enemy_lightning_resist: float | None = None
        enemy_chaos_resist: float | None = None
        enemy_physical_damage_reduction: float | None = None

    return MockConfig


@pytest.fixture
def mock_ability():
    """Create a mock ability object."""
    from dataclasses import dataclass

    @dataclass
    class MockAbility:
        """Mock ability for testing."""

        name: str = "Test Skill"
        enabled: bool = True
        level: int = 20
        quality: int = 0
        support: bool = False

    return MockAbility


@pytest.fixture
def create_test_item():
    """Create a test Item object."""
    from pobapi.models import Item

    def _create_item(
        name: str = "Test Item",
        base: str = "Leather Belt",
        rarity: str = "Rare",
        item_level: int = 80,
        quality: int = 0,
        **kwargs,
    ) -> Item:
        """Helper function to create test Item."""
        defaults = {
            "uid": "0",
            "shaper": False,
            "elder": False,
            "crafted": False,
            "sockets": None,
            "level_req": 1,
            "implicit": None,
            "text": "",
        }
        defaults.update(kwargs)
        return Item(
            name=name,
            base=base,
            rarity=rarity,
            quality=quality,
            item_level=item_level,
            **defaults,
        )

    return _create_item


@pytest.fixture(scope="module")
def build_with_jewels():
    """Create a PathOfBuildingAPI instance with jewels for testing."""
    from pobapi import create_build, models
    from pobapi.types import Ascendancy, CharacterClass

    # Create build builder
    builder = create_build()

    # Set character class and level
    builder.set_class(CharacterClass.WITCH, Ascendancy.ELEMENTALIST)
    builder.set_level(90)

    # Create passive skill tree
    builder.create_tree()

    # Add several different types of jewels
    jewels = [
        models.Item(
            rarity="Rare",
            name="Crimson Jewel",
            base="Crimson Jewel",
            uid="jewel-1",
            shaper=False,
            elder=False,
            crafted=False,
            quality=None,
            sockets=None,
            level_req=1,
            item_level=84,
            implicit=None,
            text="""Rarity: RARE
Crimson Jewel
--------
Item Level: 84
--------
+10% to Fire Resistance
+7% increased maximum Life
+12% increased Physical Damage
--------
""",
        ),
        models.Item(
            rarity="Rare",
            name="Viridian Jewel",
            base="Viridian Jewel",
            uid="jewel-2",
            shaper=False,
            elder=False,
            crafted=False,
            quality=None,
            sockets=None,
            level_req=1,
            item_level=84,
            implicit=None,
            text="""Rarity: RARE
Viridian Jewel
--------
Item Level: 84
--------
+10% to Cold Resistance
+8% increased Attack Speed
+15% increased Evasion Rating
--------
""",
        ),
        models.Item(
            rarity="Rare",
            name="Cobalt Jewel",
            base="Cobalt Jewel",
            uid="jewel-3",
            shaper=False,
            elder=False,
            crafted=False,
            quality=None,
            sockets=None,
            level_req=1,
            item_level=84,
            implicit=None,
            text="""Rarity: RARE
Cobalt Jewel
--------
Item Level: 84
--------
+10% to Lightning Resistance
+5% increased Cast Speed
+12% increased Energy Shield
--------
""",
        ),
    ]

    # Add jewels to build
    for jewel in jewels:
        builder.add_item(jewel)

    # Create item set (required for build)
    builder.create_item_set()

    # Build and return the PathOfBuildingAPI instance
    build = builder.build()
    return build

"""Shared fixtures for integration tests."""

import os

import pytest
from lxml.etree import fromstring


@pytest.fixture(scope="module")
def build():
    """Create a PathOfBuildingAPI instance from test data file."""
    from pobapi import api

    test_file = os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "test_code.txt"
    )
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

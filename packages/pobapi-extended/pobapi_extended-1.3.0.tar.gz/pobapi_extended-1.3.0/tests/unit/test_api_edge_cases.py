"""Tests for edge cases in api.py."""

import pytest

from pobapi import api, models


class TestVaalSkillHandling:
    """Tests for Vaal skill handling in active_skill property."""

    def test_vaal_skill_with_duplicate(self):
        """Test active_skill with Vaal skill that creates duplicate."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1" mainSocketGroup="1"/>
            <Skills>
                <Skill enabled="true" label="" mainActiveSkill="2">
                    <Gem gemId="1" nameSpec="Vaal Breach" enabled="true"
                         level="20" quality="0" skillId="VaalBreach"/>
                </Skill>
            </Skills>
            <Items/>
            <Tree activeSpec="1">
                <Spec>
                    <URL>AAAABgAAAAAA</URL>
                </Spec>
            </Tree>
        </PathOfBuilding>"""
        build = api.PathOfBuildingAPI(xml_str.encode())
        # active_skill_group.active is 2 (mainActiveSkill="2"), so index = 1
        # With only one Vaal gem, duplicate = [Vaal Breach, Vaal Breach]
        # duplicate[1] == duplicate[0], so should trigger Vaal handling
        active_skill = build.active_skill
        assert isinstance(active_skill, models.Gem)
        # Should map "Vaal Breach" to "Portal" via VAAL_SKILL_MAP
        assert active_skill.name == "Portal"
        assert active_skill.level == 20

    def test_vaal_skill_without_map(self):
        """Test Vaal skill that's not in VAAL_SKILL_MAP."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1" mainSocketGroup="1"/>
            <Skills>
                <Skill enabled="true" label="" mainActiveSkill="2">
                    <Gem gemId="1" nameSpec="Vaal Fireball" enabled="true"
                         level="20" quality="0" skillId="VaalFireball"/>
                </Skill>
            </Skills>
            <Items/>
            <Tree activeSpec="1">
                <Spec>
                    <URL>AAAABgAAAAAA</URL>
                </Spec>
            </Tree>
        </PathOfBuilding>"""
        build = api.PathOfBuildingAPI(xml_str.encode())
        active_skill = build.active_skill
        assert isinstance(active_skill, models.Gem)
        # Should use rpartition to get "Fireball" from "Vaal Fireball"
        assert active_skill.name == "Fireball"
        assert active_skill.level == 20

    def test_active_skill_no_vaal_duplicate(self):
        """Test active_skill when Vaal duplicate condition is not met (line 167)."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1" mainSocketGroup="1"/>
            <Skills>
                <Skill enabled="true" label="" mainActiveSkill="2">
                    <Gem gemId="1" nameSpec="Arc" enabled="true"
                         level="20" quality="0" skillId="Arc"/>
                    <Gem gemId="2" nameSpec="Vaal Breach" enabled="true"
                         level="20" quality="0" skillId="VaalBreach"/>
                </Skill>
            </Skills>
            <Items/>
            <Tree activeSpec="1">
                <Spec>
                    <URL>AAAABgAAAAAA</URL>
                </Spec>
            </Tree>
        </PathOfBuilding>"""
        build = api.PathOfBuildingAPI(xml_str.encode())
        # active_skill_group.active is 2 (mainActiveSkill="2"), so index = 1
        # duplicate = [Vaal Breach, Arc, Vaal Breach]
        # duplicate[1] != duplicate[0], so should return abilities[1] directly
        active_skill = build.active_skill
        assert isinstance(active_skill, models.Gem)
        assert active_skill.name == "Vaal Breach"


class TestKeystonesIterator:
    """Tests for Keystones __iter__ method."""

    def test_keystones_iterator(self):
        """Test iterating over active keystones."""
        from pathlib import Path

        from pobapi import api

        test_file = Path(__file__).parent.parent.parent / "data" / "test_code.txt"
        with open(test_file) as f:
            code = f.read()
        build = api.from_import_code(code)
        keystones = build.keystones

        # Test iteration
        active_keystones = list(keystones)
        # Should only include keystones that are True
        assert isinstance(active_keystones, list)
        # All values should be field names (strings)
        for keystone_name in active_keystones:
            assert isinstance(keystone_name, str)


class TestItemStr:
    """Tests for Item __str__ method."""

    def test_item_str_full(self):
        """Test Item __str__ with all fields (covers lines 234, 238, 240, 242, 246)."""
        item = models.Item(
            rarity="Unique",
            name="Test Item",
            base="Test Base",
            uid="test-uid",
            shaper=True,  # Covers line 234
            elder=False,
            crafted=True,  # Covers line 238
            quality=20,  # Covers line 240
            sockets=(("R", "G", "B"),),  # type: ignore[arg-type]  # Covers line 242
            level_req=68,
            item_level=84,
            implicit=2,  # Covers line 246
            text="+10 to maximum Life\n+20 to maximum Mana",
        )
        item_str = str(item)
        assert "Rarity: Unique" in item_str
        assert "Name: Test Item" in item_str
        assert "Base: Test Base" in item_str
        assert "Shaper Item" in item_str  # Line 234
        assert "Elder Item" not in item_str
        assert "Crafted Item" in item_str  # Line 238
        assert "Quality: 20" in item_str  # Line 240
        assert "Sockets: (('R', 'G', 'B'),)" in item_str  # Line 242
        assert "LevelReq: 68" in item_str
        assert "ItemLvl: 84" in item_str
        assert "Implicits: 2" in item_str  # Line 246
        assert "+10 to maximum Life" in item_str

    def test_item_str_minimal(self):
        """Test Item __str__ with minimal fields."""
        item = models.Item(
            rarity="Normal",
            name="Test Item",  # name cannot be empty due to validation
            base="Test Base",
            uid="",
            shaper=False,
            elder=False,
            crafted=False,
            quality=None,
            sockets=None,
            level_req=1,
            item_level=1,
            implicit=0,
            text="",
        )
        item_str = str(item)
        assert "Rarity: Normal" in item_str
        assert "Name: Test Item" in item_str
        assert "Shaper Item" not in item_str
        assert "Elder Item" not in item_str
        assert "Crafted Item" not in item_str
        assert "Quality:" not in item_str
        assert "Sockets:" not in item_str
        # implicit=0 is not printed (only if > 0)
        assert "Implicits:" not in item_str

    @pytest.mark.parametrize("elder", [True, False])
    def test_item_str_elder_field(self, elder):
        """Test Item __str__ with elder field (line 236)."""
        item = models.Item(
            rarity="Unique",
            name="Test Item",
            base="Test Base",
            uid="test-uid",
            shaper=False,
            elder=elder,
            crafted=False,
            quality=None,
            sockets=None,
            level_req=1,
            item_level=1,
            implicit=0,
            text="",
        )
        item_str = str(item)
        if elder:
            assert "Elder Item" in item_str
        else:
            assert "Elder Item" not in item_str

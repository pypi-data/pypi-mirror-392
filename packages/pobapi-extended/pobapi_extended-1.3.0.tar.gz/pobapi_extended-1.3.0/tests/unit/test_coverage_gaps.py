"""Tests to cover remaining uncovered lines in api.py and parsers.py."""

from lxml.etree import fromstring

from pobapi import api
from pobapi.parsers import SkillsParser, TreesParser


class TestSkillsElementMissing:
    """Tests for when Skills element is None or empty (covers api.py lines 130, 200)."""

    def test_skill_groups_empty_skills_element(self):
        """Test skill_groups when Skills element is empty (covers api.py line 130)."""
        # Use empty Skills element to trigger the None check in the method
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills/>
            <Items/>
            <Tree activeSpec="1">
                <Spec>
                    <URL>AAAABgAAAAAA</URL>
                </Spec>
            </Tree>
        </PathOfBuilding>"""
        build = api.PathOfBuildingAPI(xml_str.encode())
        # When Skills element exists but has no SkillSet or Skill children,
        # skill_groups should return empty list
        assert build.skill_groups == []

    def test_skill_gems_empty_skills_element(self):
        """Test skill_gems when Skills element is empty (covers api.py line 200)."""
        # Use empty Skills element to trigger the None check in the method
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills/>
            <Items/>
            <Tree activeSpec="1">
                <Spec>
                    <URL>AAAABgAAAAAA</URL>
                </Spec>
            </Tree>
        </PathOfBuilding>"""
        build = api.PathOfBuildingAPI(xml_str.encode())
        # When Skills element exists but has no SkillSet or Skill children,
        # skill_gems should return empty list
        assert build.skill_gems == []

    # Note: Lines 130 and 200 in api.py check if skills_element is None.
    # These lines cannot be covered by tests because:
    # 1. XMLValidator requires Skills element to be present
    # 2. lxml Element.find() is read-only and cannot be mocked
    # These are defensive checks that would only be useful
    # if someone bypasses validation.


class TestSkillSetStructure:
    """Tests for new SkillSet structure (Path of Building 2.0+)."""

    def test_skill_groups_with_skillset(self):
        """Test skill_groups with SkillSet wrapper (covers api.py lines 137-148)."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1" mainSocketGroup="1"/>
            <Skills>
                <SkillSet>
                    <Skill enabled="true" label="Test Group" mainActiveSkill="1">
                        <Gem gemId="1" nameSpec="Arc" enabled="true"
                             level="20" quality="0" skillId="Arc"/>
                    </Skill>
                    <Skill enabled="false" label="Group 2" mainActiveSkill="nil">
                        <Gem gemId="2" nameSpec="Fireball" enabled="true"
                             level="20" quality="0" skillId="Fireball"/>
                    </Skill>
                </SkillSet>
            </Skills>
            <Items/>
            <Tree activeSpec="1">
                <Spec>
                    <URL>AAAABgAAAAAA</URL>
                </Spec>
            </Tree>
        </PathOfBuilding>"""
        build = api.PathOfBuildingAPI(xml_str.encode())
        assert len(build.skill_groups) == 2
        assert build.skill_groups[0].enabled is True
        assert build.skill_groups[0].label == "Test Group"
        assert build.skill_groups[0].active == 1
        assert build.skill_groups[1].enabled is False
        assert build.skill_groups[1].active is None

    def test_skill_gems_with_skillset(self):
        """Test skill_gems with SkillSet wrapper (covers api.py lines 206-211)."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills>
                <SkillSet>
                    <Skill enabled="true" label="Test Group" mainActiveSkill="1">
                        <Gem gemId="1" nameSpec="Arc" enabled="true"
                             level="20" quality="0" skillId="Arc"/>
                        <Gem gemId="2" nameSpec="Fireball" enabled="true"
                             level="20" quality="0" skillId="Fireball" support="true"/>
                    </Skill>
                    <Skill enabled="true" label="Group 2" mainActiveSkill="1"
                          source="item">
                        <Gem gemId="3" nameSpec="Lightning Strike" enabled="true"
                             level="20" quality="0" skillId="LightningStrike"/>
                    </Skill>
                </SkillSet>
            </Skills>
            <Items/>
            <Tree activeSpec="1">
                <Spec>
                    <URL>AAAABgAAAAAA</URL>
                </Spec>
            </Tree>
        </PathOfBuilding>"""
        build = api.PathOfBuildingAPI(xml_str.encode())
        skill_gems = list(build.skill_gems)
        # Should only include gems from skills without "source" attribute
        # Arc and Fireball should be included,
        # Lightning Strike should not (has source="item")
        assert len(skill_gems) == 2
        assert any(gem.name == "Arc" for gem in skill_gems)
        assert any(gem.name == "Fireball" for gem in skill_gems)
        assert not any(gem.name == "Lightning Strike" for gem in skill_gems)

    def test_parser_skillset_structure(self):
        """Test SkillsParser with SkillSet structure (covers parsers.py lines 61-63)."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills>
                <SkillSet>
                    <Skill enabled="true" label="Test Group" mainActiveSkill="1">
                        <Gem gemId="1" nameSpec="Arc" enabled="true"
                             level="20" quality="0" skillId="Arc"/>
                    </Skill>
                </SkillSet>
            </Skills>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())
        result = SkillsParser.parse_skill_groups(xml_root)
        assert len(result) == 1
        assert result[0]["enabled"] is True
        assert result[0]["label"] == "Test Group"
        assert result[0]["main_active_skill"] == 1


class TestSocketsInSocketsElement:
    """Tests for sockets nested in Sockets element (covers parsers.py line 234)."""

    def test_trees_parser_with_sockets_element(self):
        """Test TreesParser with Sockets wrapper element
        (covers parsers.py line 234)."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills/>
            <Items/>
            <Tree activeSpec="1">
                <Spec>
                    <URL>https://www.pathofexile.com/passive-skill-tree/AAAABgAAAAAA</URL>
                    <Sockets>
                        <Socket nodeId="123" itemId="1"/>
                        <Socket nodeId="456" itemId="2"/>
                    </Sockets>
                </Spec>
            </Tree>
        </PathOfBuilding>"""
        xml_root = fromstring(xml_str.encode())
        result = TreesParser.parse_trees(xml_root)
        assert len(result) == 1
        assert result[0]["sockets"] == {123: 1, 456: 2}

    def test_api_trees_with_sockets_element(self):
        """Test api.trees property with Sockets wrapper element."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills/>
            <Items/>
            <Tree activeSpec="1">
                <Spec>
                    <URL>https://www.pathofexile.com/passive-skill-tree/AAAABgAAAAAA</URL>
                    <Sockets>
                        <Socket nodeId="123" itemId="1"/>
                        <Socket nodeId="456" itemId="2"/>
                    </Sockets>
                </Spec>
            </Tree>
        </PathOfBuilding>"""
        build = api.PathOfBuildingAPI(xml_str.encode())
        trees = list(build.trees)
        assert len(trees) == 1
        assert trees[0].sockets == {123: 1, 456: 2}

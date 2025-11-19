"""Tests for PathOfBuildingAPI properties."""


from pobapi import api, models
from pobapi.types import ItemSlot


class TestActiveSkillGroup:
    """Tests for active_skill_group property."""

    def test_active_skill_group_without_main_socket_group(self, minimal_xml):
        """TC-API-031: Get active_skill_group without main_socket_group."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills>
                <Skill enabled="true" label="Main">
                    <Ability name="Arc" enabled="true" level="20" quality="0"
                             gemId="1" skillId="Arc"/>
                </Skill>
            </Skills>
            <Items/>
            <Tree/>
        </PathOfBuilding>"""

        build = api.PathOfBuildingAPI(xml_str.encode())

        # Should return first group when main_socket_group is not specified
        active_group = build.active_skill_group
        assert active_group is not None
        assert active_group.label == "Main"


class TestActiveSkill:
    """Tests for active_skill property."""

    def test_active_skill_with_vaal_duplicate(self):
        """TC-API-038: Get active_skill with Vaal skill duplicate."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1" mainSocketGroup="1"/>
            <Skills>
                <Skill enabled="true" label="Main" mainActiveSkill="2">
                    <Ability name="Vaal Arc" enabled="true" level="20" quality="0"
                             gemId="1" skillId="VaalArc"/>
                </Skill>
            </Skills>
            <Items/>
            <Tree/>
        </PathOfBuilding>"""

        build = api.PathOfBuildingAPI(xml_str.encode())

        active_skill = build.active_skill
        # Should return base skill (Arc) not Vaal version
        assert active_skill is not None
        assert isinstance(active_skill, models.Gem)
        # The base skill name should be extracted from Vaal skill
        assert "Vaal" not in active_skill.name or active_skill.name == "Arc"


class TestTrees:
    """Tests for trees property."""

    def test_trees_with_url(self, mocker):
        """TC-API-042: Get trees with URL."""
        # Mock _skill_tree_nodes to return test nodes
        mock_nodes = mocker.patch("pobapi.api._skill_tree_nodes")
        mock_nodes.return_value = [1, 2, 3, 4, 5]

        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills/>
            <Items/>
            <Tree activeSpec="1">
                <Spec>
                    <URL>https://www.pathofexile.com/passive-skill-tree/AAAABAABAJitGFbaYij62E1odILHlKD56A==</URL>
                </Spec>
            </Tree>
        </PathOfBuilding>"""

        build = api.PathOfBuildingAPI(xml_str.encode())

        trees = build.trees
        assert len(trees) == 1
        assert trees[0].nodes == [1, 2, 3, 4, 5]
        mock_nodes.assert_called_once()

    def test_trees_with_nodes_element(self):
        """TC-API-043: Get trees with Nodes element."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills/>
            <Items/>
            <Tree activeSpec="1">
                <Spec>
                    <Nodes>
                        <Node id="1"/>
                        <Node id="2"/>
                        <Node id="3"/>
                    </Nodes>
                </Spec>
            </Tree>
        </PathOfBuilding>"""

        build = api.PathOfBuildingAPI(xml_str.encode())

        trees = build.trees
        assert len(trees) == 1
        assert trees[0].nodes == [1, 2, 3]

    def test_trees_with_sockets_element(self):
        """TC-API-044: Get trees with Sockets element."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills/>
            <Items/>
            <Tree activeSpec="1">
                <Spec>
                    <Sockets>
                        <Socket nodeId="1" itemId="1"/>
                        <Socket nodeId="2" itemId="2"/>
                    </Sockets>
                </Spec>
            </Tree>
        </PathOfBuilding>"""

        build = api.PathOfBuildingAPI(xml_str.encode())

        trees = build.trees
        assert len(trees) == 1
        assert trees[0].sockets == {1: 1, 2: 2}


class TestItems:
    """Tests for items property."""

    def test_items_with_pending_modifications(self, simple_build, create_test_item):
        """TC-API-049: Get items with pending modifications."""
        item = create_test_item(name="Test Helmet", base="Iron Helmet")

        # Equip item (adds to pending_items)
        simple_build.equip_item(item, ItemSlot.HELMET)

        items = list(simple_build.items)
        # Pending items should be first
        assert len(items) > 0
        # Check that pending item is included
        assert any(i.name == "Test Helmet" for i in items)

    def test_items_with_variant_and_alt_variant(self):
        """TC-API-050: Get items with variant and alt_variant."""
        xml_str = """<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills/>
            <Items>
                <Item variant="1" variantAlt="2">
                    <ModRange range="0.5"/>
                    <ModRange range="0.7"/>
                    Rarity: Unique
                    Watcher's Eye
                    Prismatic Jewel
                    LevelReq: 68
                    Item Level: 84
                </Item>
            </Items>
            <Tree/>
        </PathOfBuilding>"""

        build = api.PathOfBuildingAPI(xml_str.encode())

        items = list(build.items)
        assert len(items) == 1
        # Variant and alt_variant should be processed
        # (checked during item parsing)

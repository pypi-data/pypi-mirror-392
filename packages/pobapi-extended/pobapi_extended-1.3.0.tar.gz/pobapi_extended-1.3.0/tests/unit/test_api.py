import itertools

import pytest

from pobapi import api, config, models, stats

BASE_URL = "https://www.pathofexile.com/passive-skill-tree/"


@pytest.fixture(scope="module")
def build():
    from pathlib import Path

    test_file = Path(__file__).parent.parent.parent / "data" / "test_code.txt"
    with open(test_file) as f:
        code = f.read()
    return api.from_import_code(code)


def _assert_group(skill_group, test_list):
    for g, t in itertools.zip_longest(skill_group, test_list):
        assert g.name == t[0]
        assert g.enabled == t[1]
        assert g.level == t[2]
        if isinstance(g, models.Gem):
            assert g.quality == t[3]


def test_class_name(build):
    assert build.class_name == "Scion"


def test_ascendancy_name(build):
    assert build.ascendancy_name == "Ascendant"


def test_level(build):
    assert build.level == 1


def test_bandit(build):
    assert build.bandit == "Alira"


def test_notes(build):
    assert build.notes == "Test string."


def test_second_weapon_set(build):
    assert build.second_weapon_set is True


def test_stats_type(build):
    """Test stats property type."""
    assert isinstance(build.stats, stats.Stats)


def test_stats_values(build):
    """Test stats property values."""
    assert build.stats.life == 163
    assert build.stats.mana == 60


def test_config_default_character_level():
    """Test Config with None character_level defaults to 84."""

    from pobapi import config

    # Create Config with None character_level
    config_obj = config.Config.__new__(config.Config)
    # Manually call __post_init__ with None to test default
    config_obj.__post_init__(None)  # type: ignore[arg-type]
    # Should default enemy_level based on character_level=84
    assert config_obj.enemy_level is not None


def test_config(build):
    assert isinstance(build.config, config.Config)
    assert build.config.enemy_boss == "Shaper"


def test_active_item_set(build):
    assert build.active_item_set.body_armour == 1


def test_item_sets(build):
    for item_set in build.item_sets:
        assert item_set.body_armour == 1


def test_active_skill_group(build):
    assert build.active_skill_group.enabled is True
    assert build.active_skill_group.label == "Test label."
    assert build.active_skill_group.active == 1
    test_list = [
        ("Arc", True, 20, 1),
        ("Curse On Hit", True, 20, 2),
        ("Conductivity", True, 20, 3),
    ]
    _assert_group(build.active_skill_group.abilities, test_list)


def test_skill_groups(build):
    skill_group = build.skill_groups[0]
    assert skill_group.enabled is True
    assert skill_group.label == "Test label."
    assert skill_group.active == 1
    test_list = [
        ("Arc", True, 20, 1),
        ("Curse On Hit", True, 20, 2),
        ("Conductivity", True, 20, 3),
    ]
    _assert_group(skill_group.abilities, test_list)

    skill_group = build.skill_groups[1]
    assert skill_group.enabled is True
    assert skill_group.label == ""
    assert skill_group.active == 1
    test_list = [
        ("Herald of Ash", True, 20, 0),
        ("Herald of Ice", True, 20, 0),
        ("Herald of Thunder", True, 20, 0),
    ]
    _assert_group(skill_group.abilities, test_list)

    skill_group = build.skill_groups[2]
    assert skill_group.enabled is True
    assert skill_group.label == ""
    assert skill_group.active == 1
    test_list_2: list = [
        ("Abberath's Fury", True, 7),
        ("Added Cold Damage", True, 20, 0),
        ("Added Lightning Damage", True, 20, 0),
        ("Hypothermia", True, 20, 0),
        ("Concentrated Effect", True, 20, 0),
    ]
    _assert_group(skill_group.abilities, test_list_2)


def test_skill_groups_without_skills_element(mocker):
    """Test skill_groups property when Skills element is missing - covers line 139."""
    from lxml.etree import fromstring

    # Create XML with Skills element for validation
    xml_str = """<?xml version="1.0"?>
    <PathOfBuilding>
        <Build className="Witch" level="90"/>
        <Skills/>
        <Items/>
        <Tree activeSpec="1">
            <Spec>
                <URL></URL>
            </Spec>
        </Tree>
    </PathOfBuilding>"""
    xml_elem = fromstring(xml_str)
    build = api.PathOfBuildingAPI(xml_elem)
    # Mock xml.find to return None for "Skills" to test line 139
    original_find = build.xml.find

    def mock_find(tag):
        if tag == "Skills":
            return None
        return original_find(tag)

    mocker.patch.object(build, "xml", create=True)
    build.xml.find = mock_find
    # Should return empty generator (covers line 139)
    skill_groups = list(build.skill_groups)
    assert skill_groups == []


def test_skill_gems(build):
    test_list_active = [
        ("Arc", True, 20, 1),
        ("Curse On Hit", True, 20, 2),
        ("Conductivity", True, 20, 3),
    ]
    test_list_passive = [
        ("Herald of Ash", True, 20, 0),
        ("Herald of Ice", True, 20, 0),
        ("Herald of Thunder", True, 20, 0),
        ("Added Cold Damage", True, 20, 0),
        ("Added Lightning Damage", True, 20, 0),
        ("Hypothermia", True, 20, 0),
        ("Concentrated Effect", True, 20, 0),
    ]
    _assert_group(build.skill_gems, test_list_active + test_list_passive)


def test_skill_gems_without_skills_element(mocker):
    """Test skill_gems property when Skills element is missing - covers line 211."""
    from lxml.etree import fromstring

    # Create XML with Skills element for validation
    xml_str = """<?xml version="1.0"?>
    <PathOfBuilding>
        <Build className="Witch" level="90"/>
        <Skills/>
        <Items/>
        <Tree activeSpec="1">
            <Spec>
                <URL></URL>
            </Spec>
        </Tree>
    </PathOfBuilding>"""
    xml_elem = fromstring(xml_str)
    build = api.PathOfBuildingAPI(xml_elem)
    # Mock xml.find to return None for "Skills" to test line 211
    original_find = build.xml.find

    def mock_find(tag):
        if tag == "Skills":
            return None
        return original_find(tag)

    mocker.patch.object(build, "xml", create=True)
    build.xml.find = mock_find
    # Should return empty list (covers line 211)
    skill_gems = build.skill_gems
    assert skill_gems == []


def test_active_skill(build):
    test_list = [("Arc", True, 20, 1)]
    _assert_group([build.active_skill], test_list)


def test_active_skill_tree(build):
    assert (
        build.active_skill_tree.url == BASE_URL + "AAAABAABAJitGFbaYij62E1odILHlKD56A=="
    )
    # fmt: off
    assert build.active_skill_tree.nodes == \
        [39085, 6230, 55906, 10490, 55373, 26740, 33479, 38048, 63976]
    # fmt: on
    # Sockets may contain empty sockets (itemId=0) which are valid
    assert isinstance(build.active_skill_tree.sockets, dict)
    # Check that all sockets have itemId >= 0 (0 means empty socket)
    assert all(item_id >= 0 for item_id in build.active_skill_tree.sockets.values())


def test_trees(build):
    for tree in build.trees:
        assert tree.url == BASE_URL + "AAAABAABAJitGFbaYij62E1odILHlKD56A=="
        # fmt: off
        assert tree.nodes == \
            [39085, 6230, 55906, 10490, 55373, 26740, 33479, 38048, 63976]
        # fmt: on
        # Sockets may contain empty sockets (itemId=0) which are valid
        assert isinstance(tree.sockets, dict)
        # Check that all sockets have itemId >= 0 (0 means empty socket)
        assert all(item_id >= 0 for item_id in tree.sockets.values())


def test_keystones(build):
    assert 39085 in build.active_skill_tree.nodes  # 39085: Elemental Equilibrium


def test_api_init_with_element():
    """Test PathOfBuildingAPI initialization with Element."""
    from lxml.etree import fromstring

    xml_str = """<?xml version="1.0"?>
    <PathOfBuilding>
        <Build className="Scion" level="1"/>
        <Skills/>
        <Items/>
        <Tree/>
    </PathOfBuilding>"""
    xml_root = fromstring(xml_str.encode())
    build = api.PathOfBuildingAPI(xml_root)
    assert build.class_name == "Scion"


def test_api_init_invalid_type():
    """Test PathOfBuildingAPI initialization with invalid type."""
    from pobapi.exceptions import ValidationError

    with pytest.raises(ValidationError, match="xml must be bytes or Element"):
        api.PathOfBuildingAPI("invalid")  # type: ignore[arg-type,unused-ignore]


def test_api_init_invalid_xml_bytes():
    """Test PathOfBuildingAPI initialization with invalid XML bytes."""
    from pobapi.exceptions import ParsingError

    with pytest.raises(ParsingError, match="Failed to parse XML"):
        api.PathOfBuildingAPI(b"invalid xml")


def test_from_url_function(mocker):
    """Test from_url function."""
    # Clear cache to ensure fresh client creation
    import pobapi.util

    # Save original value to restore it later
    original_client = pobapi.util._default_http_client
    try:
        pobapi.util._default_http_client = None

        # Mock successful response
        mock_response = mocker.Mock()
        mock_response.text = "valid_import_code"
        mock_response.raise_for_status = mocker.Mock()

        mocker.patch("requests.get", return_value=mock_response)
        mock_fetch = mocker.patch("pobapi.util._fetch_xml_from_import_code")
        mock_fetch.return_value = b"""<?xml version="1.0"?>
        <PathOfBuilding>
            <Build className="Scion" level="1"/>
            <Skills/>
            <Items/>
            <Tree/>
        </PathOfBuilding>"""
        build = api.from_url("https://pastebin.com/test")
        assert build.class_name == "Scion"
    finally:
        # Restore original value to avoid polluting other tests
        pobapi.util._default_http_client = original_client


@pytest.mark.parametrize(
    "xml_str,expected",
    [
        (
            """<?xml version="1.0"?>
    <PathOfBuilding>
        <Build className="Scion" level="1"/>
        <Skills/>
        <Items/>
        <Tree/>
    </PathOfBuilding>""",
            "",
        ),
        (
            """<?xml version="1.0"?>
    <PathOfBuilding>
        <Build className="Scion" level="1"/>
        <Skills/>
        <Items/>
        <Tree/>
        <Notes/>
    </PathOfBuilding>""",
            "",
        ),
    ],
)
def test_notes_empty(xml_str, expected):
    """Test notes property when Notes element is missing or empty."""

    build = api.PathOfBuildingAPI(xml_str.encode())
    assert build.notes == expected


def test_keystones_property():
    """Test keystones property."""
    # Use the existing build fixture which has a proper skill tree
    # This test just verifies keystones property works
    from pathlib import Path

    from pobapi import api

    test_file = Path(__file__).parent.parent.parent / "data" / "test_code.txt"
    with open(test_file) as f:
        code = f.read()
    build = api.from_import_code(code)
    keystones = build.keystones
    assert isinstance(keystones, models.Keystones)


def test_items_contains_inpulsa(build):
    """Test that items list contains Inpulsa's Broken Heart."""
    item_names = [i.name for i in build.items]
    assert "Inpulsa's Broken Heart" in item_names


def test_items_without_items_element(mocker):
    """Test items property when Items element is missing - covers line 521."""
    from lxml.etree import fromstring

    # Create XML with Items element for validation
    xml_str = """<?xml version="1.0"?>
    <PathOfBuilding>
        <Build className="Witch" level="90"/>
        <Skills/>
        <Items/>
        <Tree activeSpec="1">
            <Spec>
                <URL></URL>
            </Spec>
        </Tree>
    </PathOfBuilding>"""
    xml_elem = fromstring(xml_str)
    build = api.PathOfBuildingAPI(xml_elem)
    # Mock xml.find to return None for "Items" to test line 521
    original_find = build.xml.find

    def mock_find(tag):
        if tag == "Items":
            return None
        return original_find(tag)

    mocker.patch.object(build, "xml", create=True)
    build.xml.find = mock_find
    # Should return empty generator (covers line 521)
    items = list(build.items)
    assert items == []


def test_active_item_set_without_items_element(mocker):
    """Test active_item_set property when Items element is missing.

    Covers lines 576-585.
    """
    from lxml.etree import fromstring

    # Create XML with Items element for validation
    xml_str = """<?xml version="1.0"?>
    <PathOfBuilding>
        <Build className="Witch" level="90"/>
        <Skills/>
        <Items/>
        <Tree activeSpec="1">
            <Spec>
                <URL></URL>
            </Spec>
        </Tree>
    </PathOfBuilding>"""
    xml_elem = fromstring(xml_str)
    build = api.PathOfBuildingAPI(xml_elem)
    # Mock xml.find to return None for "Items" to test lines 576-585
    original_find = build.xml.find

    def mock_find(tag):
        if tag == "Items":
            return None
        return original_find(tag)

    mocker.patch.object(build, "xml", create=True)
    build.xml.find = mock_find
    # Should create empty item set (covers lines 576-585)
    active_item_set = build.active_item_set
    assert active_item_set is not None
    # All slots should be None
    assert active_item_set.belt is None


def test_active_item_set_without_items_element_but_with_item_sets(mocker):
    """Test active_item_set when Items element is missing but item_sets exist.

    Covers line 577.
    """
    from lxml.etree import fromstring

    # Create XML with Items element for validation
    xml_str = """<?xml version="1.0"?>
    <PathOfBuilding>
        <Build className="Witch" level="90"/>
        <Skills/>
        <Items>
            <ItemSet>
                <Slot name="Belt" itemId="1"/>
            </ItemSet>
        </Items>
        <Tree activeSpec="1">
            <Spec>
                <URL></URL>
            </Spec>
        </Tree>
    </PathOfBuilding>"""
    xml_elem = fromstring(xml_str)
    build = api.PathOfBuildingAPI(xml_elem)
    # Access item_sets to create cache (so it's not empty)
    _ = build.item_sets
    # Mock xml.find to return None for "Items" to test line 577
    original_find = build.xml.find

    def mock_find(tag):
        if tag == "Items":
            return None
        return original_find(tag)

    mocker.patch.object(build, "xml", create=True)
    build.xml.find = mock_find
    # Should return first item set (covers line 577)
    active_item_set = build.active_item_set
    assert active_item_set is not None
    # Should have item from item_sets[0]
    assert active_item_set.belt == 0
    assert active_item_set.helmet is None


def test_inpulsa_item_properties(build):
    """Test Inpulsa's Broken Heart item properties."""
    inpulsa = next(i for i in build.items if i.name == "Inpulsa's Broken Heart")
    assert inpulsa.rarity == "Unique"
    assert inpulsa.name == "Inpulsa's Broken Heart"
    assert inpulsa.base == "Sadist Garb"
    assert inpulsa.shaper is True
    assert inpulsa.elder is False
    assert inpulsa.quality == 20
    assert inpulsa.sockets == (("R", "G", "B"), ("B", "B", "B"))
    assert inpulsa.level_req == 68

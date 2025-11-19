"""Integration tests for ItemCraftingAPI and PathOfBuildingAPI components."""

import pytest

pytestmark = pytest.mark.integration

from pobapi import PathOfBuildingAPI  # noqa: E402
from pobapi.crafting import (  # noqa: E402
    CraftingModifier,
    ItemCraftingAPI,
)

# Valid base item types for Path of Building
VALID_BASE_TYPES = [
    "Leather Belt",
    "Iron Ring",
    "Simple Robe",
    "Vaal Gauntlets",
    "Coral Ring",
    "Topaz Ring",
    "Sapphire Ring",
    "Ruby Ring",
    "Amethyst Ring",
    "Two-Stone Ring",
]


class TestCraftingAPIPathOfBuildingAPIIntegration:
    """Test integration between ItemCraftingAPI and PathOfBuildingAPI."""

    def test_craft_item_and_add_to_build(self, build: PathOfBuildingAPI) -> None:
        """Test crafting an item and adding it to build."""
        # Get available modifiers
        prefixes_list = ItemCraftingAPI.get_modifiers_by_type("prefix", item_level=84)
        suffixes_list = ItemCraftingAPI.get_modifiers_by_type("suffix", item_level=84)

        if not prefixes_list or not suffixes_list:
            pytest.skip("No modifiers available in database")

        # Create crafting modifiers
        prefix_mod = CraftingModifier(
            modifier=prefixes_list[0], roll_value=prefixes_list[0].max_value
        )
        suffix_mod = CraftingModifier(
            modifier=suffixes_list[0], roll_value=suffixes_list[0].max_value
        )

        # Craft item
        result = ItemCraftingAPI.craft_item(
            base_item_type="Leather Belt",
            item_level=84,
            prefixes=[prefix_mod],
            suffixes=[suffix_mod],
        )

        assert result.success is True
        assert result.item_text != ""

        # Create Item from crafted item_text
        from pobapi.models import Item

        crafted_item = Item(
            name="Crafted Belt",
            base="Leather Belt",
            rarity="Rare",
            uid="crafted-1",
            shaper=False,
            elder=False,
            crafted=True,
            quality=None,
            sockets=None,
            level_req=1,
            item_level=84,
            implicit=None,
            text=result.item_text,
        )
        build._modifier.equip_item(crafted_item, "Belt")

        # Verify item was added
        items = list(build.items)
        assert any(item.uid == "crafted-1" for item in items)

    def test_craft_item_with_modifiers_from_build_stats(
        self, build: PathOfBuildingAPI
    ) -> None:
        """Test crafting item with modifiers based on build stats."""
        from pobapi import CalculationEngine

        # Calculate build stats (for context, not used directly)
        engine = CalculationEngine()
        engine.load_build(build)
        engine.calculate_all_stats(build_data=build)

        # Get modifiers that would benefit the build
        # For example, if build has low life, craft life modifiers
        life_modifiers = ItemCraftingAPI.get_modifiers_by_stat(
            "Life", item_level=84, tags=["life", "defense"]
        )

        if not life_modifiers:
            pytest.skip("No life modifiers available")

        # Craft item with life modifier
        crafting_mod = CraftingModifier(
            modifier=life_modifiers[0], roll_value=life_modifiers[0].max_value
        )

        result = ItemCraftingAPI.craft_item(
            base_item_type="Leather Belt",
            item_level=84,
            prefixes=[crafting_mod],
        )

        assert result.success is True

        # Create Item from crafted item_text
        from pobapi.models import Item

        crafted_item = Item(
            name="Crafted Belt",
            base="Leather Belt",
            rarity="Rare",
            uid="crafted-life-1",
            shaper=False,
            elder=False,
            crafted=True,
            quality=None,
            sockets=None,
            level_req=1,
            item_level=84,
            implicit=None,
            text=result.item_text,
        )
        build._modifier.equip_item(crafted_item, "Belt")

        # Verify integration
        items = list(build.items)
        assert any(item.uid == "crafted-life-1" for item in items)

    def test_craft_item_and_serialize_build(self, build: PathOfBuildingAPI) -> None:
        """Test crafting item, adding to build, and serializing."""
        # Craft an item
        prefixes_list = ItemCraftingAPI.get_modifiers_by_type("prefix", item_level=84)

        if not prefixes_list:
            pytest.skip("No modifiers available in database")

        crafting_mod = CraftingModifier(
            modifier=prefixes_list[0], roll_value=prefixes_list[0].max_value
        )

        result = ItemCraftingAPI.craft_item(
            base_item_type="Iron Ring",
            item_level=84,
            prefixes=[crafting_mod],
        )

        assert result.success is True

        # Create Item from crafted item_text
        from pobapi.models import Item

        crafted_item = Item(
            name="Crafted Ring",
            base="Iron Ring",
            rarity="Rare",
            uid="crafted-ring-1",
            shaper=False,
            elder=False,
            crafted=True,
            quality=None,
            sockets=None,
            level_req=1,
            item_level=84,
            implicit=None,
            text=result.item_text,
        )
        build.equip_item(crafted_item, "Ring1")

        # Serialize build
        xml = build.to_xml()
        assert xml is not None
        assert len(xml) > 0

        # Verify crafted item is in serialized XML
        from lxml.etree import fromstring

        xml_root = fromstring(xml)
        items_elem = xml_root.find("Items")
        assert items_elem is not None

        # Find the crafted item by uid attribute
        crafted_item_elem = items_elem.xpath('.//Item[@uid="crafted-ring-1"]')
        assert (
            len(crafted_item_elem) > 0
        ), "Crafted item with uid='crafted-ring-1' not found in serialized XML"

        # Verify the found element is an Item
        assert crafted_item_elem[0].tag == "Item", "Found element is not an Item"

        # Optionally verify the item has expected attributes or children
        assert crafted_item_elem[0].get("uid") == "crafted-ring-1"

    def test_craft_multiple_items_for_build(self, build: PathOfBuildingAPI) -> None:
        """Test crafting multiple items and adding them to build."""
        prefixes_list = ItemCraftingAPI.get_modifiers_by_type("prefix", item_level=84)

        if not prefixes_list:
            pytest.skip("No modifiers available in database")

        # Craft multiple items
        crafted_items = []
        for i, prefix_mod in enumerate(prefixes_list[:3]):  # Craft 3 items
            crafting_mod = CraftingModifier(
                modifier=prefix_mod, roll_value=prefix_mod.max_value
            )

            base_type = VALID_BASE_TYPES[i % len(VALID_BASE_TYPES)]
            result = ItemCraftingAPI.craft_item(
                base_item_type=base_type,
                item_level=84,
                prefixes=[crafting_mod],
            )

            if result.success:
                from pobapi.models import Item

                crafted_item = Item(
                    name=f"Crafted {base_type}",
                    base=base_type,
                    rarity="Rare",
                    uid=f"crafted-{i}",
                    shaper=False,
                    elder=False,
                    crafted=True,
                    quality=None,
                    sockets=None,
                    level_req=1,
                    item_level=84,
                    implicit=None,
                    text=result.item_text,
                )
                crafted_items.append(crafted_item)

        # Add all to build
        slots = ["Ring1", "Ring2", "Amulet"]
        for item, slot in zip(crafted_items, slots):
            build._modifier.equip_item(item, slot)

        # Verify all items were added
        items = list(build.items)
        assert len(items) >= len(crafted_items)

    def test_craft_item_with_build_config_requirements(
        self, build: PathOfBuildingAPI
    ) -> None:
        """Test crafting item considering build config requirements."""
        # Get build config
        config = build.config

        # Determine item level based on config
        item_level = 84
        if config and hasattr(config, "enemy_level"):
            # Use enemy level as minimum item level
            item_level = max(84, getattr(config, "enemy_level", 84) or 84)

        # Craft item with appropriate level
        prefixes_list = ItemCraftingAPI.get_modifiers_by_type(
            "prefix", item_level=item_level
        )

        if not prefixes_list:
            pytest.skip("No modifiers available in database")

        crafting_mod = CraftingModifier(
            modifier=prefixes_list[0], roll_value=prefixes_list[0].max_value
        )

        result = ItemCraftingAPI.craft_item(
            base_item_type="Leather Belt",
            item_level=item_level,
            prefixes=[crafting_mod],
        )

        assert result.success is True
        assert result.item_text != ""

    def test_craft_item_and_calculate_stats(self, build: PathOfBuildingAPI) -> None:
        """Test crafting item, adding to build, and recalculating stats."""
        from pobapi import CalculationEngine

        # Get initial stats
        engine = CalculationEngine()
        engine.load_build(build)
        initial_stats = engine.calculate_all_stats(build_data=build)

        # Craft item with life modifier
        life_modifiers = ItemCraftingAPI.get_modifiers_by_stat("Life", item_level=84)

        if not life_modifiers:
            pytest.skip("No life modifiers available")

        crafting_mod = CraftingModifier(
            modifier=life_modifiers[0], roll_value=life_modifiers[0].max_value
        )

        result = ItemCraftingAPI.craft_item(
            base_item_type="Leather Belt",
            item_level=84,
            prefixes=[crafting_mod],
        )

        assert result.success is True

        # Create Item from crafted item_text
        from pobapi.models import Item

        crafted_item = Item(
            name="Crafted Belt",
            base="Leather Belt",
            rarity="Rare",
            uid="crafted-stats-1",
            shaper=False,
            elder=False,
            crafted=True,
            quality=None,
            sockets=None,
            level_req=1,
            item_level=84,
            implicit=None,
            text=result.item_text,
        )
        build._modifier.equip_item(crafted_item, "Belt")

        # Recalculate stats
        engine.load_build(build)
        new_stats = engine.calculate_all_stats(build_data=build)

        # Stats should be different (or at least calculated)
        assert new_stats is not None
        assert initial_stats is not None

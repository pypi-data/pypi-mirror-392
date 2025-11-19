"""Serializers for Path of Building data formats."""

from __future__ import annotations

import base64
import zlib
from typing import TYPE_CHECKING

from lxml.etree import Element, SubElement, tostring

from pobapi import models
from pobapi.build_builder import BuildBuilder

if TYPE_CHECKING:
    from pobapi.api import PathOfBuildingAPI

__all__ = ["BuildXMLSerializer", "ImportCodeGenerator"]


class BuildXMLSerializer:
    """Serializer for converting build data to XML format."""

    @staticmethod
    def serialize(builder: BuildBuilder) -> Element:
        """Serialize BuildBuilder to XML Element.

        :param builder: BuildBuilder instance.
        :return: XML Element representing the build.
        """
        # Create root element
        root = Element("PathOfBuilding")

        # Build section
        build_elem = SubElement(root, "Build")
        build_elem.set("className", builder.class_name)
        if builder.ascendancy_name:
            build_elem.set("ascendClassName", builder.ascendancy_name)
        build_elem.set("level", str(builder.level))
        if builder.bandit:
            build_elem.set("bandit", builder.bandit)
        if builder.main_socket_group is not None:
            build_elem.set("mainSocketGroup", str(builder.main_socket_group))

        # Skills section
        skills_elem = SubElement(root, "Skills")
        for skill_group in builder.skill_groups:
            skill_elem = SubElement(skills_elem, "Skill")
            skill_elem.set("enabled", "true" if skill_group.enabled else "false")
            skill_elem.set("label", skill_group.label)
            if skill_group.active is not None:
                skill_elem.set("mainActiveSkill", str(skill_group.active))

            for ability in skill_group.abilities:
                if isinstance(ability, models.Gem):
                    ability_elem = SubElement(skill_elem, "Ability")
                    # Set nameSpec (primary name field used by parser)
                    ability_elem.set("nameSpec", ability.name)
                    ability_elem.set("name", ability.name)  # For compatibility
                    ability_elem.set("enabled", "true" if ability.enabled else "false")
                    ability_elem.set("level", str(ability.level))
                    ability_elem.set("quality", str(ability.quality))
                    # Set gemId and skillId for proper parsing
                    ability_elem.set("gemId", "1")  # Indicates this is a gem
                    if ability.support:
                        ability_elem.set("support", "true")
                        ability_elem.set(
                            "skillId", f"Support{ability.name.replace(' ', '')}"
                        )
                    else:
                        ability_elem.set("skillId", ability.name.replace(" ", ""))
                elif isinstance(ability, models.GrantedAbility):
                    ability_elem = SubElement(skill_elem, "Ability")
                    ability_elem.set("name", ability.name)
                    ability_elem.set("enabled", "true" if ability.enabled else "false")
                    ability_elem.set("level", str(ability.level))
                    if ability.quality is not None:
                        ability_elem.set("quality", str(ability.quality))
                    ability_elem.set("granted", "true")

        # Items section
        items_elem = SubElement(root, "Items")
        # Set activeItemSet attribute (required by parser)
        items_elem.set("activeItemSet", "1")  # 1-based index, default to first set
        for item in builder.items:
            item_elem = SubElement(items_elem, "Item")
            # Set item text - generate proper format if text is empty
            if item.text:
                item_elem.text = item.text
            else:
                # Generate proper item text format from item properties
                # This ensures name and base can be parsed correctly
                item_text_lines = [
                    f"Rarity: {item.rarity}",
                    item.name,
                    item.base,
                ]
                if item.shaper:
                    item_text_lines.append("Shaper Item")
                if item.elder:
                    item_text_lines.append("Elder Item")
                if item.crafted:
                    item_text_lines.append("{crafted}")
                if item.quality is not None:
                    item_text_lines.append(f"Quality: {item.quality}")
                if item.sockets:
                    sockets_str = " ".join("-".join(group) for group in item.sockets)
                    item_text_lines.append(f"Sockets: {sockets_str}")
                if item.level_req is not None:
                    item_text_lines.append(f"LevelReq: {item.level_req}")
                if item.item_level is not None:
                    item_text_lines.append(f"Item Level: {item.item_level}")
                if item.implicit:
                    item_text_lines.append(f"Implicits: {item.implicit}")
                if item.uid:
                    item_text_lines.append(f"Unique ID: {item.uid}")
                item_elem.text = "\n".join(item_text_lines)

        # Item sets
        for item_set in builder.item_sets:
            item_set_elem = SubElement(items_elem, "ItemSet")

            # Map Set attributes to slot names
            slot_mapping = {
                "weapon1": "Weapon1",
                "weapon1_swap": "Weapon1 Swap",
                "weapon2": "Weapon2",
                "weapon2_swap": "Weapon2 Swap",
                "helmet": "Helmet",
                "body_armour": "Body Armour",
                "gloves": "Gloves",
                "boots": "Boots",
                "amulet": "Amulet",
                "ring1": "Ring1",
                "ring2": "Ring2",
                "belt": "Belt",
                "flask1": "Flask1",
                "flask2": "Flask2",
                "flask3": "Flask3",
                "flask4": "Flask4",
                "flask5": "Flask5",
            }

            for attr_name, slot_name in slot_mapping.items():
                item_id = getattr(item_set, attr_name)
                if item_id is not None:
                    slot_elem = SubElement(item_set_elem, "Slot")
                    slot_elem.set("name", slot_name)
                    # item_id in Set is 0-based, convert to 1-based for XML
                    slot_elem.set("itemId", str(item_id + 1))

        # Config section
        # Serialize config - this would need to be implemented based on config structure
        # For now, just create empty config
        SubElement(root, "Config")

        # Tree section
        tree_elem = SubElement(root, "Tree")
        tree_elem.set("activeSpec", str(builder.active_spec))

        for tree in builder.trees:
            spec_elem = SubElement(tree_elem, "Spec")
            # Always add URL element, even if empty (required by parser)
            url_elem = SubElement(spec_elem, "URL")
            url_elem.text = tree.url if tree.url else ""

            # Add nodes
            if tree.nodes:
                nodes_elem = SubElement(spec_elem, "Nodes")
                for node_id in tree.nodes:
                    node_elem = SubElement(nodes_elem, "Node")
                    node_elem.set("id", str(node_id))

            # Add sockets
            for socket_id, item_id in tree.sockets.items():
                socket_elem = SubElement(spec_elem, "Socket")
                socket_elem.set("nodeId", str(socket_id))
                # item_id in Tree.sockets is 0-based, convert to 1-based for XML
                socket_elem.set("itemId", str(item_id + 1))

        # Notes section
        if builder.notes:
            notes_elem = SubElement(root, "Notes")
            notes_elem.text = builder.notes

        return root

    @staticmethod
    def serialize_from_api(api: PathOfBuildingAPI) -> Element:
        """Serialize PathOfBuildingAPI instance to XML Element.

        This method reconstructs XML from an existing PathOfBuildingAPI instance.

        :param api: PathOfBuildingAPI instance.
        :return: XML Element representing the build.
        """
        # Create root element
        root = Element("PathOfBuilding")

        # Build section
        build_elem = SubElement(root, "Build")
        build_elem.set("className", api.class_name)
        if api.ascendancy_name:
            build_elem.set("ascendClassName", api.ascendancy_name)
        build_elem.set("level", str(api.level))
        if api.bandit:
            build_elem.set("bandit", api.bandit)
        # main_socket_group is a property, check if it exists and has value
        main_socket_group = getattr(api, "main_socket_group", None)
        if main_socket_group is not None:
            build_elem.set("mainSocketGroup", str(main_socket_group))

        # Skills section
        skills_elem = SubElement(root, "Skills")
        for skill_group in api.skill_groups:
            skill_elem = SubElement(skills_elem, "Skill")
            skill_elem.set("enabled", "true" if skill_group.enabled else "false")
            skill_elem.set("label", skill_group.label)
            if skill_group.active is not None:
                skill_elem.set("mainActiveSkill", str(skill_group.active))

            for ability in skill_group.abilities:
                if isinstance(ability, models.Gem):
                    ability_elem = SubElement(skill_elem, "Ability")
                    # Set nameSpec (primary name field used by parser)
                    ability_elem.set("nameSpec", ability.name)
                    ability_elem.set("name", ability.name)  # For compatibility
                    ability_elem.set("enabled", "true" if ability.enabled else "false")
                    ability_elem.set("level", str(ability.level))
                    ability_elem.set("quality", str(ability.quality))
                    # Set gemId and skillId for proper parsing
                    ability_elem.set("gemId", "1")  # Indicates this is a gem
                    if ability.support:
                        ability_elem.set("support", "true")
                        ability_elem.set(
                            "skillId", f"Support{ability.name.replace(' ', '')}"
                        )
                    else:
                        ability_elem.set("skillId", ability.name.replace(" ", ""))
                elif isinstance(ability, models.GrantedAbility):
                    ability_elem = SubElement(skill_elem, "Ability")
                    ability_elem.set("name", ability.name)
                    ability_elem.set("enabled", "true" if ability.enabled else "false")
                    ability_elem.set("level", str(ability.level))
                    if ability.quality is not None:
                        ability_elem.set("quality", str(ability.quality))
                    ability_elem.set("granted", "true")

        # Items section
        items_elem = SubElement(root, "Items")
        # Set activeItemSet attribute (required by parser)
        items_elem.set("activeItemSet", "1")  # 1-based index, default to first set
        # Add existing items
        for item in api.items:
            item_elem = SubElement(items_elem, "Item")
            if item.text:
                item_elem.text = item.text
            # Add uid as attribute if present
            if item.uid:
                item_elem.set("uid", item.uid)
        # Add pending items (from equip_item calls)
        if hasattr(api, "_pending_items"):
            for item in api._pending_items:
                item_elem = SubElement(items_elem, "Item")
                if item.text:
                    item_elem.text = item.text
                # Add uid as attribute if present
                if item.uid:
                    item_elem.set("uid", item.uid)

        # Item sets
        for item_set in api.item_sets:
            item_set_elem = SubElement(items_elem, "ItemSet")

            slot_mapping = {
                "weapon1": "Weapon1",
                "weapon1_swap": "Weapon1 Swap",
                "weapon2": "Weapon2",
                "weapon2_swap": "Weapon2 Swap",
                "helmet": "Helmet",
                "body_armour": "Body Armour",
                "gloves": "Gloves",
                "boots": "Boots",
                "amulet": "Amulet",
                "ring1": "Ring1",
                "ring2": "Ring2",
                "belt": "Belt",
                "flask1": "Flask1",
                "flask2": "Flask2",
                "flask3": "Flask3",
                "flask4": "Flask4",
                "flask5": "Flask5",
            }

            for attr_name, slot_name in slot_mapping.items():
                item_id = getattr(item_set, attr_name)
                if item_id is not None:
                    slot_elem = SubElement(item_set_elem, "Slot")
                    slot_elem.set("name", slot_name)
                    # item_id in Set from XML parser is 0-based,
                    # but we need 1-based for XML
                    # Check if it's already 1-based (from XML) or
                    # 0-based (from builder)
                    # Since we're serializing from API, it's 0-based
                    # from parser
                    slot_elem.set("itemId", str(item_id + 1))

        # Config section
        # Config serialization would need to be implemented based on config structure
        SubElement(root, "Config")

        # Tree section
        tree_elem = SubElement(root, "Tree")
        tree_elem.set("activeSpec", "1")  # Default

        for tree in api.trees:
            spec_elem = SubElement(tree_elem, "Spec")
            if tree.url:
                url_elem = SubElement(spec_elem, "URL")
                url_elem.text = tree.url

            # Add nodes
            if tree.nodes:
                nodes_elem = SubElement(spec_elem, "Nodes")
                for node_id in tree.nodes:
                    node_elem = SubElement(nodes_elem, "Node")
                    node_elem.set("id", str(node_id))

            # Add sockets
            for socket_id, item_id in tree.sockets.items():
                socket_elem = SubElement(spec_elem, "Socket")
                socket_elem.set("nodeId", str(socket_id))
                socket_elem.set("itemId", str(item_id))

        # Notes section
        if api.notes:
            notes_elem = SubElement(root, "Notes")
            notes_elem.text = api.notes

        return root


class ImportCodeGenerator:
    """Generator for Path of Building import codes."""

    @staticmethod
    def generate(xml_element: Element) -> str:
        """Generate import code from XML Element.

        :param xml_element: XML Element representing the build.
        :return: Import code string.
        """
        # Convert XML to bytes
        xml_bytes = tostring(
            xml_element, encoding="utf-8", xml_declaration=True, pretty_print=False
        )

        # Compress with zlib
        compressed = zlib.compress(xml_bytes, level=9)

        # Encode to base64
        import_code = base64.urlsafe_b64encode(compressed).decode("ascii")

        return import_code

    @staticmethod
    def generate_from_builder(builder: BuildBuilder) -> str:
        """Generate import code from BuildBuilder.

        :param builder: BuildBuilder instance.
        :return: Import code string.
        """
        xml_element = BuildXMLSerializer.serialize(builder)
        return ImportCodeGenerator.generate(xml_element)

    @staticmethod
    def generate_from_api(api: PathOfBuildingAPI) -> str:
        """Generate import code from PathOfBuildingAPI.

        :param api: PathOfBuildingAPI instance.
        :return: Import code string.
        """
        xml_element = BuildXMLSerializer.serialize_from_api(api)
        return ImportCodeGenerator.generate(xml_element)

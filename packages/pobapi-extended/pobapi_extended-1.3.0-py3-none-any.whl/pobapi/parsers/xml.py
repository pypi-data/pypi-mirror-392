"""XML parsers for different parts of Path of Building data."""

import logging

from lxml.etree import Element

from pobapi.exceptions import ParsingError
from pobapi.interfaces import BuildParser
from pobapi.util import _get_stat, _get_text, _skill_tree_nodes

logger = logging.getLogger(__name__)

__all__ = [
    "DefaultBuildParser",
    "BuildInfoParser",
    "SkillsParser",
    "ItemsParser",
    "TreesParser",
]


def _safe_int(value: str | bool | None, default: int | None = 0) -> int | None:
    """Safely convert a value to int, returning default on failure.

    :param value: Value to convert to int.
    :param default: Default value to return if conversion fails.
    :return: Converted integer or default value.
    """
    if not value or value is True:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


class BuildInfoParser:
    """Parser for build information (class, level, etc.)."""

    @staticmethod
    def parse(xml_root: Element) -> dict[str, str | None]:
        """Parse build information from XML root.

        :param xml_root: Root XML element.
        :return: Dictionary with build information.
        :raises: ParsingError if build element not found.
        """
        build_element = xml_root.find("Build")
        if build_element is None:
            raise ParsingError("Build element not found in XML")

        return {
            "class_name": build_element.get("className"),
            "ascendancy_name": build_element.get("ascendClassName"),
            "level": build_element.get("level"),
            "bandit": build_element.get("bandit"),
            "main_socket_group": build_element.get("mainSocketGroup"),
        }


class SkillsParser:
    """Parser for skills and skill groups."""

    @staticmethod
    def _parse_skill_element(skill: Element) -> dict:
        """Parse a single Skill element into a dictionary.

        :param skill: Skill XML element.
        :return: Dictionary with skill data (enabled, label,
            main_active_skill, source, abilities).
        """
        main_active = skill.get("mainActiveSkill")
        main_active_skill = None
        if main_active and main_active != "nil" and main_active.strip():
            try:
                main_active_skill = int(main_active)
            except ValueError:
                logger.warning(
                    f"Invalid mainActiveSkill value '{main_active}' "
                    f"for skill '{skill.get('label')}', expected integer"
                )
        return {
            "enabled": skill.get("enabled") == "true",
            "label": skill.get("label"),
            "main_active_skill": main_active_skill,
            "source": skill.get("source"),
            "abilities": list(skill),
        }

    @staticmethod
    def parse_skill_groups(xml_root: Element) -> list[dict]:
        """Parse skill groups from XML.

        :param xml_root: Root XML element.
        :return: List of skill group dictionaries.
        """
        skills_element = xml_root.find("Skills")
        if skills_element is None:
            return []

        skill_groups = []
        # Handle new structure with SkillSet (Path of Building 2.0+)
        skill_sets = skills_element.findall("SkillSet")
        if skill_sets:
            # New structure: Skills -> SkillSet -> Skill
            for skill_set in skill_sets:
                for skill in skill_set.findall("Skill"):
                    skill_groups.append(SkillsParser._parse_skill_element(skill))
        else:
            # Old structure: Skills -> Skill (direct)
            for skill in skills_element.findall("Skill"):
                skill_groups.append(SkillsParser._parse_skill_element(skill))
        return skill_groups


class ItemsParser:
    """Parser for items."""

    @staticmethod
    def parse_items(xml_root: Element) -> list[dict]:
        """Parse items from XML.

        :param xml_root: Root XML element.
        :return: List of item dictionaries.
        """
        items_element = xml_root.find("Items")
        if items_element is None:
            return []

        items = []
        for item_element in items_element.findall("Item"):
            variant = item_element.get("variant")
            alt_variant = item_element.get("variantAlt")
            mod_ranges = []
            for mod_range_element in item_element.findall("ModRange"):
                range_attr = mod_range_element.get("range")
                if range_attr is None:
                    logger.warning(
                        "ModRange element missing 'range' attribute, skipping"
                    )
                    continue
                try:
                    mod_ranges.append(float(range_attr))
                except (ValueError, TypeError) as e:
                    logger.warning(
                        f"Failed to parse ModRange 'range' attribute "
                        f"'{range_attr}' as float: {e}, skipping"
                    )
            item_text = (
                item_element.text.strip("\n\r\t").splitlines()
                if item_element.text
                else []
            )
            # Strip leading/trailing whitespace from each line
            item_text = [line.strip() for line in item_text if line.strip()]

            rarity_stat = _get_stat(item_text, "Rarity: ")
            # _get_stat returns empty string if not found, or the value after "Rarity: "
            if isinstance(rarity_stat, str) and rarity_stat and rarity_stat != "":
                rarity = rarity_stat.capitalize()
            else:
                rarity = "Normal"
            name = item_text[1] if len(item_text) > 1 else ""
            # For items with variant, name might be empty, use base as fallback
            if not name and variant is not None:
                name = item_text[2] if len(item_text) > 2 else "Unknown"
            base = (
                name
                if rarity in ("Normal", "Magic")
                else (item_text[2] if len(item_text) > 2 else name or "Unknown")
            )
            uid = _get_stat(item_text, "Unique ID: ")
            shaper = bool(_get_stat(item_text, "Shaper Item"))
            elder = bool(_get_stat(item_text, "Elder Item"))
            crafted = bool(_get_stat(item_text, "{crafted}"))
            _quality = _get_stat(item_text, "Quality: ")
            quality = _safe_int(_quality, None) if _quality else None
            _sockets = _get_stat(item_text, "Sockets: ")
            sockets = (
                tuple(tuple(group.split("-")) for group in _sockets.split())
                if isinstance(_sockets, str) and _sockets
                else None
            )
            level_req = _safe_int(_get_stat(item_text, "LevelReq: "), 0)
            item_level = _safe_int(_get_stat(item_text, "Item Level: "), 1)
            implicit = _safe_int(_get_stat(item_text, "Implicits: "), 0)
            item_text_processed = _get_text(item_text, variant, alt_variant, mod_ranges)

            items.append(
                {
                    "rarity": rarity,
                    "name": name,
                    "base": base,
                    "uid": uid,
                    "shaper": shaper,
                    "elder": elder,
                    "crafted": crafted,
                    "quality": quality,
                    "sockets": sockets,
                    "level_req": level_req,
                    "item_level": item_level,
                    "implicit": implicit,
                    "text": item_text_processed,
                }
            )
        return items

    @staticmethod
    def parse_item_sets(xml_root: Element) -> list[dict]:
        """Parse item sets from XML.

        :param xml_root: Root XML element.
        :return: List of item set dictionaries.
        """
        items_element = xml_root.find("Items")
        if items_element is None:
            return []

        import pobapi.constants as constants

        item_sets = []
        for item_set in items_element.findall("ItemSet"):
            slots = {}
            for slot in item_set.findall("Slot"):
                slot_name = constants.SET_MAP.get(slot.get("name"))
                if slot_name:
                    raw_item = slot.get("itemId")
                    if raw_item == "0":
                        item_id = None
                    else:
                        try:
                            item_id = int(raw_item) - 1
                        except (TypeError, ValueError):
                            logger.debug(
                                "Invalid itemId value '%s' in slot '%s', "
                                "treating as None",
                                raw_item,
                                slot.get("name"),
                            )
                            item_id = None
                    slots[slot_name] = item_id
            item_sets.append(slots)
        return item_sets


class TreesParser:
    """Parser for skill trees."""

    @staticmethod
    def parse_trees(xml_root: Element) -> list[dict]:
        """Parse skill trees from XML.

        :param xml_root: Root XML element.
        :return: List of tree dictionaries.
        """
        tree_element = xml_root.find("Tree")
        if tree_element is None:
            return []

        trees = []
        for spec in tree_element.findall("Spec"):
            url_element = spec.find("URL")
            if url_element is None or url_element.text is None:
                continue

            url = url_element.text.strip("\n\r\t")
            nodes = _skill_tree_nodes(url)
            # Socket elements can be either:
            # 1. Direct children of Spec: <Spec><Socket .../></Spec>
            # 2. Inside Sockets element: <Spec><Sockets><Socket .../></Sockets></Spec>
            sockets_element = spec.find("Sockets")
            if sockets_element is not None:
                socket_elements = sockets_element.findall("Socket")
            else:
                socket_elements = spec.findall("Socket")
            sockets = {}
            for idx, s in enumerate(socket_elements):
                node_id_attr = s.get("nodeId")
                item_id_attr = s.get("itemId")

                if node_id_attr is None or item_id_attr is None:
                    logger.warning(
                        "Skipping socket at index %d: missing attributes "
                        "(nodeId=%r, itemId=%r)",
                        idx,
                        node_id_attr,
                        item_id_attr,
                    )
                    continue

                try:
                    node_id = int(node_id_attr)
                    item_id = int(item_id_attr)
                    sockets[node_id] = item_id
                except (ValueError, TypeError) as e:
                    logger.warning(
                        "Skipping socket at index %d: invalid numeric values "
                        "(nodeId=%r, itemId=%r): %s",
                        idx,
                        node_id_attr,
                        item_id_attr,
                        e,
                    )
                    continue
            trees.append({"url": url, "nodes": nodes, "sockets": sockets})
        return trees


class DefaultBuildParser(BuildParser):
    """Default implementation of BuildParser."""

    def parse_build_info(self, xml_element: Element) -> dict:
        """Parse build information."""
        return BuildInfoParser.parse(xml_element)

    def parse_skills(self, xml_element: Element) -> list:
        """Parse skills."""
        return SkillsParser.parse_skill_groups(xml_element)

    def parse_items(self, xml_element: Element) -> list:
        """Parse items."""
        return ItemsParser.parse_items(xml_element)

    def parse_trees(self, xml_element: Element) -> list:
        """Parse trees."""
        return TreesParser.parse_trees(xml_element)

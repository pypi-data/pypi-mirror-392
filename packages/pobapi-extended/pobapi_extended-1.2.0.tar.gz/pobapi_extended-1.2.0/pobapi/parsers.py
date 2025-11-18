"""XML parsers for different parts of Path of Building data."""

from lxml.etree import Element

from pobapi.exceptions import ParsingError
from pobapi.interfaces import BuildParser
from pobapi.util import _get_stat, _get_text, _skill_tree_nodes

__all__ = [
    "DefaultBuildParser",
    "BuildInfoParser",
    "SkillsParser",
    "ItemsParser",
    "TreesParser",
]


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
                    skill_groups.append(
                        {
                            "enabled": skill.get("enabled") == "true",
                            "label": skill.get("label"),
                            "main_active_skill": (
                                int(main_active)
                                if (main_active := skill.get("mainActiveSkill"))
                                and main_active != "nil"
                                else None
                            ),
                            "source": skill.get("source"),
                            "abilities": list(skill),
                        }
                    )
        else:
            # Old structure: Skills -> Skill (direct)
            for skill in skills_element.findall("Skill"):
                skill_groups.append(
                    {
                        "enabled": skill.get("enabled") == "true",
                        "label": skill.get("label"),
                        "main_active_skill": (
                            int(main_active)
                            if (main_active := skill.get("mainActiveSkill"))
                            and main_active != "nil"
                            else None
                        ),
                        "source": skill.get("source"),
                        "abilities": list(skill),
                    }
                )
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
            mod_ranges = [
                float(i.get("range")) for i in item_element.findall("ModRange")
            ]
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
            base = (
                name
                if rarity in ("Normal", "Magic")
                else (item_text[2] if len(item_text) > 2 else name)
            )
            uid = _get_stat(item_text, "Unique ID: ")
            shaper = bool(_get_stat(item_text, "Shaper Item"))
            elder = bool(_get_stat(item_text, "Elder Item"))
            crafted = bool(_get_stat(item_text, "{crafted}"))
            _quality = _get_stat(item_text, "Quality: ")
            quality = int(_quality) if _quality else None
            _sockets = _get_stat(item_text, "Sockets: ")
            sockets = (
                tuple(tuple(group.split("-")) for group in _sockets.split())
                if isinstance(_sockets, str) and _sockets
                else None
            )
            level_req = int(_get_stat(item_text, "LevelReq: ") or 0)
            item_level = int(_get_stat(item_text, "Item Level: ") or 1)
            implicit = (
                int(_get_stat(item_text, "Implicits: "))
                if _get_stat(item_text, "Implicits: ")
                else 0
            )
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
                    item_id = (
                        int(slot.get("itemId")) - 1
                        if slot.get("itemId") != "0"
                        else None
                    )
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
            sockets = {
                int(s.get("nodeId")): int(s.get("itemId")) for s in socket_elements
            }
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

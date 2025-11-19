from __future__ import annotations

from typing import TYPE_CHECKING

from lxml.etree import _Element, fromstring

from pobapi import config, constants, models, stats

if TYPE_CHECKING:
    from pobapi.build_builder import BuildBuilder
from pobapi.build_modifier import BuildModifier
from pobapi.builders import ConfigBuilder, ItemSetBuilder, StatsBuilder
from pobapi.decorators import listify, memoized_property
from pobapi.exceptions import ParsingError, ValidationError
from pobapi.interfaces import BuildParser
from pobapi.parsers import DefaultBuildParser
from pobapi.types import ItemSlot
from pobapi.util import (
    _fetch_xml_from_import_code,
    _fetch_xml_from_url,
    _get_stat,
    _get_text,
    _skill_tree_nodes,
    clean_pob_formatting,
)
from pobapi.validators import InputValidator, XMLValidator

"""API for PathOfBuilding's XML export format."""

__all__ = ["PathOfBuildingAPI", "from_url", "from_import_code"]


class PathOfBuildingAPI:
    """Instances of this class are single Path Of Building pastebins.

    :param xml: Path of Building XML document in byte format or Element.

    .. note:: XML must me in byte format, not string format.
        This is required because the XML contains encoding information.

    .. note:: To instantiate from pastebin.com links or import codes, use
        :func:`~pobapi.api.from_url` or
        :func:`~pobapi.api.from_import_code`, respectively."""

    def __init__(
        self,
        xml: bytes | _Element,
        parser: BuildParser | None = None,
    ):
        """
        Create a PathOfBuildingAPI instance from raw XML bytes or an existing
        Element and initialize its parsing and mutation state.

        Parameters:
            xml (bytes | Element): XML content for the build. If bytes, the
                input is validated and parsed into an Element; if already an
                Element, it is used directly.
            parser (BuildParser | None): Optional parser implementation to use
                for extracting build info; defaults to the library's default
                parser when omitted.

        Raises:
            ParsingError: If XML bytes fail to parse into an Element.
            ValidationError: If `xml` is neither bytes nor _Element, or if the
                parsed/received XML does not conform to expected build
                structure.
        """
        if isinstance(xml, bytes):
            InputValidator.validate_xml_bytes(xml)
            try:
                self.xml = fromstring(xml)
            except Exception as e:
                raise ParsingError("Failed to parse XML") from e
        elif isinstance(xml, _Element):
            self.xml = xml
        else:
            raise ValidationError("xml must be bytes or Element instance")

        XMLValidator.validate_build_structure(self.xml)
        self._parser = parser or DefaultBuildParser()
        self._build_info: dict | None = None
        self._is_mutable = False  # Flag to track if build has been modified
        self._pending_items: list[models.Item] = []  # Items to add on serialization
        self._pending_item_sets: dict[int, models.Set] = {}  # Modified item sets
        self._pending_skill_groups: list[models.SkillGroup] = []  # Added skill groups
        self._modifier = BuildModifier(self)  # Build modification handler

    @property
    def _build_info_cache(self) -> dict:
        """
        Lazily parse and cache the build's parsed metadata from the XML.

        Parses build information on first access using the configured parser
        and stores the result for subsequent calls.

        Returns:
            dict: A dictionary of parsed build information derived from the build XML.
        """
        if self._build_info is None:
            self._build_info = self._parser.parse_build_info(self.xml)
        return self._build_info

    @memoized_property
    def class_name(self) -> str:
        """
        Get the character's class name.

        Returns:
            str: The character class name, or an empty string if the class
                is not specified.
        """
        result = self._build_info_cache["class_name"]
        return str(result) if result is not None else ""

    @memoized_property
    def ascendancy_name(self) -> str | None:
        """Get a character's ascendancy class.

        :return: Character ascendancy class, if ascended.
        :rtype: :data:`~typing.Optional`\\[:class:`str`]"""
        return self._build_info_cache["ascendancy_name"]  # type: ignore[no-any-return]

    @memoized_property
    def level(self) -> int:
        """
        Retrieve the character's level.

        Returns:
            int: Character level. Returns 1 if the build does not specify a level.
        """
        level_str = self._build_info_cache["level"]
        return int(level_str) if level_str else 1

    @memoized_property
    def bandit(self) -> str | None:
        """
        Return the character's selected bandit choice.

        Returns:
            str if a bandit was selected, `None` otherwise.
        """
        return self._build_info_cache["bandit"]  # type: ignore[no-any-return]

    @memoized_property
    def active_skill_group(self) -> models.SkillGroup:
        """
        Return the build's main skill group.

        Determines the active skill group from the build metadata; if the
        build's main socket group is unspecified, the first skill group is
        returned.

        Returns:
            models.SkillGroup: The main skill group for the character.
        """
        main_socket_group = self._build_info_cache["main_socket_group"]
        index = int(main_socket_group) - 1 if main_socket_group else 0
        return self.skill_groups[index]  # type: ignore[no-any-return]

    @memoized_property
    def stats(self) -> stats.Stats:
        """
        Get aggregated character stats for the current build.

        Returns:
            stats.Stats: Character stats computed from the build XML.
        """
        return StatsBuilder.build(self.xml)

    @memoized_property
    @listify
    def skill_groups(self) -> list[models.SkillGroup]:  # type: ignore[misc]
        """
        Retrieve the character's skill groups (skill setups).

        Supports both Path of Building 2.0+ (Skills -> SkillSet -> Skill) and
        the legacy Skills -> Skill structure. Pending skill groups added via
        API modifications are yielded before groups parsed from XML.

        Returns:
            list[models.SkillGroup]: Ordered list of skill groups; each group
                includes enabled flag, label, active skill index (or `None`),
                and ability entries.
        """
        # First yield pending skill groups (from add_skill calls)
        if hasattr(self, "_pending_skill_groups"):
            yield from self._pending_skill_groups

        # Then yield skill groups from XML
        skills_element = self.xml.find("Skills")
        if skills_element is None:
            return

        # Handle new structure with SkillSet (Path of Building 2.0+)
        # Check if there are SkillSet elements
        skill_sets = skills_element.findall("SkillSet")
        if skill_sets:
            # New structure: Skills -> SkillSet -> Skill
            for skill_set in skill_sets:
                for skill in skill_set.findall("Skill"):
                    enabled = skill.get("enabled") == "true"
                    label = skill.get("label")
                    active = (
                        int(skill.get("mainActiveSkill"))
                        if skill.get("mainActiveSkill")
                        and skill.get("mainActiveSkill") != "nil"
                        else None
                    )
                    abilities = self._abilities(skill)
                    yield models.SkillGroup(enabled, label, active, abilities)
        else:
            # Old structure: Skills -> Skill (direct)
            for skill in skills_element.findall("Skill"):
                enabled = skill.get("enabled") == "true"
                label = skill.get("label")
                main_active = skill.get("mainActiveSkill")
                active = (
                    int(main_active) if main_active and main_active != "nil" else None
                )
                abilities = self._abilities(skill)
                yield models.SkillGroup(enabled, label, active, abilities)

    @memoized_property
    def active_skill(self) -> models.Gem | models.GrantedAbility | None:
        """
        Determine the currently active skill for the build's active skill group.

        Returns:
            `models.Gem` or `models.GrantedAbility` representing the active
            skill, or `None` if the active skill group has no active index.
        """
        if self.active_skill_group.active is None:
            return None
        index = self.active_skill_group.active - 1
        # Short-circuited for the most common case
        if not index:
            return self.active_skill_group.abilities[index]  # type: ignore[no-any-return]
        # For base skills on Vaal skill gems,
        # the offset is as if the base skill gems would also be present.
        # Simulating this is easier than calculating the adjusted offset.
        active = [gem for gem in self.active_skill_group.abilities if not gem.support]
        duplicate = []
        for gem in active:
            if gem.name.startswith("Vaal"):
                duplicate.append(gem)
            duplicate.append(gem)
        if len(duplicate) > 1 and duplicate[index] == duplicate[index - 1]:
            gem = duplicate[index - 1]
            # Try to get base name from map first
            name = constants.VAAL_SKILL_MAP.get(gem.name)
            if name is None:
                # Try to extract base name by removing "Vaal" prefix
                if gem.name.startswith("Vaal "):
                    name = gem.name[5:]  # Remove "Vaal " prefix
                elif gem.name.startswith("Vaal"):
                    name = gem.name[4:]  # Remove "Vaal" prefix
                else:
                    name = gem.name
            return models.Gem(name, gem.enabled, gem.level, gem.quality, gem.support)
        return self.active_skill_group.abilities[index]  # type: ignore[no-any-return]

    @memoized_property
    @listify
    def skill_gems(self) -> list[models.Gem]:  # type: ignore[misc]  # Added for convenience
        """
        List all skill gems present on the character.

        Excludes abilities that are granted by items.

        Returns:
            list_of_gems (list[models.Gem]): Skill gem objects for the character.
        """
        skills_element = self.xml.find("Skills")
        if skills_element is None:
            return []

        # Handle new structure with SkillSet (Path of Building 2.0+)
        skill_sets = skills_element.findall("SkillSet")
        if skill_sets:
            # New structure: Skills -> SkillSet -> Skill
            for skill_set in skill_sets:
                for skill in skill_set.findall("Skill"):
                    if not skill.get("source"):
                        for ability in self._abilities(skill):
                            if isinstance(ability, models.Gem):
                                yield ability
        else:
            # Old structure: Skills -> Skill (direct)
            for skill in skills_element.findall("Skill"):
                if not skill.get("source"):
                    for ability in self._abilities(skill):
                        if isinstance(ability, models.Gem):
                            yield ability

    @memoized_property
    def active_skill_tree(self) -> models.Tree:
        """
        Determines the character's currently active passive skill tree.

        Returns:
            models.Tree: The active skill tree selected by the build's `activeSpec`.
        """
        index = int(self.xml.find("Tree").get("activeSpec")) - 1
        return self.trees[index]  # type: ignore[no-any-return]

    @memoized_property
    @listify
    def trees(self) -> list[models.Tree]:  # type: ignore[misc]
        """
        Return the character's passive skill trees parsed from the build XML.

        Returns:
            list[models.Tree]: A list where each Tree contains the tree URL
                (empty string if not present), the list of node IDs for that
                spec, and a mapping of nodeId to itemId for sockets.
        """
        for spec in self.xml.find("Tree").findall("Spec"):
            url_elem = spec.find("URL")
            url = (
                url_elem.text.strip("\n\r\t")
                if url_elem is not None and url_elem.text
                else ""
            )

            # If URL is empty, try to get nodes from Nodes element
            nodes_elem = spec.find("Nodes")
            if url:
                nodes = _skill_tree_nodes(url)
            elif nodes_elem is not None:
                # Extract nodes from XML Nodes element
                nodes = [
                    int(node_elem.get("id")) for node_elem in nodes_elem.findall("Node")
                ]
            else:
                nodes = []
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
            yield models.Tree(url, nodes, sockets)

    @memoized_property
    def keystones(self) -> models.Keystones:
        """
        Represent which keystone passive nodes are active for the character.

        Returns:
            models.Keystones: Dataclass with keystone fields set to `True`
                when the corresponding node ID is present in the active
                passive tree's nodes, `False` otherwise.
        """
        # Get all field names from Keystones dataclass
        from dataclasses import fields

        keystone_fields = {f.name for f in fields(models.Keystones)}
        kwargs = {
            keystone: id_ in self.active_skill_tree.nodes
            for keystone, id_ in constants.KEYSTONE_IDS.items()
            if keystone in keystone_fields
        }
        return models.Keystones(**kwargs)

    @memoized_property
    def notes(self) -> str:
        """
        Return the build author's notes with Path of Building formatting removed.

        Notes are cleaned of PoB-specific formatting codes and returned as
        a plain string; when no notes are present, an empty string is
        returned.

        Returns:
            str: The cleaned notes.
        """
        notes_element = self.xml.find("Notes")
        if notes_element is None or notes_element.text is None:
            return ""
        raw_notes = notes_element.text.strip("\n\r\t").rstrip("\n\r\t")
        return clean_pob_formatting(raw_notes)

    def add_node(self, node_id: int, tree_index: int = 0) -> None:
        """
        Add a passive skill tree node to the specified tree.

        Parameters:
            node_id (int): Passive node ID to add (e.g.,
                PassiveNodeID.ELEMENTAL_EQUILIBRIUM or 39085).
            tree_index (int): Index of the tree to modify (default 0).

        Raises:
            ValidationError: If `tree_index` is invalid.
        """
        self._modifier.add_node(node_id, tree_index)

    def remove_node(self, node_id: int, tree_index: int = 0) -> None:
        """
        Remove a node from the build's passive skill tree.

        Parameters:
            node_id (int): ID of the passive node to remove.
            tree_index (int): Zero-based index of the tree spec to modify (default: 0).
        """
        self._modifier.remove_node(node_id, tree_index)

    def equip_item(
        self,
        item: models.Item,
        slot: ItemSlot | str,
        item_set_index: int = 0,
    ) -> int:
        """
        Equip an item into the specified slot of an item set.

        Parameters:
            item: The item to place into the slot.
            slot: Slot name or ItemSlot value identifying where to equip the
                item (e.g., "Body Armour", "Helmet").
            item_set_index: Zero-based index of the item set to modify
                (defaults to 0).

        Returns:
            The index of the added item.

        Raises:
            ValidationError: If the given slot or item_set_index is invalid.
        """
        return self._modifier.equip_item(item, slot, item_set_index)

    def add_skill(
        self,
        gem: models.Gem | models.GrantedAbility,
        group_label: str = "Main",
    ) -> None:
        """
        Add a skill (gem or granted ability) to the named skill group.

        Parameters:
                gem (models.Gem | models.GrantedAbility): The gem or granted
                    ability to append to the group.
                group_label (str): Label of the target skill group; defaults to "Main".
        """
        self._modifier.add_skill(gem, group_label)

    def remove_skill(
        self,
        gem: models.Gem | models.GrantedAbility,
        group_label: str = "Main",
    ) -> None:
        """
        Remove a skill (gem or granted ability) from the named skill group.

        Parameters:
            gem (models.Gem | models.GrantedAbility): The gem or granted
                ability to remove from the group.
            group_label (str): Label of the skill group to remove from
                (defaults to "Main").
        """
        self._modifier.remove_skill(gem, group_label)

    def unequip_item(
        self,
        slot: ItemSlot | str,
        item_set_index: int = 0,
    ) -> None:
        """
        Unequip an item from a specified item set slot.

        Parameters:
            slot (ItemSlot | str): Slot name or ItemSlot value identifying
                the slot to unequip (e.g., "Body Armour", "Helmet").
            item_set_index (int): Zero-based index of the item set to modify
                (defaults to 0).

        Raises:
            ValidationError: If the given slot or item_set_index is invalid.
        """
        self._modifier.unequip_item(slot, item_set_index)

    def set_level(self, level: int) -> None:
        """
        Set the character's level within the allowed range.

        Parameters:
            level (int): Character level; must be between 1 and 100 inclusive.

        Raises:
            ValidationError: If `level` is less than 1 or greater than 100.
        """
        self._modifier.set_level(level)

    def set_bandit(self, bandit: str | None) -> None:
        """
        Set the chosen bandit for the build.

        Parameters:
            bandit (str | None): Bandit selection as one of the strings
                "Alira", "Oak", "Kraityn", or None to unset.

        Raises:
            ValidationError: If `bandit` is a string other than "Alira",
                "Oak", "Kraityn", or None.
        """
        self._modifier.set_bandit(bandit)

    def to_xml(self) -> bytes:
        """
        Serialize the current API state to a Path of Building XML document.

        Includes any pending in-memory modifications tracked by the API.

        Returns:
            bytes: XML document for the build, including pending modifications.
        """
        from lxml.etree import tostring

        from pobapi.serializers import BuildXMLSerializer

        xml_element = BuildXMLSerializer.serialize_from_api(self)
        xml_bytes: bytes = tostring(
            xml_element, encoding="utf-8", xml_declaration=True, pretty_print=False
        )
        return xml_bytes

    def to_import_code(self) -> str:
        """
        Return the current build encoded as a Path of Building import code.

        Returns:
            import_code (str): The build represented as a Path of Building
                import code string.
        """
        from pobapi.serializers import ImportCodeGenerator

        return ImportCodeGenerator.generate_from_api(self)

    @memoized_property
    def second_weapon_set(self) -> bool:
        """
        Determine whether the build uses the second weapon set.

        Checks the Items element's `useSecondWeaponSet` attribute.

        Returns:
            True if the Items `useSecondWeaponSet` attribute is equal to
            "true", False otherwise.
        """
        return self.xml.find("Items").get("useSecondWeaponSet") == "true"  # type: ignore[no-any-return]

    @memoized_property
    @listify
    def items(self) -> list[models.Item]:  # type: ignore[misc]
        """
        Iterates all items present in the build, including any pending
        items added by modifications.

        Returns:
                An iterable of Item models representing the build's items;
                pending items (from modifications) are yielded before items
                parsed from the XML.
        """
        # First yield pending items (from equip_item calls)
        if hasattr(self, "_pending_items"):
            yield from self._pending_items

        # Then yield items from XML
        items_element = self.xml.find("Items")
        if items_element is None:
            return

        for text in items_element.findall("Item"):
            variant = text.get("variant")
            alt_variant = text.get("variantAlt")
            # "variantAlt" is for the second Watcher's Eye unique mod.
            # The 3-stat variant obtained from Uber Elder is not yet implemented in PoB.
            mod_ranges = [float(i.get("range")) for i in text.findall("ModRange")]
            item_text_content = text.text if text.text is not None else ""
            item_lines = item_text_content.strip("\n\r\t").splitlines()
            # Strip leading/trailing whitespace from each line
            item_lines = [line.strip() for line in item_lines if line.strip()]
            rarity_stat = _get_stat(item_lines, "Rarity: ")
            rarity = (
                rarity_stat.capitalize()
                if isinstance(rarity_stat, str) and rarity_stat
                else "Normal"
            )
            name = item_lines[1] if len(item_lines) > 1 else ""
            # For items with variant, name might be empty, use base as fallback
            if not name and variant is not None:
                name = item_lines[2] if len(item_lines) > 2 else "Unknown"
            base = (
                name
                if rarity in ("Normal", "Magic")
                else (item_lines[2] if len(item_lines) > 2 else name or "Unknown")
            )
            uid = _get_stat(item_lines, "Unique ID: ") or ""
            shaper = bool(_get_stat(item_lines, "Shaper Item"))
            elder = bool(_get_stat(item_lines, "Elder Item"))
            crafted = bool(_get_stat(item_lines, "{crafted}"))
            _quality = _get_stat(item_lines, "Quality: ")
            quality = int(_quality) if _quality else None
            _sockets = _get_stat(item_lines, "Sockets: ")
            sockets: tuple | None = (
                tuple(tuple(group.split("-")) for group in _sockets.split())
                if isinstance(_sockets, str) and _sockets
                else None
            )
            level_req = int(_get_stat(item_lines, "LevelReq: ") or 0)
            item_level = int(_get_stat(item_lines, "Item Level: ") or 1)
            implicit = int(_get_stat(item_lines, "Implicits: ") or 0)
            item_text = _get_text(item_lines, variant, alt_variant, mod_ranges)
            # fmt: off
            yield models.Item(
                rarity, name, base, str(uid), shaper, elder, crafted, quality,
                sockets, level_req, item_level, implicit, item_text
            )
            # fmt: on

    @memoized_property
    def active_item_set(self) -> models.Set:
        """
        Return the item set currently equipped by the character.

        If the build contains an Items element, the item set is selected
        from the document's item sets using the `activeItemSet` attribute
        (1-based). If `activeItemSet` is missing or out of range, the first
        item set is used. If the build contains no item sets, an empty item
        set with all slots set to None is returned. If there is
        no Items element at all, the first item set is returned when
        present; otherwise an empty item set is returned.

        Returns:
            models.Set: The active item set, or an empty set with all slots
                `None` when no
            item sets exist.
        """
        items_elem = self.xml.find("Items")
        if items_elem is None:
            # If no Items element, return first item set or create empty one
            if self.item_sets:
                first_set: models.Set = self.item_sets[0]
                return first_set
            from pobapi.builders import ItemSetBuilder

            empty_set_data = {
                slot_name: None
                for slot_name in [
                    "weapon1",
                    "weapon1_swap",
                    "weapon2",
                    "weapon2_swap",
                    "helmet",
                    "body_armour",
                    "gloves",
                    "boots",
                    "amulet",
                    "ring1",
                    "ring2",
                    "belt",
                    "flask1",
                    "flask2",
                    "flask3",
                    "flask4",
                    "flask5",
                ]
            }
            return ItemSetBuilder._build_single(empty_set_data)

        active_item_set_attr = items_elem.get("activeItemSet")
        if active_item_set_attr is None:
            # Default to first item set (0-based index)
            index = 0
        else:
            index = int(active_item_set_attr) - 1

        if index < 0 or index >= len(self.item_sets):
            # If no item sets exist, return empty set
            if not self.item_sets:
                from pobapi.builders import ItemSetBuilder

                empty_set_data = {
                    slot_name: None
                    for slot_name in [
                        "weapon1",
                        "weapon1_swap",
                        "weapon2",
                        "weapon2_swap",
                        "helmet",
                        "body_armour",
                        "gloves",
                        "boots",
                        "amulet",
                        "ring1",
                        "ring2",
                        "belt",
                        "flask1",
                        "flask2",
                        "flask3",
                        "flask4",
                        "flask5",
                    ]
                }
                return ItemSetBuilder._build_single(empty_set_data)
            index = 0

        return self.item_sets[index]  # type: ignore[no-any-return]

    @memoized_property
    def item_sets(self) -> list[models.Set]:
        """
        Return the character's item sets in order.

        Applies any pending modifications from equip_item calls; if pending
        changes reference indices beyond the existing sets, intermediate
        slots are filled with empty sets. Slot IDs are 0-indexed.

        Returns:
            list_of_sets (list[pobapi.models.Set]): Ordered list of item
                sets for the character.
        """

        item_sets_list = ItemSetBuilder.build_all(self.xml)

        # Apply pending modifications (from equip_item calls)
        if hasattr(self, "_pending_item_sets"):
            empty_set_data = {
                slot_name: None
                for slot_name in [
                    "weapon1",
                    "weapon1_swap",
                    "weapon2",
                    "weapon2_swap",
                    "helmet",
                    "body_armour",
                    "gloves",
                    "boots",
                    "amulet",
                    "ring1",
                    "ring2",
                    "belt",
                    "flask1",
                    "flask2",
                    "flask3",
                    "flask4",
                    "flask5",
                ]
            }
            for index, modified_set in self._pending_item_sets.items():
                if index < len(item_sets_list):
                    # Update the item_set with modifications
                    item_sets_list[index] = modified_set
                else:
                    # Append new item set (index >= len)
                    while len(item_sets_list) <= index:
                        # Fill gaps with empty sets if needed
                        item_sets_list.append(
                            ItemSetBuilder._build_single(empty_set_data)
                        )
                    # After while loop, len(item_sets_list) > index always
                    # So we can directly set the modified set at the correct index
                    item_sets_list[index] = modified_set

        return item_sets_list

    @memoized_property
    def config(self) -> config.Config:
        """
        Expose Path Of Building config tab options and their current values.

        Returns:
            config.Config: Configuration options and their current values
                for this build.
        """
        return ConfigBuilder.build(self.xml, self.level)

    @classmethod
    @listify
    def _abilities(cls, skill) -> list[models.Gem | models.GrantedAbility]:  # type: ignore[misc]
        """
        Produce ability objects for each ability element in the given skill
        element.

        Parameters:
                skill (xml.etree.ElementTree.Element |
                    Iterable[xml.etree.ElementTree.Element]):
                    An element or iterable containing ability child elements to
                    parse; each ability may represent a gem or a granted ability.

        Returns:
                list[models.Gem | models.GrantedAbility]: A list of parsed
                    ability objects: `models.Gem` for gem-based abilities and
                    `models.GrantedAbility` for non-gem abilities.
        """
        for ability in skill:
            gem_id = ability.get("gemId")
            name = ability.get("nameSpec")
            enabled = ability.get("enabled") == "true"
            level = int(ability.get("level"))
            if gem_id:
                quality = int(ability.get("quality"))
                skill_id = ability.get("skillId")
                support = skill_id.startswith("Support") if skill_id else False
                # Ensure name is not None for Gem
                if not name:
                    name = skill_id or ""
                yield models.Gem(name, enabled, level, quality, support)
            else:
                skill_id = ability.get("skillId")
                name = (
                    name
                    or (constants.SKILL_MAP.get(skill_id) if skill_id else None)
                    or ""
                )
                yield models.GrantedAbility(name, enabled, level)


def from_url(url: str, timeout: float = 6.0) -> PathOfBuildingAPI:
    """
    Create a PathOfBuildingAPI instance from a pastebin.com URL produced by
    Path of Building.

    Parameters:
        url (str): pastebin.com URL containing a Path of Building export.
        timeout (float): Request timeout in seconds.

    Returns:
        PathOfBuildingAPI: The parsed build API constructed from the fetched XML.

    Raises:
        pobapi.exceptions.InvalidURLError: If the URL is not a valid Path
            of Building pastebin link.
        pobapi.exceptions.NetworkError: If the network request fails or
            times out.
        pobapi.exceptions.ParsingError: If the fetched content cannot be
            parsed as a Path of Building build.
    """
    InputValidator.validate_url(url)
    xml_bytes = _fetch_xml_from_url(url, timeout)
    try:
        return PathOfBuildingAPI(xml_bytes)
    except ValidationError as e:
        # Convert ValidationError to ParsingError for invalid XML structure
        if "Required element" in str(e) or "not found in XML" in str(e):
            raise ParsingError(f"Invalid XML structure: {e}") from e
        raise


def from_import_code(import_code: str) -> PathOfBuildingAPI:
    """
    Create a PathOfBuildingAPI instance from a Path of Building import code.

    Parameters:
        import_code (str): The Path of Building import code string.

    Returns:
        PathOfBuildingAPI: An API representing the parsed build.

    Raises:
        :class:`~pobapi.exceptions.InvalidImportCodeError`: If the import
            code is invalid.
        :class:`~pobapi.exceptions.ParsingError`: If the generated XML
            cannot be parsed.
    """
    InputValidator.validate_import_code(import_code)
    xml_bytes = _fetch_xml_from_import_code(import_code)
    try:
        return PathOfBuildingAPI(xml_bytes)
    except ValidationError as e:
        # Convert ValidationError to ParsingError for invalid XML structure
        if "Required element" in str(e) or "not found in XML" in str(e):
            raise ParsingError(f"Invalid XML structure: {e}") from e
        raise


def create_build() -> BuildBuilder:
    """
    Create a new, empty BuildBuilder for composing a Path of Building build.

    Returns:
        BuildBuilder: a new BuildBuilder instance ready for constructing a build.
    """
    from pobapi.build_builder import BuildBuilder

    return BuildBuilder()

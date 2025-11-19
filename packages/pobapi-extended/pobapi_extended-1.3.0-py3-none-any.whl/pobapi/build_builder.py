"""Builder for creating Path of Building builds programmatically."""

from __future__ import annotations

from typing import Any

from pobapi import models
from pobapi.api import PathOfBuildingAPI
from pobapi.exceptions import ValidationError
from pobapi.types import (
    Ascendancy,
    BanditChoice,
    CharacterClass,
    ItemSlot,
)

__all__ = ["BuildBuilder"]


class BuildBuilder:
    """Builder for creating Path of Building builds programmatically.

    This class allows you to create a build from scratch without needing
    to start from an existing XML or import code.
    """

    def __init__(self):
        """
        Create a BuildBuilder with a default, empty build state.

        Initializes builder fields to sensible defaults used for
        constructing a Path of Building build, including:
        - class_name: "Scion"
        - ascendancy_name: None
        - level: 1
        - bandit: None
        - main_socket_group: None
        - items: empty list
        - item_sets: empty list
        - trees: empty list
        - active_spec: 1
        - skill_groups: empty list
        - config: None
        - notes: empty string
        - second_weapon_set: False
        """
        self.class_name: str = "Scion"
        self.ascendancy_name: str | None = None
        self.level: int = 1
        self.bandit: str | None = None
        self.main_socket_group: int | None = None

        self.items: list[models.Item] = []
        self.item_sets: list[models.Set] = []
        self.trees: list[models.Tree] = []
        self.active_spec: int = 1
        self.skill_groups: list[models.SkillGroup] = []
        self.config: Any | None = None
        self.notes: str = ""
        self.second_weapon_set: bool = False

    def set_class(
        self,
        class_name: CharacterClass | str,
        ascendancy_name: Ascendancy | str | None = None,
    ) -> BuildBuilder:
        """
        Set the character class and optional ascendancy for the builder.

        Parameters:
            class_name (CharacterClass | str): Character class as a
                CharacterClass enum or its name (e.g., "Witch").
            ascendancy_name (Ascendancy | str | None): Optional ascendancy
                as an Ascendancy enum, its name, or None.

        Returns:
            BuildBuilder: The builder instance (self) to allow method chaining.
        """
        if isinstance(class_name, CharacterClass):
            self.class_name = class_name.value
        else:
            self.class_name = class_name

        if isinstance(ascendancy_name, Ascendancy):
            self.ascendancy_name = ascendancy_name.value
        elif ascendancy_name is not None:
            self.ascendancy_name = ascendancy_name
        else:
            self.ascendancy_name = None
        return self

    def set_level(self, level: int) -> BuildBuilder:
        """
        Set the character's level within the allowed range.

        Parameters:
            level (int): Character level; must be between 1 and 100 inclusive.

        Returns:
            BuildBuilder: Self for method chaining.

        Raises:
            ValidationError: If `level` is less than 1 or greater than 100.
        """
        if not 1 <= level <= 100:
            raise ValidationError(f"Level must be between 1 and 100, got {level}")
        self.level = level
        return self

    def set_bandit(self, bandit: BanditChoice | str | None) -> BuildBuilder:
        """
        Set the chosen bandit for the build.

        Parameters:
            bandit (BanditChoice | str | None): Bandit selection as a
                BanditChoice enum, one of the strings "Alira", "Oak",
                "Kraityn", or None to unset.

        Returns:
            BuildBuilder: Self for method chaining.

        Raises:
            ValidationError: If `bandit` is a string other than "Alira",
                "Oak", "Kraityn", or None.
        """
        if isinstance(bandit, BanditChoice):
            self.bandit = bandit.value
        elif bandit not in (None, "Alira", "Oak", "Kraityn"):
            raise ValidationError(f"Invalid bandit choice: {bandit}")
        else:
            self.bandit = bandit
        return self

    def add_item(
        self, item: models.Item, slot: ItemSlot | str | None = None
    ) -> int | BuildBuilder:
        """Add item to build.

        :param item: Item to add.
        :param slot: Optional slot to equip item to (for method chaining).
        :return: Index of added item (0-based) if slot is None,
            otherwise self for method chaining.
        """
        item_index = len(self.items)
        self.items.append(item)
        if slot is not None:
            try:
                return self.equip_item(item_index, slot)
            except Exception:
                # Rollback: remove the item that was just added
                self.items.pop()
                # Re-raise the exception preserving the original traceback
                raise
        return item_index

    def create_item_set(self) -> models.Set:
        """Create a new empty item set.

        :return: New empty Set instance.
        """
        item_set = models.Set(
            weapon1=None,
            weapon1_as1=None,
            weapon1_as2=None,
            weapon1_swap=None,
            weapon1_swap_as1=None,
            weapon1_swap_as2=None,
            weapon2=None,
            weapon2_as1=None,
            weapon2_as2=None,
            weapon2_swap=None,
            weapon2_swap_as1=None,
            weapon2_swap_as2=None,
            helmet=None,
            helmet_as1=None,
            helmet_as2=None,
            body_armour=None,
            body_armour_as1=None,
            body_armour_as2=None,
            gloves=None,
            gloves_as1=None,
            gloves_as2=None,
            boots=None,
            boots_as1=None,
            boots_as2=None,
            amulet=None,
            ring1=None,
            ring2=None,
            belt=None,
            belt_as1=None,
            belt_as2=None,
            flask1=None,
            flask2=None,
            flask3=None,
            flask4=None,
            flask5=None,
        )
        self.item_sets.append(item_set)
        return item_set

    def equip_item(
        self,
        item_index: int,
        slot: ItemSlot | str,
        item_set_index: int = 0,
    ) -> BuildBuilder:
        """
        Equip an item into a specific slot of an item set.

        Parameters:
            item_index (int): 0-based index of the item in the builder's
                items list.
            slot (ItemSlot | str): Slot name (for example, "Body Armour",
                "Helmet", "Ring1").
            item_set_index (int): 0-based index of the target item set;
                new item sets will be created if this index is beyond the
                current count.

        Returns:
            BuildBuilder: Self for method chaining.

        Raises:
            ValidationError: If `item_index` is out of range or `slot` is
                not a recognized slot name.
        """
        if item_index < 0 or item_index >= len(self.items):
            raise ValidationError(f"Invalid item index: {item_index}")
        if item_set_index < 0 or item_set_index >= len(self.item_sets):
            # Create item set if it doesn't exist
            while len(self.item_sets) <= item_set_index:
                self.create_item_set()

        item_set = self.item_sets[item_set_index]

        # Map slot names to Set attributes
        slot_mapping = {
            "Weapon1": "weapon1",
            "Weapon1 Swap": "weapon1_swap",
            "Weapon2": "weapon2",
            "Weapon2 Swap": "weapon2_swap",
            "Helmet": "helmet",
            "Body Armour": "body_armour",
            "Gloves": "gloves",
            "Boots": "boots",
            "Amulet": "amulet",
            "Ring1": "ring1",
            "Ring2": "ring2",
            "Belt": "belt",
            "Flask1": "flask1",
            "Flask2": "flask2",
            "Flask3": "flask3",
            "Flask4": "flask4",
            "Flask5": "flask5",
        }

        # Get slot string value
        if isinstance(slot, ItemSlot):
            slot_str = slot.value
        else:
            slot_str = slot

        slot_attr = slot_mapping.get(slot_str)
        if slot_attr is None:
            raise ValidationError(f"Invalid slot name: {slot_str}")

        setattr(item_set, slot_attr, item_index)
        return self

    def create_tree(self, url: str = "") -> models.Tree:
        """
        Create a passive skill tree and append it to the builder's trees.

        Parameters:
            url (str): Optional Path of Exile passive skill tree share URL
                to associate with the tree.

        Returns:
            The newly created Tree instance.
        """
        tree = models.Tree(url=url, nodes=[], sockets={})
        self.trees.append(tree)
        return tree

    def allocate_node(self, node_id: int, tree_index: int = 0) -> BuildBuilder:
        """
        Allocate the given passive skill tree node into the specified tree.

        Parameters:
            node_id: Node ID to allocate (for example
                `PassiveNodeID.ELEMENTAL_EQUILIBRIUM` or `39085`).
            tree_index: Index of the target tree. If no trees exist and
                `tree_index` is 0, a new tree is created; if `tree_index` is
                out of range and trees already exist, a ValidationError is
                raised.

        Returns:
            Self for method chaining.

        Raises:
            ValidationError: If `tree_index` is invalid when trees already exist.
        """
        # node_id can be int or PassiveNodeID.<CONSTANT> (which is also int)
        actual_node_id = int(node_id)

        if tree_index < 0 or tree_index >= len(self.trees):
            # Create tree if it doesn't exist
            if len(self.trees) == 0:
                self.create_tree()
            else:
                raise ValidationError(f"Invalid tree index: {tree_index}")

        tree = self.trees[tree_index]
        if actual_node_id not in tree.nodes:
            tree.nodes.append(actual_node_id)
        return self

    def remove_node(self, node_id: int, tree_index: int = 0) -> BuildBuilder:
        """
        Remove a node from the specified passive skill tree.

        If the tree index is out of range or the node is not present, no
        changes are made.

        Returns:
            BuildBuilder: The builder instance for method chaining.
        """
        if 0 <= tree_index < len(self.trees):
            tree = self.trees[tree_index]
            if node_id in tree.nodes:
                tree.nodes.remove(node_id)
        return self

    def socket_jewel(
        self, socket_id: int, item_index: int, tree_index: int = 0
    ) -> BuildBuilder:
        """
        Place a jewel item into a specified socket on a passive skill tree.

        Parameters:
            socket_id (int): Identifier of the socket node in the tree.
            item_index (int): Index of the jewel in this builder's items
                list.
            tree_index (int): Index of the target tree in this builder's
                trees list (default 0).

        Returns:
            self: The builder instance for chaining.

        Raises:
            ValidationError: If `item_index` is out of range, or
                `tree_index` is invalid (unless a new tree is created when
                none exist).
        """
        if item_index < 0 or item_index >= len(self.items):
            raise ValidationError(f"Invalid item index: {item_index}")
        if tree_index < 0 or tree_index >= len(self.trees):
            if len(self.trees) == 0:
                self.create_tree()
            else:
                raise ValidationError(f"Invalid tree index: {tree_index}")

        tree = self.trees[tree_index]
        tree.sockets[socket_id] = item_index
        return self

    def add_skill_group(
        self,
        label: str = "Main",
        enabled: bool = True,
        active: int | None = None,
    ) -> models.SkillGroup:
        """
        Create and append a new skill group with the given label and enabled state.

        If this is the first skill group added and the builder's main
        socket group is unset, sets main_socket_group to 1.

        Parameters:
            label (str): Label for the skill group.
            enabled (bool): Whether the group is enabled.
            active (int | None): Index of the active ability in the group, or None.

        Returns:
            models.SkillGroup: The newly created skill group.
        """
        skill_group = models.SkillGroup(
            enabled=enabled, label=label, active=active, abilities=[]
        )
        self.skill_groups.append(skill_group)

        # Set as main socket group if it's the first one
        if len(self.skill_groups) == 1 and self.main_socket_group is None:
            self.main_socket_group = 1

        return skill_group

    def add_skill(
        self,
        gem: models.Gem | models.GrantedAbility,
        group_label: str = "Main",
    ) -> BuildBuilder:
        """Add a skill gem to a skill group.

        :param gem: Gem or GrantedAbility to add.
        :param group_label: Label of skill group to add to.
        :return: Self for method chaining.
        """
        # Find or create skill group
        skill_group = None
        for group in self.skill_groups:
            if group.label == group_label:
                skill_group = group
                break

        if skill_group is None:
            skill_group = self.add_skill_group(label=group_label)

        skill_group.abilities.append(gem)
        return self

    def set_config(self, config: Any) -> BuildBuilder:
        """
        Set the build's configuration object.

        Parameters:
            config (Any): Configuration object applied to the build.

        Returns:
            BuildBuilder: The same builder instance for method chaining.
        """
        self.config = config
        return self

    def set_notes(self, notes: str) -> BuildBuilder:
        """
        Set the build's notes text.

        Returns:
            The same BuildBuilder instance for method chaining.
        """
        self.notes = notes
        return self

    def set_active_spec(self, spec_index: int) -> BuildBuilder:
        """
        Set the active specification index for the build.

        Parameters:
            spec_index (int): 1-based index of the active specification;
                must be >= 1.

        Returns:
            BuildBuilder: The builder instance (`self`) for method chaining.
        """
        if spec_index < 1:
            raise ValidationError(f"Spec index must be >= 1, got {spec_index}")
        self.active_spec = spec_index
        return self

    def build(self) -> PathOfBuildingAPI:
        """
        Serialize the builder into a PathOfBuildingAPI model.

        Serializes the current BuildBuilder state to Path of Building XML
        and returns a PathOfBuildingAPI constructed from that XML.

        Returns:
            PathOfBuildingAPI: Instance representing the constructed build.
        """
        from pobapi.serializers import BuildXMLSerializer

        # Serialize to XML
        xml_element = BuildXMLSerializer.serialize(self)

        # Create PathOfBuildingAPI from XML
        return PathOfBuildingAPI(xml_element)

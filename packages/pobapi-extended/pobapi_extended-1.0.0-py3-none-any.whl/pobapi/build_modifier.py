"""Build modification functionality.

This module provides BuildModifier class for modifying builds,
separating modification logic from the main API class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pobapi import models
from pobapi.exceptions import ValidationError
from pobapi.types import ItemSlot

if TYPE_CHECKING:
    from pobapi.api import PathOfBuildingAPI

__all__ = ["BuildModifier"]


class BuildModifier:
    """Class for modifying Path of Building builds.

    This class handles all build modification operations including:
    - Adding/removing passive tree nodes
    - Equipping items
    - Adding skills

    :param api: PathOfBuildingAPI instance to modify.
    """

    def __init__(self, api: PathOfBuildingAPI):
        """
        Create a BuildModifier bound to a PathOfBuildingAPI instance for making build changes.
        
        Parameters:
            api (PathOfBuildingAPI): The API instance whose build state will be modified by this BuildModifier.
        """
        self._api = api

    def add_node(self, node_id: int, tree_index: int = 0) -> None:
        """
        Add a passive node to the specified passive skill tree.
        
        Parameters:
            node_id (int): Passive node identifier. Accepts an integer or a PassiveNodeID enum member (which is an int).
            tree_index (int): Index of the target tree in the API's `trees` list (default 0).
        
        Raises:
            ValidationError: If `tree_index` is less than 0 or greater than or equal to the number of available trees.
        """
        # node_id can be int or PassiveNodeID.<CONSTANT> (which is also int)
        actual_node_id = int(node_id)

        if tree_index < 0 or tree_index >= len(self._api.trees):
            raise ValidationError(f"Invalid tree index: {tree_index}")

        tree = self._api.trees[tree_index]
        if actual_node_id not in tree.nodes:
            tree.nodes.append(actual_node_id)
            self._api._is_mutable = True
            # Invalidate cached properties that depend on tree
            if hasattr(self._api, "_active_skill_tree"):
                delattr(self._api, "_active_skill_tree")

    def remove_node(self, node_id: int, tree_index: int = 0) -> None:
        """
        Remove a passive node from a specified passive skill tree.
        
        If the provided tree_index is within range and the node is present in that tree, the node is removed, the API is marked mutable, and the cached active skill tree (if any) is cleared.
        
        Parameters:
            node_id (int): Identifier of the passive node to remove.
            tree_index (int): Zero-based index of the passive tree to modify (default 0).
        """
        if 0 <= tree_index < len(self._api.trees):
            tree = self._api.trees[tree_index]
            if node_id in tree.nodes:
                tree.nodes.remove(node_id)
                self._api._is_mutable = True
                # Invalidate cached properties
                if hasattr(self._api, "_active_skill_tree"):
                    delattr(self._api, "_active_skill_tree")

    def equip_item(
        self,
        item: models.Item,
        slot: ItemSlot | str,
        item_set_index: int = 0,
    ) -> int:
        """
        Equip an item into a specified item set slot.
        
        Parameters:
            item (models.Item): Item to add to the build's pending items.
            slot (ItemSlot | str): Slot name (e.g., "Body Armour", "Helmet") or an ItemSlot enum.
            item_set_index (int): Index of the item set to modify (defaults to 0).
        
        Returns:
            item_index (int): 0-based index assigned to the newly added item.
        
        Raises:
            ValidationError: If the provided slot name is not recognized.
        """
        # Add item to pending items list
        if not hasattr(self._api, "_pending_items"):
            self._api._pending_items = []

        # Calculate index based on current items count (including pending)
        item_index = len(list(self._api.items))

        # Add to pending items
        self._api._pending_items.append(item)

        # Invalidate items cache
        if hasattr(self._api, "_items"):
            delattr(self._api, "_items")

        # Get or create item set
        # First, get current item_sets (may be cached)
        current_item_sets = list(self._api.item_sets)
        if item_set_index >= len(current_item_sets):
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
            # Create new item sets and add to pending
            if not hasattr(self._api, "_pending_item_sets"):
                self._api._pending_item_sets = {}
            while len(current_item_sets) <= item_set_index:
                new_set = ItemSetBuilder._build_single(empty_set_data)
                current_item_sets.append(new_set)
                # Save to pending_item_sets so it persists after cache invalidation
                self._api._pending_item_sets[len(current_item_sets) - 1] = new_set

        item_set = current_item_sets[item_set_index]

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

        # Note: This modifies the model, but XML won't be updated
        # until to_xml() is called
        setattr(item_set, slot_attr, item_index)  # Store 0-based index
        self._api._is_mutable = True

        # Save modified item_set to pending list to preserve changes
        # (since item_sets property reads from XML, we need to track
        # modifications separately)
        if not hasattr(self._api, "_pending_item_sets"):
            self._api._pending_item_sets = {}
        self._api._pending_item_sets[item_set_index] = item_set

        # Invalidate cached properties
        if hasattr(self._api, "_active_item_set"):
            delattr(self._api, "_active_item_set")
        if hasattr(self._api, "_item_sets"):
            delattr(self._api, "_item_sets")

        return item_index

    def add_skill(
        self,
        gem: models.Gem | models.GrantedAbility,
        group_label: str = "Main",
    ) -> None:
        """
        Add a skill gem to the named skill group.
        
        If a skill group with the given label does not exist, creates a new enabled group with that label and adds it. Appends the provided gem or granted ability to the group's abilities, marks the API as modified, and invalidates cached skill-group data so the change is reflected.
        
        Parameters:
            gem (models.Gem | models.GrantedAbility): The gem or granted ability to add to the group.
            group_label (str): Label of the skill group to add to (defaults to "Main").
        """
        # Find or create skill group
        skill_group = None
        for group in self._api.skill_groups:
            if group.label == group_label:
                skill_group = group
                break

        if skill_group is None:
            skill_group = models.SkillGroup(
                enabled=True, label=group_label, active=None, abilities=[]
            )
            # Store pending skill groups
            if not hasattr(self._api, "_pending_skill_groups"):
                self._api._pending_skill_groups = []
            self._api._pending_skill_groups.append(skill_group)
            self._api._is_mutable = True
            # Invalidate cached properties
            if hasattr(self._api, "_skill_groups"):
                delattr(self._api, "_skill_groups")
            if hasattr(self._api, "_active_skill_group"):
                delattr(self._api, "_active_skill_group")

        skill_group.abilities.append(gem)
        self._api._is_mutable = True
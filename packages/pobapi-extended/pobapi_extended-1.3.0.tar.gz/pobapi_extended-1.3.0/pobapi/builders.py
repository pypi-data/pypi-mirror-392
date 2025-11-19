"""Builder pattern for complex objects."""

from typing import Any

from pobapi import config, constants, models, stats
from pobapi.parsers import (
    ItemsParser,
)

__all__ = ["StatsBuilder", "ConfigBuilder", "ItemSetBuilder"]


class StatsBuilder:
    """Builder for Stats objects."""

    @staticmethod
    def build(xml_root) -> stats.Stats:
        """
        Constructs a Stats instance from the XML root's Build/PlayerStat entries.

        Parses the "Build" child of `xml_root` and collects numeric values from each
        "PlayerStat" element whose "stat" attribute maps via constants.STATS_MAP.
        If the "Build" element is absent, returns an empty Stats instance.

        Parameters:
            xml_root: The XML root element containing an optional "Build" child.

        Returns:
            stats.Stats: A Stats object populated with parsed stat values (floats) keyed
            by mapped stat names.
        """
        build_element = xml_root.find("Build")
        if build_element is None:
            return stats.Stats()

        kwargs: dict[str, float] = {}
        for i in build_element.findall("PlayerStat"):
            stat_key = constants.STATS_MAP.get(i.get("stat"))
            if stat_key:
                kwargs[stat_key] = float(i.get("value"))
        return stats.Stats(**kwargs)  # type: ignore[arg-type]


class ConfigBuilder:
    """Builder for Config objects."""

    @staticmethod
    def build(xml_root, character_level: int) -> config.Config:
        """
        Build a config.Config from an XML root using mapped Input entries
        and the provided character level.

        Parameters:
            xml_root (xml.etree.ElementTree.Element): XML root element
                expected to contain an optional "Config" child with
                "Input" elements.
            character_level (int): Character level to include in the
                resulting Config; used when the "Config" section is
                absent and always set on the returned object.

        Returns:
            config.Config: A Config populated from mapped input fields
                found under the "Config" element; any unmapped inputs
                are ignored and missing fields use defaults, with
                `character_level` set to the provided value.
        """
        config_element = xml_root.find("Config")
        if config_element is None:
            return config.Config(character_level=character_level)

        def _convert_fields(item):
            """
            Convert an input attribute mapping to the appropriate Python value.

            Parameters:
                item (dict): A mapping that may contain the keys
                    "boolean", "number", or "string".
                    - If "boolean" is present, the boolean value is
                      represented (always `True` here).
                    - If "number" is present, its value is parsed as an
                      integer.
                    - If "string" is present, its value is returned with
                      the first character capitalized.

            Returns:
                The converted value: `True` if "boolean" is present, an
                `int` for "number", a capitalized `str` for "string", or
                `None` if none of those keys are present.
            """
            if item.get("boolean"):
                return True
            elif item.get("number"):
                return int(item.get("number"))
            elif item.get("string"):
                return item.get("string").capitalize()
            return None

        kwargs: dict[str, Any] = {}
        for i in config_element.findall("Input"):
            config_key = constants.CONFIG_MAP.get(i.get("name"))
            if config_key:
                kwargs[config_key] = _convert_fields(i)
        kwargs["character_level"] = character_level
        return config.Config(**kwargs)


class ItemSetBuilder:
    """Builder for Item Set objects."""

    @staticmethod
    def build_all(xml_root) -> list[models.Set]:
        """
        Build item set models from an XML root.

        Parameters:
            xml_root: XML root element containing item-set definitions.

        Returns:
            A list of models.Set instances constructed from the item sets
                found in the XML.
        """
        return [
            ItemSetBuilder._build_single(item_set_data)
            for item_set_data in ItemsParser.parse_item_sets(xml_root)
        ]

    @staticmethod
    def _build_single(item_set_data: dict) -> models.Set:
        """
        Constructs a models.Set with all equipment and flask slots
        present; any missing fields in item_set_data are set to None.

        Parameters:
            item_set_data (dict): Mapping of Set field names to values;
                provided keys override defaults.

        Returns:
            models.Set: A Set instance populated with the provided values
                and None for any absent fields.
        """
        # Initialize all Set fields with None as default
        set_kwargs = {
            "weapon1": None,
            "weapon1_as1": None,
            "weapon1_as2": None,
            "weapon1_swap": None,
            "weapon1_swap_as1": None,
            "weapon1_swap_as2": None,
            "weapon2": None,
            "weapon2_as1": None,
            "weapon2_as2": None,
            "weapon2_swap": None,
            "weapon2_swap_as1": None,
            "weapon2_swap_as2": None,
            "helmet": None,
            "helmet_as1": None,
            "helmet_as2": None,
            "body_armour": None,
            "body_armour_as1": None,
            "body_armour_as2": None,
            "gloves": None,
            "gloves_as1": None,
            "gloves_as2": None,
            "boots": None,
            "boots_as1": None,
            "boots_as2": None,
            "amulet": None,
            "ring1": None,
            "ring2": None,
            "belt": None,
            "belt_as1": None,
            "belt_as2": None,
            "flask1": None,
            "flask2": None,
            "flask3": None,
            "flask4": None,
            "flask5": None,
        }
        # Update with actual data from XML
        set_kwargs.update(item_set_data)
        return models.Set(**set_kwargs)

"""Pantheon support for Path of Building.

This module handles Pantheon powers and their soul modifiers.
"""

from dataclasses import dataclass

from pobapi.calculator.item_modifier_parser import ItemModifierParser
from pobapi.calculator.modifiers import ModifierSystem

__all__ = ["PantheonGod", "PantheonSoul", "PantheonTools"]


@dataclass
class PantheonSoul:
    """Represents a Pantheon soul (minor or major).

    :param name: Soul name.
    :param mods: List of modifier strings.
    """

    name: str
    mods: list[str]


@dataclass
class PantheonGod:
    """Represents a Pantheon god.

    :param name: God name (e.g., "The Brine King", "Arakaali").
    :param souls: List of PantheonSoul objects.
    """

    name: str
    souls: list[PantheonSoul]


class PantheonTools:
    """Tools for applying Pantheon modifiers.

    In Path of Building (Lua), Pantheon powers are applied as modifiers
    based on the selected major and minor souls.
    """

    def __init__(self, modifiers: ModifierSystem):
        """Initialize Pantheon tools.

        :param modifiers: Modifier system to add modifiers to.
        """
        self.modifiers = modifiers
        self.parser = ItemModifierParser()

    def apply_soul_mod(self, god: PantheonGod) -> None:
        """Apply modifiers from a Pantheon god's souls.

        :param god: PantheonGod object with souls.
        """
        for soul in god.souls:
            for soul_mod_line in soul.mods:
                # Parse modifier line
                parsed_mods = self.parser.parse_line(soul_mod_line)

                if parsed_mods:
                    # Add source prefix
                    god_name = god.souls[0].name if god.souls else god.name
                    for mod in parsed_mods:
                        mod.source = f"Pantheon:{god_name}"

                    # Add modifiers to system
                    self.modifiers.add_modifiers(parsed_mods)

    def apply_pantheon(
        self, major_god: PantheonGod | None, minor_god: PantheonGod | None
    ) -> None:
        """Apply Pantheon modifiers from major and minor gods.

        :param major_god: Major Pantheon god (or None).
        :param minor_god: Minor Pantheon god (or None).
        """
        if major_god:
            self.apply_soul_mod(major_god)

        if minor_god:
            self.apply_soul_mod(minor_god)

    @staticmethod
    def create_god(
        name: str, souls_data: list[dict[str, str | list[str]]]
    ) -> PantheonGod:
        """Create a PantheonGod from data.

        :param name: God name.
        :param souls_data: List of soul data dictionaries with 'name' and 'mods'.
        :return: PantheonGod object.
        """
        souls = [
            PantheonSoul(
                name=str(soul["name"]) if isinstance(soul["name"], str) else "",
                mods=soul["mods"] if isinstance(soul["mods"], list) else [],
            )
            for soul in souls_data
        ]
        return PantheonGod(name=name, souls=souls)

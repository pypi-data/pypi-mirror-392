"""Parser for extracting modifiers from item text.

This module provides backward compatibility for ItemModifierParser.
The actual implementation has been moved to pobapi.parsers.item_modifier.
"""

__all__ = ["ItemModifierParser"]  # noqa: F822


def __getattr__(name: str):
    """Lazy import to avoid circular dependencies."""
    if name == "ItemModifierParser":
        from pobapi.parsers.item_modifier import ItemModifierParser

        return ItemModifierParser
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

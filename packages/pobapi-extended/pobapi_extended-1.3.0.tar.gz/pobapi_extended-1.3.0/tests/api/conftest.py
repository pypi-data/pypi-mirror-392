"""Fixtures for API tests."""

import pytest

from pobapi import create_build


@pytest.fixture
def simple_build():
    """Create a simple build for testing."""
    builder = create_build()
    builder.set_class("Witch", "Necromancer")
    builder.set_level(90)
    builder.create_tree()
    # Add an item set so equip_item works
    builder.create_item_set()
    build = builder.build()
    # Initialize _pending_items if needed
    if not hasattr(build, "_pending_items"):
        build._pending_items = []
    return build

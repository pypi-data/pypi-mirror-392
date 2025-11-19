"""Tests for BuildBuilder API."""

import pytest

from pobapi import api, create_build, models
from pobapi.exceptions import ValidationError
from pobapi.types import Ascendancy, CharacterClass, ItemSlot


class TestCreateBuild:
    """Tests for create_build function."""

    def test_create_build_from_scratch(self):
        """TC-API-081: Create build from scratch."""
        builder = create_build()

        assert builder is not None
        assert hasattr(builder, "class_name")
        assert hasattr(builder, "level")

        build = builder.build()

        assert build is not None
        assert isinstance(build, api.PathOfBuildingAPI)
        assert build.class_name == "Scion"  # Default class


class TestBuildBuilderSetClass:
    """Tests for BuildBuilder.set_class method."""

    def test_buildbuilder_set_class(self):
        """TC-API-082: BuildBuilder set_class."""
        builder = create_build()
        builder.set_class("Ranger", "Deadeye")

        build = builder.build()

        assert build.class_name == "Ranger"
        assert build.ascendancy_name == "Deadeye"

    def test_buildbuilder_set_class_with_enum(self):
        """TC-API-083: BuildBuilder set_class with CharacterClass enum."""
        builder = create_build()
        builder.set_class(CharacterClass.RANGER, Ascendancy.DEADEYE)

        build = builder.build()

        assert build.class_name == "Ranger"
        assert build.ascendancy_name == "Deadeye"


class TestBuildBuilderAddItem:
    """Tests for BuildBuilder.add_item method."""

    def test_buildbuilder_add_item(self, create_test_item):
        """TC-API-084: BuildBuilder add_item."""
        builder = create_build()
        item = create_test_item(name="Test Helmet", base="Iron Helmet")

        builder.add_item(item, ItemSlot.HELMET)

        build = builder.build()

        # Verify item is in build
        items = list(build.items)
        assert len(items) > 0
        assert any(i.name == "Test Helmet" for i in items)


class TestBuildBuilderAddSkill:
    """Tests for BuildBuilder.add_skill method."""

    def test_buildbuilder_add_skill(self):
        """TC-API-085: BuildBuilder add_skill."""
        builder = create_build()
        gem = models.Gem(
            name="Fireball", level=20, quality=0, enabled=True, support=False
        )

        builder.add_skill(gem, "Main")

        build = builder.build()

        # Verify skill is in build
        groups = list(build.skill_groups)
        assert len(groups) > 0
        main_group = next((g for g in groups if g.label == "Main"), None)
        assert main_group is not None
        assert len(main_group.abilities) > 0


class TestBuildBuilderSetLevel:
    """Tests for BuildBuilder.set_level method."""

    def test_buildbuilder_set_level(self):
        """TC-API-086: BuildBuilder set_level."""
        builder = create_build()
        builder.set_level(90)

        build = builder.build()

        assert build.level == 90


class TestBuildBuilderSetBandit:
    """Tests for BuildBuilder.set_bandit method."""

    def test_buildbuilder_set_bandit(self):
        """TC-API-087: BuildBuilder set_bandit."""
        builder = create_build()
        builder.set_bandit("Alira")

        build = builder.build()

        assert build.bandit == "Alira"


class TestBuildBuilderSetActiveSpec:
    """Tests for BuildBuilder.set_active_spec method."""

    def test_buildbuilder_set_active_spec(self):
        """TC-API-088: BuildBuilder set_active_spec."""
        builder = create_build()
        builder.create_tree()  # Create a tree first
        builder.set_active_spec(1)

        build = builder.build()

        # Verify active spec is set
        assert build.active_skill_tree is not None

    def test_buildbuilder_set_active_spec_with_invalid_value(self):
        """TC-API-089: BuildBuilder set_active_spec with invalid value."""
        builder = create_build()

        with pytest.raises(ValidationError):
            builder.set_active_spec(0)  # Must be >= 1


class TestBuildBuilderMethodChaining:
    """Tests for BuildBuilder method chaining."""

    def test_buildbuilder_method_chaining(self, create_test_item):
        """TC-API-090: BuildBuilder method chaining."""
        item = create_test_item(name="Test Helmet", base="Iron Helmet")
        gem = models.Gem(
            name="Fireball", level=20, quality=0, enabled=True, support=False
        )

        # Chain multiple methods
        build = (
            create_build()
            .set_class("Ranger", "Deadeye")
            .set_level(90)
            .add_item(item, ItemSlot.HELMET)
            .add_skill(gem, "Main")
            .build()
        )

        assert build.class_name == "Ranger"
        assert build.ascendancy_name == "Deadeye"
        assert build.level == 90
        assert len(list(build.items)) > 0
        assert len(list(build.skill_groups)) > 0

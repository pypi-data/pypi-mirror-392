"""Unit tests for model validators."""

import pytest

from pobapi.exceptions import ValidationError
from pobapi.model_validators import (
    ModelValidator,
    validate_character_level,
    validate_gem_level,
    validate_gem_quality,
    validate_item_level_req,
    validate_rarity,
    validate_resistance_penalty,
)


class TestModelValidator:
    """Tests for ModelValidator class."""

    @pytest.mark.parametrize(
        "value,expected_type,field_name,should_raise",
        [
            ("test", str, "name", False),
            (123, str, "name", True),
            (None, str, "name", False),  # None is allowed
        ],
    )
    def test_validate_type(self, value, expected_type, field_name, should_raise):
        """Test type validation."""
        if should_raise:
            with pytest.raises(ValidationError, match="must be of type"):
                ModelValidator.validate_type(value, expected_type, field_name)
        else:
            ModelValidator.validate_type(value, expected_type, field_name)

    @pytest.mark.parametrize(
        "value,min_value,max_value,field_name,should_raise,error_match",
        [
            (5, 1, 10, "level", False, None),
            (0, 1, 10, "level", True, "must be >="),
            (20, 1, 10, "level", True, "must be <="),
            (None, 1, 10, "level", False, None),  # None is allowed
            ("not a number", 1, 10, "level", True, "must be numeric"),
        ],
    )
    def test_validate_range(
        self, value, min_value, max_value, field_name, should_raise, error_match
    ):
        """Test range validation."""
        if should_raise:
            with pytest.raises(ValidationError, match=error_match):
                ModelValidator.validate_range(
                    value,
                    min_value=min_value,
                    max_value=max_value,
                    field_name=field_name,
                )
        else:
            ModelValidator.validate_range(
                value, min_value=min_value, max_value=max_value, field_name=field_name
            )

    @pytest.mark.parametrize(
        "value,choices,field_name,should_raise",
        [
            ("Normal", ["Normal", "Magic", "Rare"], "rarity", False),
            ("Invalid", ["Normal", "Magic"], "rarity", True),
            (None, ["Normal", "Magic"], "rarity", False),  # None is allowed
        ],
    )
    def test_validate_choice(self, value, choices, field_name, should_raise):
        """Test choice validation."""
        if should_raise:
            with pytest.raises(ValidationError, match="must be one of"):
                ModelValidator.validate_choice(value, choices, field_name)
        else:
            ModelValidator.validate_choice(value, choices, field_name)

    @pytest.mark.parametrize(
        "value,field_name,should_raise,error_match",
        [
            ("test", "name", False, None),
            ([1, 2], "items", False, None),
            (None, "name", True, "cannot be None"),
            ("", "name", True, "cannot be empty"),
            ([], "items", True, "cannot be empty"),
        ],
    )
    def test_validate_not_empty(self, value, field_name, should_raise, error_match):
        """Test not empty validation."""
        if should_raise:
            with pytest.raises(ValidationError, match=error_match):
                ModelValidator.validate_not_empty(value, field_name)
        else:
            ModelValidator.validate_not_empty(value, field_name)

    @pytest.mark.parametrize(
        "value,field_name,should_raise",
        [
            (1, "value", False),
            (100, "value", False),
            (0, "value", True),
            (-1, "value", True),
            (None, "value", False),  # None is allowed
            ("not a number", "value", True),
        ],
    )
    def test_validate_positive(self, value, field_name, should_raise):
        """Test positive validation."""
        if should_raise:
            with pytest.raises(
                ValidationError, match="must be positive|must be numeric"
            ):
                ModelValidator.validate_positive(value, field_name)
        else:
            ModelValidator.validate_positive(value, field_name)


class TestSpecificValidators:
    """Tests for specific validators."""

    @pytest.mark.parametrize(
        "level,should_raise",
        [
            (1, False),
            (20, False),
            (30, False),
            (0, True),
            (31, True),
        ],
    )
    def test_validate_gem_level(self, level, should_raise):
        """Test gem level validation."""
        if should_raise:
            with pytest.raises(ValidationError):
                validate_gem_level(level, "level")
        else:
            validate_gem_level(level, "level")

    @pytest.mark.parametrize(
        "quality,should_raise",
        [
            (0, False),
            (20, False),
            (30, False),
            (-1, True),
            (31, True),
        ],
    )
    def test_validate_gem_quality(self, quality, should_raise):
        """Test gem quality validation."""
        if should_raise:
            with pytest.raises(ValidationError):
                validate_gem_quality(quality, "quality")
        else:
            validate_gem_quality(quality, "quality")

    @pytest.mark.parametrize(
        "level,should_raise",
        [
            (1, False),
            (50, False),
            (100, False),
            (0, True),
            (101, True),
        ],
    )
    def test_validate_character_level(self, level, should_raise):
        """Test character level validation."""
        if should_raise:
            with pytest.raises(ValidationError):
                validate_character_level(level, "level")
        else:
            validate_character_level(level, "level")

    @pytest.mark.parametrize(
        "level_req,should_raise",
        [
            (0, False),  # 0 means no requirement
            (1, False),
            (68, False),
            (100, False),
            (-1, True),
            (101, True),
        ],
    )
    def test_validate_item_level_req(self, level_req, should_raise):
        """Test item level requirement validation."""
        if should_raise:
            with pytest.raises(ValidationError):
                validate_item_level_req(level_req, "level_req")
        else:
            validate_item_level_req(level_req, "level_req")

    @pytest.mark.parametrize(
        "rarity,should_raise",
        [
            ("Normal", False),
            ("Magic", False),
            ("Rare", False),
            ("Unique", False),
            ("Invalid", True),
        ],
    )
    def test_validate_rarity(self, rarity, should_raise):
        """Test rarity validation."""
        if should_raise:
            with pytest.raises(ValidationError):
                validate_rarity(rarity, "rarity")
        else:
            validate_rarity(rarity, "rarity")

    @pytest.mark.parametrize(
        "penalty,should_raise",
        [
            (0, False),
            (-30, False),
            (-60, False),
            (-20, True),
            (10, True),
        ],
    )
    def test_validate_resistance_penalty(self, penalty, should_raise):
        """Test resistance penalty validation."""
        if should_raise:
            with pytest.raises(ValidationError):
                validate_resistance_penalty(penalty, "penalty")
        else:
            validate_resistance_penalty(penalty, "penalty")


class TestValidateModel:
    """Tests for validate_model function."""

    def test_validate_model_valid(self):
        """Test validate_model with valid data."""
        from dataclasses import dataclass

        from pobapi.model_validators import validate_model

        @dataclass
        class TestModel:
            name: str
            level: int

        def validate_name(value, field_name):
            if not value:
                raise ValidationError(f"{field_name} cannot be empty")

        def validate_level(value, field_name):
            if value < 1:
                raise ValidationError(f"{field_name} must be >= 1")

        model = TestModel(name="Test", level=10)
        validators = {
            "name": [validate_name],
            "level": [validate_level],
        }
        validate_model(model, validators)  # Should not raise

    def test_validate_model_invalid(self):
        """Test validate_model with invalid data."""
        from dataclasses import dataclass

        from pobapi.model_validators import validate_model

        @dataclass
        class TestModel:
            name: str
            level: int

        def validate_name(value, field_name):
            if not value:
                raise ValidationError(f"{field_name} cannot be empty")

        model = TestModel(name="", level=10)
        validators = {"name": [validate_name]}
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_model(model, validators)

    def test_validate_model_missing_field(self):
        """Test validate_model with missing field."""
        from dataclasses import dataclass

        from pobapi.model_validators import validate_model

        @dataclass
        class TestModel:
            name: str

        model = TestModel(name="Test")
        validators = {"nonexistent": [lambda v, f: None]}
        validate_model(model, validators)  # Should skip missing field


class TestValidatorDecorator:
    """Tests for validator decorator."""

    def test_validator_decorator(self):
        """Test validator decorator."""
        from pobapi.model_validators import validator

        @validator
        def test_validator(value, field_name):
            pass

        assert hasattr(test_validator, "_is_validator")

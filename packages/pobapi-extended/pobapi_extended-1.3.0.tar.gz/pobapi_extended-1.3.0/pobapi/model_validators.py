"""Custom validators for data models."""

from collections.abc import Callable
from typing import Any, TypeVar

from pobapi.exceptions import ValidationError

T = TypeVar("T")


class ModelValidator:
    """Custom validator for data models without pydantic."""

    @staticmethod
    def validate_type(value: Any, expected_type: type, field_name: str) -> None:
        """Validate that value is of expected type.

        :param value: Value to validate.
        :param expected_type: Expected type.
        :param field_name: Name of the field being validated.
        :raises: ValidationError if type doesn't match.
        """
        if value is None:
            return  # None is allowed for optional fields

        if not isinstance(value, expected_type):
            raise ValidationError(
                f"Field '{field_name}' must be of type {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )

    @staticmethod
    def validate_range(
        value: Any,
        min_value: float | None = None,
        max_value: float | None = None,
        field_name: str = "",
    ) -> None:
        """Validate that numeric value is within range.

        :param value: Value to validate.
        :param min_value: Minimum allowed value.
        :param max_value: Maximum allowed value.
        :param field_name: Name of the field being validated.
        :raises: ValidationError if value is out of range.
        """
        if value is None:
            return

        if not isinstance(value, int | float):
            raise ValidationError(f"Field '{field_name}' must be numeric")

        if min_value is not None and value < min_value:
            raise ValidationError(
                f"Field '{field_name}' must be >= {min_value}, got {value}"
            )

        if max_value is not None and value > max_value:
            raise ValidationError(
                f"Field '{field_name}' must be <= {max_value}, got {value}"
            )

    @staticmethod
    def validate_choice(value: Any, choices: list[Any], field_name: str) -> None:
        """Validate that value is one of the allowed choices.

        :param value: Value to validate.
        :param choices: List of allowed values.
        :param field_name: Name of the field being validated.
        :raises: ValidationError if value is not in choices.
        """
        if value is None:
            return

        if value not in choices:
            raise ValidationError(
                f"Field '{field_name}' must be one of {choices}, got {value}"
            )

    @staticmethod
    def validate_not_empty(value: Any, field_name: str) -> None:
        """Validate that value is not empty.

        :param value: Value to validate.
        :param field_name: Name of the field being validated.
        :raises: ValidationError if value is empty.
        """
        if value is None:
            raise ValidationError(f"Field '{field_name}' cannot be None")

        if isinstance(value, str | list | dict) and len(value) == 0:
            raise ValidationError(f"Field '{field_name}' cannot be empty")

    @staticmethod
    def validate_positive(value: Any, field_name: str) -> None:
        """Validate that numeric value is positive.

        :param value: Value to validate.
        :param field_name: Name of the field being validated.
        :raises: ValidationError if value is not positive.
        """
        if value is None:
            return

        if not isinstance(value, int | float):
            raise ValidationError(f"Field '{field_name}' must be numeric")

        if value <= 0:
            raise ValidationError(f"Field '{field_name}' must be positive, got {value}")


def validate_model(model_instance: Any, validators: dict[str, list[Callable]]) -> None:
    """Validate a model instance using provided validators.

    :param model_instance: Instance of the model to validate.
    :param validators: Dictionary mapping field names to lists of validator functions.
    :raises: ValidationError if validation fails.
    """
    for field_name, field_validators in validators.items():
        if not hasattr(model_instance, field_name):
            continue

        value = getattr(model_instance, field_name)
        for validator in field_validators:
            validator(value, field_name)


def validator(func: Callable) -> Callable:
    """Decorator to mark a function as a validator.

    :param func: Validator function.
    :return: Decorated function.
    """
    func._is_validator = True  # type: ignore[attr-defined]
    return func


# Specific validators for pobapi models


def validate_gem_level(value: Any, field_name: str) -> None:
    """Validate gem level (1-21 typically, but can be higher with support)."""
    ModelValidator.validate_range(
        value, min_value=1, max_value=30, field_name=field_name
    )


def validate_gem_quality(value: Any, field_name: str) -> None:
    """Validate gem quality (0-23 typically)."""
    ModelValidator.validate_range(
        value, min_value=0, max_value=30, field_name=field_name
    )


def validate_character_level(value: Any, field_name: str) -> None:
    """Validate character level (1-100)."""
    ModelValidator.validate_range(
        value, min_value=1, max_value=100, field_name=field_name
    )


def validate_item_level_req(value: Any, field_name: str) -> None:
    """Validate item level requirement (0-100).

    0 means no level requirement.
    """
    ModelValidator.validate_range(
        value, min_value=0, max_value=100, field_name=field_name
    )


def validate_rarity(value: Any, field_name: str) -> None:
    """Validate item rarity."""
    ModelValidator.validate_choice(
        value, ["Normal", "Magic", "Rare", "Unique"], field_name=field_name
    )


def validate_resistance_penalty(value: Any, field_name: str) -> None:
    """Validate resistance penalty."""
    ModelValidator.validate_choice(value, [0, -30, -60], field_name=field_name)

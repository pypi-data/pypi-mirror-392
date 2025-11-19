"""Custom decorators to replace unstdlib dependencies."""

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

T = TypeVar("T")


def memoized_property(func: Callable[[Any], T]) -> property:  # noqa: UP047
    """Memoized property decorator.

    Caches the result of the property method after first access.

    :param func: Property method to memoize.
    :return: Property with memoization.
    """
    attr_name = f"_{func.__name__}"

    @property  # type: ignore[misc]
    @wraps(func)
    def wrapper(self: Any) -> T:
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)  # type: ignore[no-any-return]

    return wrapper  # type: ignore[return-value]


def listify(func: Callable[..., Any]) -> Callable[..., list[Any]]:
    """Decorator to convert generator to list.

    :param func: Generator function to convert.
    :return: Function that returns a list.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> list[Any]:
        return list(func(*args, **kwargs))

    return wrapper

"""Common utilities for Python code generation."""

from typing import Literal

from funcy_bear.type_stuffs.builtin_tools import type_name

Sections = Literal["header", "imports", "type_checking", "body", "footer"]


def to_type_names(types: tuple[type, ...] | list[type]) -> list[str]:
    """Convert types to their string names.

    Args:
        *types: The types to convert.

    Returns:
        A list of type names as strings.
    """
    return [type_name(t) for t in types]

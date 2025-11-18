"""Functions for File Builder operations related to strings and common patterns."""

from __future__ import annotations

from collections.abc import Sequence
from types import NoneType
from typing import TYPE_CHECKING

from funcy_bear.constants.characters import NEWLINE, PIPE, TRIPLE_QUOTE
from funcy_bear.sentinels import NOTSET, NotSetType
from funcy_bear.type_stuffs.builtin_tools import type_name

from ._buffer import BufferHelper
from .parts import Arg, Decorator

if TYPE_CHECKING:
    from _collections_abc import dict_items
    from collections.abc import Sequence

    from ._protocols import CodeBuilder


def generate_dict_literal(
    items: dict[str, str] | Sequence[tuple[str, str]],
    *,
    multiline: bool = True,
    indent: int = 0,
) -> str:
    """Generate a Python dict literal with proper formatting.

    Args:
        items: Dict items as dict or sequence of (key, value) tuples.
        multiline: Whether to format multiline (True) or single-line (False).
        indent: Indentation level for multiline dicts.

    Returns:
        Formatted dict literal string.
    """
    if not items:
        return "{}"

    pairs: dict_items[str, str] | Sequence[tuple[str, str]] = items.items() if isinstance(items, dict) else items

    if not multiline:
        return "{" + ", ".join(f'"{k}": {v}' for k, v in pairs) + "}"

    buffer = BufferHelper(indent=indent)
    buffer.write("{", suffix=NEWLINE)
    buffer.tick()
    for key, value in pairs:
        buffer.write(f'"{key}": {value},', suffix=NEWLINE)
    buffer.tock()
    buffer.write("}")
    return buffer.getvalue()


def generate_list_literal(
    items: Sequence[str],
    *,
    multiline: bool = True,
    indent: int = 0,
) -> str:
    """Generate a Python list literal with proper formatting.

    Args:
        items: List items as strings (already formatted/quoted if needed).
        multiline: Whether to format multiline (True) or single-line (False).
        indent: Indentation level for multiline lists.

    Returns:
        Formatted list literal string.
    """
    if not items:
        return "[]"

    if not multiline:
        return "[" + ", ".join(items) + "]"

    buffer = BufferHelper(indent=indent)
    buffer.write("[", suffix=NEWLINE)
    buffer.tick()
    for item in items:
        buffer.write(f"{item},", suffix=NEWLINE)
    buffer.tock()
    buffer.write("]")
    return buffer.getvalue()


def generate_if_block(
    condition: str,
    body: str | list[str | CodeBuilder],
    *,
    indent: int = 0,
) -> str:
    """Generate an if statement block with proper formatting.

    Args:
        condition: The if condition (without 'if' keyword or colon).
        body: Body content - strings or CodeBuilder objects.
        indent: Base indentation level.

    Returns:
        Formatted if block string.
    """
    buffer = BufferHelper(indent=indent)
    buffer.write(f"if {condition}:", suffix=NEWLINE)

    body_buffer = BufferHelper(indent=indent + 1)
    if isinstance(body, str):
        body_buffer.write(body, suffix=NEWLINE)
    else:
        for item in body:
            if isinstance(item, str):
                body_buffer.write(item, suffix=NEWLINE)
            else:
                body_buffer.write(item.render(), suffix=NEWLINE)

    buffer.write(body_buffer.getvalue())
    return buffer.getvalue()


def generate_all_export(names: list[str]) -> str:
    """Generate __all__ export list using generate_list_literal.

    Args:
        names: List of names to export.

    Returns:
        Formatted __all__ list string.
    """
    quoted_names: list[str] = [f'"{name}"' for name in names]
    list_literal: str = generate_list_literal(quoted_names, multiline=len(names) > 1, indent=0)
    return f"__all__ = {list_literal}"


def get_returns(ret: str | type | NotSetType | tuple[type, ...], prefix: str = "", suffix: str = "") -> str:
    """Set or update the return type annotation.

    Args:
        ret: The return type annotation as a string or type.
        prefix: Optional prefix to add before the return type.
        suffix: Optional suffix to add after the return type.

    Returns:
        string representing the return type annotation (includes suffix even if NOTSET).
    """
    if ret is NOTSET:
        return suffix  # Return just the suffix (colon) when no return type
    if ret is NoneType:
        ret_str = "None"
    elif isinstance(ret, (str, type)):
        ret_str: str = type_name(ret)
    elif isinstance(ret, tuple):
        ret_str = PIPE.join(type_name(t) if t is not NoneType else "None" for t in ret)
    else:
        raise TypeError(f"Unsupported return type: {ret!r}")
    return f"{prefix}{ret_str}{suffix}"


def get_docstring(docstring: str) -> str:
    """Wrap the given docstring content in triple quotes.

    Args:
        docstring: The docstring content (without triple quotes).

    Returns:
        String representing the docstring with triple quotes.
    """
    return f"{TRIPLE_QUOTE}{docstring}{TRIPLE_QUOTE}"


def render_args(args: str | Arg | list[Arg]) -> str:
    """Render function arguments to a string.

    Args:
        args: Function arguments (string, Arg, or list of Args).

    Returns:
        The rendered arguments as a string.
    """
    return (
        args.render()
        if isinstance(args, Arg)
        else ", ".join(arg.render() for arg in args)
        if isinstance(args, list)
        else args
    )


def get_decorators(decorators: list[str] | list[Decorator]) -> str:
    """Render function decorators to a string.

    Args:
        decorators: Function decorators (list of strings or Decorators).

    Returns:
        The rendered decorators as a string.
    """
    return "\n".join(decorator.render() if isinstance(decorator, Decorator) else decorator for decorator in decorators)

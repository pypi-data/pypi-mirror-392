"""Functions for File Builder operations related to strings and common patterns."""

from __future__ import annotations

from collections.abc import Sequence
from functools import partial
from typing import TYPE_CHECKING, Any

from codec_cub.common import COMMA_SPACE
from codec_cub.pythons import common as co
from funcy_bear.constants import characters as ch, py_chars as py
from funcy_bear.ops.strings import manipulation as man
from funcy_bear.sentinels import NotSetType
from funcy_bear.tools import Dispatcher
from funcy_bear.type_stuffs.builtin_tools import type_name
from funcy_bear.typing_stuffs import is_instance_of, is_str, is_tuple

from ._buffer import BufferHelper
from .parts import Arg, Decorator

if TYPE_CHECKING:
    from _collections_abc import dict_items
    from collections.abc import Sequence

    from ._protocols import CodeBuilder
    from .type_annotation import TypeAnnotation


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
        return man.quoted({})

    pairs: dict_items[str, str] | Sequence[tuple[str, str]] = items.items() if isinstance(items, dict) else items

    if not multiline:
        return ch.LEFT_BRACE + COMMA_SPACE.join(f"{man.quoted(k)}: {v}" for k, v in pairs) + ch.RIGHT_BRACE

    buffer = BufferHelper(indent=indent)
    buffer.write(ch.LEFT_BRACE, suffix=ch.NEWLINE)
    buffer.tick()
    for key, value in pairs:
        buffer.write(f"{man.quoted(key)}: {value},", suffix=ch.NEWLINE)
    buffer.tock()
    buffer.write(ch.RIGHT_BRACE)
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
        return man.quoted([])

    if not multiline:
        return man.bracketed(COMMA_SPACE.join(items))

    buffer = BufferHelper(indent=indent)
    buffer.write(ch.LEFT_BRACKET, suffix=ch.NEWLINE)
    buffer.tick()
    for item in items:
        buffer.write(f"{man.quoted(item)},", suffix=ch.NEWLINE)
    buffer.tock()
    buffer.write(ch.RIGHT_BRACKET)
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
    buffer.write(f"{py.IF_STR} {condition}:", suffix=ch.NEWLINE)

    body_buffer = BufferHelper(indent=indent + 1)
    if isinstance(body, str):
        body_buffer.write(body, suffix=ch.NEWLINE)
    else:
        for item in body:
            if isinstance(item, str):
                body_buffer.write(item, suffix=ch.NEWLINE)
            else:
                body_buffer.write(item.render(), suffix=ch.NEWLINE)

    buffer.write(body_buffer.getvalue())
    return buffer.getvalue()


def generate_all_export(names: list[str]) -> str:
    """Generate __all__ export list using generate_list_literal.

    Args:
        names: List of names to export.

    Returns:
        Formatted __all__ list string.
    """
    quoted_names: list[str] = [f"{man.quoted(name)}" for name in names]
    list_literal: str = generate_list_literal(quoted_names, multiline=len(names) > 1, indent=0)
    return f"__all__ = {list_literal}"


ret = Dispatcher("ret")


@ret.register(partial(is_instance_of, types=NotSetType))
def _not_set(ret: Any, prefix: str = ch.EMPTY_STRING, suffix: str = ch.EMPTY_STRING) -> str:
    return suffix


@ret.register(lambda x: hasattr(x, "__TYPE_ANNOTATION__"), lambda x: hasattr(x, "render"))
def _type_annotation(ret: TypeAnnotation, prefix: str = ch.EMPTY_STRING, suffix: str = ch.EMPTY_STRING) -> str:
    return man.join(prefix, ret.render(), suffix)


@ret.register(is_str)
def _string_return(ret: str, prefix: str = ch.EMPTY_STRING, suffix: str = ch.EMPTY_STRING) -> str:
    return man.join(prefix, ret, suffix)


@ret.register(partial(is_instance_of, types=type))
def _typed_return(ret: type, prefix: str = ch.EMPTY_STRING, suffix: str = ch.EMPTY_STRING) -> str:
    return man.join(prefix, type_name(ret), suffix)


@ret.register(is_tuple)
def _tuple_return(ret: tuple[type, ...], prefix: str = ch.EMPTY_STRING, suffix: str = ch.EMPTY_STRING) -> str:
    return man.join(prefix, man.piped(co.to_type_names(ret)), suffix)


@ret.dispatcher()
def get_returns(ret: Any, prefix: str = ch.EMPTY_STRING, suffix: str = ch.EMPTY_STRING) -> str:
    """Set or update the return type annotation.

    Args:
        ret: The return type annotation as a string, type, or TypeAnnotation.
        prefix: Optional prefix to add before the return type.
        suffix: Optional suffix to add after the return type.

    Returns:
        string representing the return type annotation (includes suffix even if NOTSET).
    """
    raise TypeError(f"Unsupported return type: {ret!r}")


def get_docstring(docstring: str) -> str:
    """Wrap the given docstring content in triple quotes.

    Args:
        docstring: The docstring content (without triple quotes).

    Returns:
        String representing the docstring with triple quotes.
    """
    return f"{ch.TRIPLE_QUOTE}{docstring}{ch.TRIPLE_QUOTE}"


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


def get_literal_type(values: Sequence[str], *, quote_values: bool = True) -> str:
    """Generate a Literal type annotation with proper formatting.

    Args:
        values: List of literal values.
        quote_values: Whether to add quotes around values (default True).

    Returns:
        Formatted Literal type string (e.g., 'Literal["a", "b", "c"]').
    """
    if not values:
        return py.LITERAL_STR + man.bracketed(ch.EMPTY_STRING)
    formatted_values: list[str] = [man.quoted(value) if quote_values else value for value in values]
    return py.LITERAL_STR + man.bracketed(COMMA_SPACE.join(formatted_values))


def get_type_alias(name: str, type_expr: str) -> str:
    """Generate a PEP 613 type alias statement (Python 3.12+ syntax).

    Args:
        name: The name of the type alias.
        type_expr: The type expression (e.g., 'Literal["a", "b"]' or 'dict[str, int]').

    Returns:
        Formatted type alias string (e.g., 'type StorageChoices = Literal["a", "b"]').
    """
    return f"type {name} = {type_expr}"


# ruff: noqa: ARG001

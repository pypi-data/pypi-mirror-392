"""API for building Python class definitions"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from codec_cub.common import COMMA_SPACE
from funcy_bear.constants import characters as ch, py_chars as py
from funcy_bear.ops.strings import manipulation as man

from ._buffer import BufferHelper
from ._protocols import CodeBuilder
from .helpers import Decorator, get_decorators
from .parts import Attribute, Docstring

if TYPE_CHECKING:
    from .function_builder import FunctionBuilder


class ClassBuilder(CodeBuilder):
    """Builder for Python class definitions with support for attributes and methods.

    Supports dataclasses, Pydantic models, and regular classes with inline attributes.
    """

    __CLASS_BUILDER__ = True

    def __init__(
        self,
        name: str,
        indent: int = 0,
        bases: str | list[str] = ch.EMPTY_STRING,
        type_p: str | list[str] = ch.EMPTY_STRING,
        decorators: list[str] | list[Decorator] | None = None,
        attributes: list[Attribute] | None = None,
        methods: list[FunctionBuilder] | None = None,
        docstring: str = ch.EMPTY_STRING,
        body: str = ch.EMPTY_STRING,
    ) -> None:
        """Initialize a ClassBuilder.

        Args:
            name: Class name.
            bases: Optional base classes (without parentheses).
            type_p: Optional type parameters (for generics).
            decorators: Optional list of decorator strings (without @).
            attributes: Optional list of class attributes (for dataclasses/Pydantic).
            methods: Optional list of FunctionBuilder instances.
            docstring: Optional class docstring.
            body: Optional raw body content (use if not using attributes/methods).
            indent: Base indentation level.
        """
        self.name: str = name
        if isinstance(bases, list):
            bases_str: str = COMMA_SPACE.join(bases)
        else:
            bases_str = bases
        self._bases: str = man.paren(bases_str) if bases_str else ch.EMPTY_STRING
        self._type_p: str = (
            man.bracketed(COMMA_SPACE.join(type_p))
            if isinstance(type_p, list)
            else man.bracketed(type_p)
            if type_p
            else ch.EMPTY_STRING
        )
        self._decorators: str = get_decorators(decorators) if decorators else ch.EMPTY_STRING
        self._attributes: list[Attribute] = attributes or []
        self._methods: list[FunctionBuilder] = methods or []
        self._docstring: Docstring = Docstring(docstring)
        self._body: BufferHelper = BufferHelper(indent=indent + 1)
        self._added_lines: BufferHelper = BufferHelper(indent=indent + 1)
        self._added_lines.write(body, suffix=ch.NEWLINE) if body else None
        self._result: BufferHelper = BufferHelper()

    @property
    def signature(self) -> str:
        """Set or update the class signature.

        Returns:
            string representing the class signature.
        """
        return man.join(py.CLASS_STR, ch.SPACE, self.name, self._type_p, self._bases, ch.COLON)

    def render(self) -> str:
        """Render the class to a string.

        Returns:
            The complete class definition as a string.
        """
        if self._decorators:
            self._result.write(self._decorators, suffix=ch.NEWLINE)
        self._result.write(self.signature, suffix=ch.NEWLINE)

        if self._docstring:
            self._body.write(self._docstring.render(), suffix=ch.NEWLINE)

        if self._attributes:
            for attr in self._attributes:
                self._body.write(attr.render(), suffix=ch.NEWLINE)
            if self._methods:
                self._body.write(ch.NEWLINE)

        if self._methods:
            for i, method in enumerate(self._methods):
                if i > 0:
                    self._body.write(ch.NEWLINE)
                self._body.write(method.render())

        if self._added_lines.not_empty:
            self._body.write(self._added_lines.getvalue())

        if not self._body.not_empty:
            self._body.write(ch.ELLIPSIS)

        self._result.write(self._body.getvalue())
        result: str = self._result.getvalue()
        self.clear()
        return result

    def clear(self) -> Self:
        """Clear the class body and docstring."""
        self.name = ch.EMPTY_STRING
        self._bases = ch.EMPTY_STRING
        self._decorators = ch.EMPTY_STRING
        self._attributes = []
        self._methods = []
        self._docstring.clear()
        self._body.clear()
        self._result.clear()
        self._added_lines.clear()
        return self

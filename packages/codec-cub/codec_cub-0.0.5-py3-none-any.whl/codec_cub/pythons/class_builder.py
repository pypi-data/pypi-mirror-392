"""API for building Python class definitions"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Self

from funcy_bear.constants.characters import COLON, ELLIPSIS, EMPTY_STRING, NEWLINE

from ._buffer import BufferHelper
from ._protocols import CodeBuilder
from .helpers import Decorator, get_decorators
from .parts import Attribute, Docstring

if TYPE_CHECKING:
    from .function_builder import FunctionBuilder

Sections = Literal["header", "imports", "type_checking", "body", "footer"]


class ClassBuilder(CodeBuilder):
    """Builder for Python class definitions with support for attributes and methods.

    Supports dataclasses, Pydantic models, and regular classes with inline attributes.
    """

    def __init__(
        self,
        name: str,
        indent: int = 0,
        bases: str | list[str] = EMPTY_STRING,
        type_p: str | list[str] = EMPTY_STRING,
        decorators: list[str] | list[Decorator] | None = None,
        attributes: list[Attribute] | None = None,
        methods: list[FunctionBuilder] | None = None,
        docstring: str = EMPTY_STRING,
        body: str = EMPTY_STRING,
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
            bases_str: str = ", ".join(bases)
        else:
            bases_str = bases
        self._bases: str = f"({bases_str})" if bases_str else EMPTY_STRING
        self._type_p: str = (
            f"[{', '.join(type_p)}]" if isinstance(type_p, list) else f"[{type_p}]" if type_p else EMPTY_STRING
        )
        self._decorators: str = get_decorators(decorators) if decorators else EMPTY_STRING
        self._attributes: list[Attribute] = attributes or []
        self._methods: list[FunctionBuilder] = methods or []
        self._docstring: Docstring = Docstring(docstring)
        self._body: BufferHelper = BufferHelper(indent=indent + 1)
        self._added_lines: BufferHelper = BufferHelper(indent=indent + 1)
        self._added_lines.write(body, suffix=NEWLINE) if body else None
        self._result: BufferHelper = BufferHelper()

    @property
    def signature(self) -> str:
        """Set or update the class signature.

        Returns:
            string representing the class signature.
        """
        return f"class {self.name}{self._type_p}{self._bases}{COLON}"

    def render(self) -> str:
        """Render the class to a string.

        Returns:
            The complete class definition as a string.
        """
        if self._decorators:
            self._result.write(self._decorators, suffix=NEWLINE)
        self._result.write(self.signature, suffix=NEWLINE)

        # Add docstring if present
        if self._docstring:
            self._body.write(self._docstring.render(), suffix=NEWLINE)

        # Add attributes if present
        if self._attributes:
            for attr in self._attributes:
                self._body.write(attr.render(), suffix=NEWLINE)
            if self._methods:
                self._body.write(EMPTY_STRING, suffix=NEWLINE)  # Blank line before methods

        # Add methods if present
        if self._methods:
            for i, method in enumerate(self._methods):
                # Add blank line between methods
                if i > 0:
                    self._body.write(EMPTY_STRING, suffix=NEWLINE)
                self._body.write(method.render())

        # Add custom body content if present
        if self._added_lines.not_empty:
            self._body.write(self._added_lines.getvalue())

        # If no content at all, add ellipsis
        if not self._body.not_empty:
            self._body.write(ELLIPSIS)

        self._result.write(self._body.getvalue())
        result: str = self._result.getvalue()
        self.clear()
        return result

    def clear(self) -> Self:
        """Clear the class body and docstring."""
        self.name = EMPTY_STRING
        self._bases = EMPTY_STRING
        self._decorators = EMPTY_STRING
        self._attributes = []
        self._methods = []
        self._docstring.clear()
        self._body.clear()
        self._result.clear()
        self._added_lines.clear()
        return self

"""Builder for Python function definitions."""

from __future__ import annotations

from types import NoneType
from typing import TYPE_CHECKING, Self

from funcy_bear.constants import characters as ch
from funcy_bear.ops.strings.manipulation import join, paren
from funcy_bear.sentinels import NOTSET, NotSetType

from ._buffer import BufferHelper
from ._protocols import CodeBuilder
from .helpers import render_args
from .parts import Arg, Decorator, Docstring

if TYPE_CHECKING:
    from .docstring_builder import DocstringBuilder
    from .type_annotation import TypeAnnotation


class FunctionBuilder(CodeBuilder):
    """Builder for Python function definitions."""

    __FUNCTION_BUILDER__ = True

    def __init__(
        self,
        name: str,
        indent: int = 0,
        args: str | Arg | list[Arg] = ch.EMPTY_STRING,
        returns: str | type | TypeAnnotation | NotSetType | tuple[type, ...] = NOTSET,
        decorators: list[str] | list[Decorator] | None = None,
        docstring: str | DocstringBuilder = ch.EMPTY_STRING,
        body: str = ch.EMPTY_STRING,
    ) -> None:
        """Initialize a FunctionBuilder.

        Args:
            name: Function name.
            args: Function arguments (without parentheses).
            returns: Optional return type annotation (NOTSET for no annotation, NoneType for -> None, or TypeAnnotation object).
            decorators: Optional list of decorator strings (without @).
            docstring: Docstring content (string or DocstringBuilder object).
            indent: Base indentation level.
        """
        from .helpers import get_decorators, get_returns  # noqa: PLC0415

        self.name: str = name
        self.args: str = render_args(args)
        self.returns: str = get_returns(returns, prefix=f" {ch.ARROW} ", suffix=ch.COLON)
        self._decorators: str = get_decorators(decorators) if decorators else ch.EMPTY_STRING

        if hasattr(docstring, "__DOCSTRING_BUILDER__") and hasattr(docstring, "render"):
            docstring_str = getattr(docstring, "render")()  # noqa: B009
        else:
            docstring_str: str = docstring  # pyright: ignore[reportAssignmentType]

        self._docstring: Docstring = Docstring(docstring_str)

        self._added_lines: BufferHelper = BufferHelper(indent=indent + 1)
        self._added_lines.write(body, suffix=ch.NEWLINE) if body else None
        self._body: BufferHelper = BufferHelper(indent=indent + 1)
        self._result: BufferHelper = BufferHelper()

    @property
    def signature(self) -> str:
        """Set or update the function signature.

        Returns:
            string representing the function signature.
        """
        return join("def ", self.name, paren(self.args), self.returns)

    def render(self) -> str:
        """Render the function to a string.

        Returns:
            The complete function definition as a string.
        """
        if self._decorators:
            self._result.write(self._decorators, suffix=ch.NEWLINE)
        self._result.write(self.signature, suffix=ch.NEWLINE)
        if self._docstring:
            self._body.write(self._docstring.render(), suffix=ch.NEWLINE)
        self._result.write(self._body.getvalue())
        if self._added_lines.not_empty:
            self._result.write(self._added_lines.getvalue())
        else:
            self._body.write(ch.ELLIPSIS)
            self._result.write(self._body.getvalue())
        result: str = self._result.getvalue()
        self.clear()
        return result

    def clear(self) -> Self:
        """Clear the function body and docstring."""
        self.name = ch.EMPTY_STRING
        self.args = ch.EMPTY_STRING
        self.returns = ch.EMPTY_STRING
        self._decorators = ch.EMPTY_STRING
        self._docstring.clear()
        self._body.clear()
        self._result.clear()
        self._added_lines.clear()
        return self


def generate_main_block(
    body: str | list[str | CodeBuilder],
    *,
    include_docstring: bool = False,
) -> str:
    """Generate if __name__ == "__main__": block using FunctionBuilder and generate_if_block.

    Args:
        body: Body content - strings or CodeBuilder objects.
        include_docstring: Whether to add a docstring to main().

    Returns:
        Formatted main block string.
    """
    from .helpers import generate_if_block  # noqa: PLC0415

    main_func = FunctionBuilder(
        name="main",
        returns=NoneType,  # Explicitly None return type
        docstring="Run the main program." if include_docstring else ch.EMPTY_STRING,
    )

    if isinstance(body, str):
        main_func.add_line(body)
    else:
        for item in body:
            if isinstance(item, str):
                main_func.add_line(item)
            else:
                main_func.add_line(item.render())

    buffer = BufferHelper()
    buffer.write(main_func.render(), suffix=ch.NEWLINE)
    buffer.write(ch.NEWLINE)
    buffer.write(generate_if_block('__name__ == "__main__"', "main()"))

    return buffer.getvalue()

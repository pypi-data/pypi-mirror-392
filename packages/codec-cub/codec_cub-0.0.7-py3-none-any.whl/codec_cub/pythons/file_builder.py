"""A simple in-memory string buffer that helps with dynamically creating files."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from enum import IntEnum
from typing import TYPE_CHECKING, Any, Self

from codec_cub.common import COMMA_SPACE
from codec_cub.pythons._buffer import StringBuilder
from codec_cub.pythons.common import Sections  # noqa: TC001
from funcy_bear.constants import characters as ch, py_chars as py
from funcy_bear.ops.strings.manipulation import first_item, join, quoted

from ._buffer import BufferHelper
from ._protocols import CodeBuilder
from .helpers import Decorator, get_decorators
from .parts import Docstring

if TYPE_CHECKING:
    from collections.abc import Generator

    from .fluent_builders import DictLiteralBuilder, ListLiteralBuilder, TypeAliasBuilder, VariableBuilder

SPC: str = ch.SPACE


class NewLineReturn(IntEnum):
    """Enumeration for newline return options."""

    ZERO = 0
    ONE = 1
    TWO = 2


class CodeSection:
    """A code section buffer with indentation management and context managers for code blocks."""

    def __init__(self, name: Sections) -> None:
        """Initialize the CodeSection with a name and empty buffer."""
        self.section_name: str = name
        self._buffer: list[str] = []
        self._current_indent: int = 0

    def _indent(self, off: int = 0) -> str:
        """Get the current indentation level as string with optional offset."""
        return self._current_indent * ch.INDENT + (off * ch.INDENT)

    def _add(self, *segments: str, sep: str = ch.EMPTY_STRING, indent: bool = False) -> None:
        """Concatenate segments with current indentation."""
        _indent: str = self._indent() if indent else ch.EMPTY_STRING
        values = []
        for seg in segments:
            if hasattr(seg, "render"):
                values.append(seg.render())  # pyright: ignore[reportAttributeAccessIssue]
            else:
                values.append(seg)
        self._buffer.append(join(*values, indent=_indent, sep=sep))

    def docstring(self, *doc_lines: str, indent: int = 0) -> None:
        """Begin a docstring block.

        Args:
            *doc_lines: Lines of the docstring.
            indent: Relative indent change (can be negative to outdent relative to class).
        """
        _indent: str = self._indent(indent)
        self._add(_indent, ch.TRIPLE_QUOTE)
        for line in doc_lines:
            self._add(_indent, line)
        self._add(_indent, ch.NEWLINE, ch.TRIPLE_QUOTE)

    def _detect_spacing(self, item: str | CodeBuilder, original_item: str | CodeBuilder) -> int:
        """Detect appropriate spacing for the given item.

        Args:
            item: The rendered string (if CodeBuilder was passed, this is the rendered output).
            original_item: The original item (CodeBuilder or string).

        Returns:
            Number of newlines to add after this item.
        """
        if hasattr(original_item, "__FUNCTION_BUILDER__"):
            decorators: str = getattr(original_item, "_decorators", "")
            if (isinstance(item, str) and "@overload" in item) or (decorators and "overload" in decorators):
                return NewLineReturn.ONE
            return NewLineReturn.TWO

        if hasattr(original_item, "__CLASS_BUILDER__") or hasattr(original_item, "__ENUM_BUILDER__"):
            return NewLineReturn.TWO

        if isinstance(item, str):  # noqa: SIM102
            if (item.startswith("type ") and ch.EQUALS in item) or (
                ch.COLON in item and ch.EQUALS in item and not item.strip().startswith(py.DEF_STR)
            ):
                return NewLineReturn.ONE

        return NewLineReturn.ZERO

    def add(self, *ln: str | CodeBuilder, indent: int = 0, end: int | None = None) -> Self:
        """Add line(s) or CodeBuilder object(s) to the buffer with smart spacing.

        Args:
            *ln: Line(s) or CodeBuilder object(s) to add to the buffer.
            indent: Relative indent change (can be negative to outdent relative to class).
            end: Number of newlines to add after the content. If None (default), auto-detects based on content type.

        """
        _indent: str = self._indent(indent)

        lines_to_add: list[str] = []
        original_items: list[str | CodeBuilder] = []

        for item in ln:
            original_items.append(item)
            if isinstance(item, CodeBuilder):
                lines_to_add.append(item.render())
            else:
                lines_to_add.append(item)

        if len(lines_to_add) == 1:
            self._add(first_item(lines_to_add), _indent)
        else:
            for line in lines_to_add:
                self._add(line, _indent)

        if end is None and lines_to_add and original_items:
            end = self._detect_spacing(lines_to_add[0], original_items[0])

        if end is not None and end > 0:
            self.newline(end)
        return self

    def newline(self, n: int = 1) -> Self:
        """Add newlines to the buffer.

        Args:
            n: Number of newlines to add, default is 1.
        """
        for _ in range(n):
            self._buffer.append(ch.NEWLINE)
        return self

    def tick(self) -> Self:
        """Increment the current indentation level by 1."""
        self._current_indent += 1
        return self

    def tock(self) -> Self:
        """Decrement the current indentation level by 1."""
        if self._current_indent > 0:
            self._current_indent -= 1
        return self

    def set_indent(self, level: int) -> Self:
        """Set the absolute indentation level.

        Args:
            level: The indentation level to set (0 = no indent).
        """
        self._current_indent = level
        return self

    def reset_indent(self) -> Self:
        """Reset indentation to 0."""
        self._current_indent = 0
        return self

    def get(self) -> list[str]:
        """Get the current buffer lines.

        Returns:
            A list of strings representing the buffer lines.
        """
        return self._buffer

    def join(self, sep: str = ch.EMPTY_STRING) -> str:
        """Join the current buffer lines into a single string.

        Returns:
            The complete buffer as a single string.
        """
        return join(*self._buffer, sep=sep)

    def type_alias(self, name: str) -> TypeAliasBuilder:
        """Create a fluent type alias builder.

        Args:
            name: The name of the type alias.

        Returns:
            A TypeAliasBuilder for fluent API.

        Examples:
            >>> section.type_alias("StorageChoices").literal("json", "yaml", "toml")
            >>> section.type_alias("IntOrStr").union("int", "str")
        """
        from .fluent_builders import TypeAliasBuilder  # noqa: PLC0415

        return TypeAliasBuilder(self, name)

    def variable(self, name: str) -> VariableBuilder:
        """Create a fluent variable builder.

        Args:
            name: The variable name.

        Returns:
            A VariableBuilder for fluent API.

        Examples:
            >>> section.variable("storage_map").type_hint("dict[str, type[Storage]]").value(
            ...     "{...}"
            ... )
        """
        from .fluent_builders import VariableBuilder  # noqa: PLC0415

        return VariableBuilder(self, name)

    def list_literal(self) -> ListLiteralBuilder:
        """Create a fluent list literal builder.

        Returns:
            A ListLiteralBuilder for fluent API.

        Examples:
            >>> from codec_cub.pythons.fluent_builders import ListLiteralBuilder
            >>> builder = ListLiteralBuilder()
            >>> builder.add("'a'").add("'b'").multiline().render()
        """
        from .fluent_builders import ListLiteralBuilder  # noqa: PLC0415

        return ListLiteralBuilder(indent=self._current_indent)

    def dict_literal(self) -> DictLiteralBuilder:
        """Create a fluent dict literal builder.

        Returns:
            A DictLiteralBuilder for fluent API.

        Examples:
            >>> from codec_cub.pythons.fluent_builders import DictLiteralBuilder
            >>> builder = DictLiteralBuilder()
            >>> builder.entry("'host'", "'localhost'").multiline().render()
        """
        from .fluent_builders import DictLiteralBuilder  # noqa: PLC0415

        return DictLiteralBuilder(indent=self._current_indent)

    @contextmanager
    def block(self, header: str) -> Generator[None, Any]:
        """Context manager for a generic code block with automatic indentation.

        Args:
            header: The header line (will have colon appended if not present).

        Yields:
            None
        """
        self.add(header if header.endswith(ch.COLON) else join(header, ch.COLON))
        self.tick()
        try:
            yield
        finally:
            self.tock()

    @contextmanager
    def function(self, name: str, args: str = ch.EMPTY_STRING, returns: str | None = None) -> Generator[None, Any]:
        """Context manager for a function definition.

        Args:
            name: Function name.
            args: Function arguments (without parentheses).
            returns: Optional return type annotation.

        Yields:
            None
        """
        s = StringBuilder(join(py.DEF_STR, SPC, name, ch.LEFT_PAREN, args, ch.RIGHT_PAREN))
        if returns:
            s.join(SPC, ch.ARROW, SPC, returns)
        with self.block(s.consume()):
            yield

    @contextmanager
    def class_def(self, name: str, bases: str = ch.EMPTY_STRING) -> Generator[None, Any]:
        """Context manager for a class definition.

        Args:
            name: Class name.
            bases: Optional base classes (without parentheses).

        Yields:
            None
        """
        s = StringBuilder(join(py.CLASS_STR, SPC, name))
        if bases:
            s.join(ch.LEFT_PAREN, bases, ch.RIGHT_PAREN)
        with self.block(s.consume()):
            yield

    @contextmanager
    def if_block(self, condition: str = "") -> Generator[Any, Any, Any]:
        """Context manager for an if statement.

        Args:
            condition: The condition to test.

        Yields:
            None
        """
        if self.section_name == py.TYPE_CHECKING_STR.lower():
            condition = py.TYPE_CHECKING_STR
        if not condition:
            condition = ch.TRUE_LITERAL
        with self.block(join(py.IF_STR, SPC, condition)):
            yield

    @contextmanager
    def elif_block(self, condition: str) -> Generator[None, Any]:
        """Context manager for an elif statement.

        Args:
            condition: The condition to test.

        Yields:
            None
        """
        with self.block(join(py.ELIF_STR, SPC, condition)):
            yield

    @contextmanager
    def else_block(self) -> Generator[None, Any]:
        """Context manager for an else statement.

        Yields:
            None
        """
        with self.block(py.ELSE_STR):
            yield

    @contextmanager
    def with_block(self, expression: str, as_var: str | None = None) -> Generator[None, Any]:
        """Context manager for a with statement.

        Args:
            expression: The context manager expression.
            as_var: Optional variable name for 'as' clause.

        Yields:
            None
        """
        s = StringBuilder(py.WITH_STR, SPC, expression)
        if as_var:
            s.join(SPC, py.AS_STR, SPC, as_var)
        with self.block(s.consume()):
            yield

    @contextmanager
    def try_block(self) -> Generator[None, Any]:
        """Context manager for a try statement.

        Yields:
            None
        """
        with self.block(py.TRY_STR):
            yield

    @contextmanager
    def except_block(self, exception: str | None = None, as_var: str | None = None) -> Generator[None, Any]:
        """Context manager for an except statement.

        Args:
            exception: Optional exception type to catch.
            as_var: Optional variable name for 'as' clause.

        Yields:
            None
        """
        s = StringBuilder(py.EXCEPT_STR)
        if exception:
            s.join(SPC, exception)
        if as_var:
            s.join(SPC, py.AS_STR, SPC, as_var)
        with self.block(s.consume()):
            yield

    @contextmanager
    def finally_block(self) -> Generator[None, Any]:
        """Context manager for a finally statement.

        Yields:
            None
        """
        with self.block(py.FINALLY_STR):
            yield

    @contextmanager
    def for_loop(self, variable: str, iterable: str) -> Generator[None, Any]:
        """Context manager for a for loop.

        Args:
            variable: Loop variable name.
            iterable: Expression to iterate over.

        Yields:
            None
        """
        with self.block(join(py.FOR_STR, SPC, variable, SPC, py.IN_STR, SPC, iterable)):
            yield

    @contextmanager
    def while_loop(self, condition: str) -> Generator[None, Any]:
        """Context manager for a while loop.

        Args:
            condition: The loop condition.

        Yields:
            None
        """
        with self.block(f"while {condition}"):
            yield


class FileBuilder:
    """A file builder that organizes code into logical sections with automatic formatting."""

    def __init__(self) -> None:
        """Initialize the FileBuilder with empty sections."""
        self._sections: dict[Sections, CodeSection] = {
            "header": CodeSection("header"),
            "imports": CodeSection("imports"),
            "type_checking": CodeSection("type_checking"),
            "body": CodeSection("body"),
            "footer": CodeSection("footer"),
        }

    def add(self, section: Sections, line: str, indent: int = 0) -> None:
        """Add a line to the buffer in the specified section.

        Args:
            section: The section where the line should be added.
            line: The line to add to the buffer.
            indent: Relative indent change for this line.
        """
        self._sections[section].add(line, indent=indent)

    def get_section(self, section: Sections) -> CodeSection:
        """Get a specific section buffer for direct manipulation.

        Args:
            section: The section to retrieve.

        Returns:
            The CodeSection for the specified section.
        """
        return self._sections[section]

    @property
    def header(self) -> CodeSection:
        """Get the header section.

        Returns:
            The header CodeSection.
        """
        return self._sections["header"]

    @property
    def imports(self) -> CodeSection:
        """Get the imports section.

        Returns:
            The imports CodeSection.
        """
        return self._sections["imports"]

    @property
    def type_checking(self) -> CodeSection:
        """Get the type_checking section.

        Returns:
            The type_checking CodeSection.
        """
        return self._sections["type_checking"]

    @property
    def body(self) -> CodeSection:
        """Get the body section.

        Returns:
            The body CodeSection.
        """
        return self._sections["body"]

    @property
    def footer(self) -> CodeSection:
        """Get the footer section.

        Returns:
            The footer CodeSection.
        """
        return self._sections["footer"]

    def render(self, add_section_separators: bool = False) -> str:
        """Render the buffer into a single string with sections in order.

        Args:
            add_section_separators: If True, add blank lines between non-empty sections.

        Returns:
            A string containing all lines in the buffer, ordered by section.
        """
        output_lines: list[str] = []
        sections_order: tuple[Sections, ...] = ("header", "imports", "type_checking", "body", "footer")
        for section in sections_order:
            code_section: CodeSection = self._sections[section]
            section_lines: list[str] = code_section.get()
            if section_lines:
                if output_lines and add_section_separators:
                    output_lines.append(ch.EMPTY_STRING)
                output_lines.extend(section_lines)
        return join(*output_lines, sep=ch.NEWLINE)


class EnumBuilder:
    """General-purpose enum builder for Enum, IntEnum, StrEnum, Flag, etc.

    Supports all enum types by specifying the base class.
    """

    __ENUM_BUILDER__ = True

    def __init__(
        self,
        name: str,
        members: dict[str, str | int] | list[str],
        base_class: str = "Enum",
        decorators: list[str] | list[Decorator] | None = None,
        docstring: str = ch.EMPTY_STRING,
    ) -> None:
        """Initialize an EnumBuilder.

        Args:
            name: Enum class name.
            members: Either dict of name->value pairs or list of names (auto values).
            base_class: Base enum type (Enum, IntEnum, StrEnum, Flag, etc.).
            decorators: Optional decorators.
            docstring: Optional docstring.
        """
        self.name: str = name
        self.base_class: str = base_class
        self._members: dict[str, str | int]
        if isinstance(members, list):
            self._members = dict.fromkeys(members, f"{py.AUTO_STR}()")
        else:
            self._members = members
        self._decorators: str = get_decorators(decorators) if decorators else ch.EMPTY_STRING
        self._docstring: Docstring = Docstring(docstring)
        self._added_lines: BufferHelper = BufferHelper(indent=1)

    def add_line(self, line: str) -> Self:
        """Add a line to the enum body.

        Args:
            line: The line to add.

        Returns:
            Self for method chaining.
        """
        self._added_lines.write(line, suffix=ch.NEWLINE)
        return self

    def add_to_docs(
        self,
        additional_content: str,
        prefix: str = "",
        suffix: str = "",
    ) -> Self:
        """Add additional content to the docstring.

        Args:
            additional_content: The content to add to the docstring.
            prefix: An optional prefix to add before the additional content.
            suffix: An optional suffix to add after the additional content.

        Returns:
            Self for method chaining.
        """
        self._docstring.add(additional_content, prefix=prefix, suffix=suffix)
        return self

    def render(self) -> str:
        """Render the enum to a string.

        Returns:
            The complete enum definition as a string.
        """
        result = BufferHelper()

        if self._decorators:
            result.write(self._decorators, suffix=ch.NEWLINE)

        result.write(
            join(py.CLASS_STR, SPC, self.name, ch.LEFT_PAREN, self.base_class, ch.RIGHT_PAREN, ch.COLON),
            suffix=ch.NEWLINE,
        )

        body = BufferHelper(indent=1)
        if self._docstring:
            body.write(self._docstring.render(), suffix=ch.NEWLINE)
            body.write(ch.NEWLINE)

        for member_name, member_value in self._members.items():
            mem_val: Any = member_value
            if isinstance(member_value, str) and not member_value.startswith(
                (py.AUTO_STR, ch.DOUBLE_QUOTE, ch.SINGLE_QUOTE)
            ):
                mem_val = quoted(member_value)
            body.write(join(member_name, SPC, ch.EQUALS, SPC, str(mem_val)), suffix=ch.NEWLINE)

        if self._added_lines.not_empty:
            body.write(self._added_lines.getvalue())

        result.write(body.getvalue())
        return result.getvalue()


class ImportManager:
    """Manages imports and automatically deduplicates them.

    Organizes imports into standard library, third-party, and local sections.
    """

    __IMPORT_MANAGER__ = True

    def __init__(self) -> None:
        """Initialize the ImportManager."""
        self._future_imports: set[str] = set()
        self._standard_imports: set[str] = set()
        self._third_party_imports: set[str] = set()
        self._local_imports: set[str] = set()
        self._from_imports: dict[str, set[str]] = {}
        self._result = None

    def add_import(self, module: str, *, is_third_party: bool = False, is_local: bool = False) -> Self:
        """Add a simple import statement.

        Args:
            module: Module name to import.
            is_third_party: Whether this is a third-party module.
            is_local: Whether this is a local/relative import.

        Returns:
            Self for method chaining.
        """
        if module.startswith("__future__"):
            self._future_imports.add(module)
        elif is_local:
            self._local_imports.add(module)
        elif is_third_party:
            self._third_party_imports.add(module)
        else:
            self._standard_imports.add(module)
        return self

    def add_from_import(
        self,
        module: str,
        names: str | list[str],
        *,
        is_third_party: bool = False,
        is_local: bool = False,
    ) -> Self:
        """Add a from...import statement.

        Args:
            module: Module to import from.
            names: Single name or list of names to import.
            is_third_party: Whether this is a third-party module.
            is_local: Whether this is a local/relative import.

        Returns:
            Self for method chaining.
        """
        if isinstance(names, str):
            names = [names]

        key: str = join(module, ch.PIPE, "third" if is_third_party else "local" if is_local else "std")
        if key not in self._from_imports:
            self._from_imports[key] = set()
        self._from_imports[key].update(names)
        return self

    def _insert_newline(self, n: int = 1) -> None:
        """Insert newlines into the import buffer."""
        for _ in range(n):
            self.result.write(ch.NEWLINE)

    def _from_import(self, m: str, f: str, sep: str = ch.NEWLINE) -> None:
        self.result.write(join("from", SPC, m, SPC, "import", SPC, f), suffix=sep)

    def _import(self, m: str, sep: str = ch.NEWLINE) -> None:
        self.result.write(join("import", SPC, m), suffix=sep)

    @property
    def _std_from(self) -> dict[str, set[str]]:
        """Get standard library from-imports."""
        return {k: v for k, v in self._from_imports.items() if k.endswith("|std")}

    @property
    def _third_from(self) -> dict[str, set[str]]:
        """Get third-party from-imports."""
        return {k: v for k, v in self._from_imports.items() if k.endswith("|third")}

    @property
    def _local_from(self) -> dict[str, set[str]]:
        """Get local from-imports."""
        return {k: v for k, v in self._from_imports.items() if k.endswith("|local")}

    @property
    def result(self) -> BufferHelper:
        """Get the internal buffer, initializing it if necessary."""
        if self._result is None:
            self._result = BufferHelper()
        return self._result

    def _render_imports(self, name: str, imports: dict[str, set[str]], blank: bool = True) -> None:
        """Render a set of imports into formatted strings."""
        import_name: str = f"_{name}_imports"
        if getattr(self, import_name) or imports:
            for module in sorted(getattr(self, import_name)):
                self._import(module)
            for key in sorted(imports.keys()):
                module: str = first_item(key.split(ch.PIPE))
                names: str = COMMA_SPACE.join(sorted(imports[key]))
                self._from_import(module, names)
            if blank:
                self._insert_newline()

    def render(self) -> str:
        """Render all imports organized by category.

        Returns:
            Formatted import statements with proper grouping.
        """
        if self._future_imports:
            for module in sorted(self._future_imports):
                self._from_import(module, "annotations")
            self._insert_newline()
        self._render_imports("standard", self._std_from)
        self._render_imports("third_party", self._third_from)
        self._render_imports("local", self._local_from, blank=False)
        return self.result.getvalue()

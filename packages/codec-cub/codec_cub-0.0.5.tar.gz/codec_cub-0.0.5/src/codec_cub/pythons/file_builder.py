"""A simple in-memory string buffer that helps with dynamically creating files."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Literal

from codec_cub.common import COMMA_SPACE, first_token
from funcy_bear.constants.characters import COLON, DOUBLE_QUOTE, EMPTY_STRING, INDENT, NEWLINE, PIPE, SINGLE_QUOTE

from ._buffer import BufferHelper
from .helpers import Decorator, get_decorators
from .parts import Docstring

if TYPE_CHECKING:
    from collections.abc import Generator

Sections = Literal["header", "imports", "type_checking", "body", "footer"]


class CodeSection:
    """A code section buffer with indentation management and context managers for code blocks."""

    def __init__(self, name: Sections) -> None:
        """Initialize the CodeSection with a name and empty buffer."""
        self.section_name: str = name
        self._buffer: list[str] = []
        self._current_indent: int = 0

    def add(self, line: str, indent: int = 0) -> None:
        """Add a line to the buffer with the current indentation.

        Args:
            line: The line to add to the buffer.
            indent: Relative indent change (can be negative to outdent).
        """
        self._current_indent += indent
        indented_line: str = INDENT * self._current_indent + line
        self._buffer.append(indented_line)

    def add_blank(self) -> None:
        """Add a blank line to the buffer."""
        self._buffer.append(EMPTY_STRING)

    def set_indent(self, level: int) -> None:
        """Set the absolute indentation level.

        Args:
            level: The indentation level to set (0 = no indent).
        """
        self._current_indent = level

    def reset_indent(self) -> None:
        """Reset indentation to 0."""
        self._current_indent = 0

    def get(self) -> list[str]:
        """Get the current buffer lines.

        Returns:
            A list of strings representing the buffer lines.
        """
        return self._buffer

    @contextmanager
    def block(self, header: str) -> Generator[None, Any]:
        """Context manager for a generic code block with automatic indentation.

        Args:
            header: The header line (will have colon appended if not present).

        Yields:
            None
        """
        header_line: str = header if header.endswith(COLON) else header + COLON
        self.add(header_line)
        self._current_indent += 1
        try:
            yield
        finally:
            self._current_indent -= 1

    @contextmanager
    def function(self, name: str, args: str = EMPTY_STRING, returns: str | None = None) -> Generator[None, Any]:
        """Context manager for a function definition.

        Args:
            name: Function name.
            args: Function arguments (without parentheses).
            returns: Optional return type annotation.

        Yields:
            None
        """
        signature: str = f"def {name}({args})"
        if returns:
            signature += f" -> {returns}"
        with self.block(signature):
            yield

    @contextmanager
    def class_def(self, name: str, bases: str = EMPTY_STRING) -> Generator[None, Any]:
        """Context manager for a class definition.

        Args:
            name: Class name.
            bases: Optional base classes (without parentheses).

        Yields:
            None
        """
        class_line: str = f"class {name}({bases})" if bases else f"class {name}"
        with self.block(class_line):
            yield

    @contextmanager
    def if_block(self, condition: str):
        """Context manager for an if statement.

        Args:
            condition: The condition to test.

        Yields:
            None
        """
        with self.block(f"if {condition}"):
            yield

    @contextmanager
    def elif_block(self, condition: str) -> Generator[None, Any]:
        """Context manager for an elif statement.

        Args:
            condition: The condition to test.

        Yields:
            None
        """
        with self.block(f"elif {condition}"):
            yield

    @contextmanager
    def else_block(self) -> Generator[None, Any]:
        """Context manager for an else statement.

        Yields:
            None
        """
        with self.block("else"):
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
        with_line: str = f"with {expression}"
        if as_var:
            with_line += f" as {as_var}"
        with self.block(with_line):
            yield

    @contextmanager
    def try_block(self) -> Generator[None, Any]:
        """Context manager for a try statement.

        Yields:
            None
        """
        with self.block("try"):
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
        except_line = "except"
        if exception:
            except_line += f" {exception}"
        if as_var:
            except_line += f" as {as_var}"
        with self.block(except_line):
            yield

    @contextmanager
    def finally_block(self) -> Generator[None, Any]:
        """Context manager for a finally statement.

        Yields:
            None
        """
        with self.block("finally"):
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
        with self.block(f"for {variable} in {iterable}"):
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
        self._sections[section].add(line, indent)

    def get_section(self, section: Sections) -> CodeSection:
        """Get a specific section buffer for direct manipulation.

        Args:
            section: The section to retrieve.

        Returns:
            The CodeSection for the specified section.
        """
        return self._sections[section]

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
                    output_lines.append(EMPTY_STRING)
                output_lines.extend(section_lines)

        return "\n".join(output_lines)


class EnumBuilder:
    """General-purpose enum builder for Enum, IntEnum, StrEnum, Flag, etc.

    Supports all enum types by specifying the base class.
    """

    def __init__(
        self,
        name: str,
        members: dict[str, str | int] | list[str],
        base_class: str = "Enum",
        decorators: list[str] | list[Decorator] | None = None,
        docstring: str = EMPTY_STRING,
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
            self._members = dict.fromkeys(members, "auto()")
        else:
            self._members = members
        self._decorators: str = get_decorators(decorators) if decorators else EMPTY_STRING
        self._docstring: Docstring = Docstring(docstring)

    def render(self) -> str:
        """Render the enum to a string.

        Returns:
            The complete enum definition as a string.
        """
        result = BufferHelper()

        if self._decorators:
            result.write(self._decorators, suffix=NEWLINE)

        result.write(f"class {self.name}({self.base_class}){COLON}", suffix=NEWLINE)

        body = BufferHelper(indent=1)
        if self._docstring:
            body.write(self._docstring.render(), suffix=NEWLINE)
            body.write(EMPTY_STRING, suffix=NEWLINE)

        for member_name, member_value in self._members.items():
            mem_val: Any = member_value
            if isinstance(member_value, str) and not member_value.startswith(
                ("auto()", f"{DOUBLE_QUOTE}", f"{SINGLE_QUOTE}")
            ):
                mem_val = f"{DOUBLE_QUOTE}{member_value}{DOUBLE_QUOTE}"
            body.write(f"{member_name} = {mem_val}", suffix=NEWLINE)

        result.write(body.getvalue())
        return result.getvalue()


class ImportManager:
    """Manages imports and automatically deduplicates them.

    Organizes imports into standard library, third-party, and local sections.
    """

    def __init__(self) -> None:
        """Initialize the ImportManager."""
        self._future_imports: set[str] = set()
        self._standard_imports: set[str] = set()
        self._third_party_imports: set[str] = set()
        self._local_imports: set[str] = set()
        self._from_imports: dict[str, set[str]] = {}

    def add_import(self, module: str, *, is_third_party: bool = False, is_local: bool = False) -> None:
        """Add a simple import statement.

        Args:
            module: Module name to import.
            is_third_party: Whether this is a third-party module.
            is_local: Whether this is a local/relative import.
        """
        if module.startswith("__future__"):
            return self._future_imports.add(module)
        if is_local:
            return self._local_imports.add(module)
        if is_third_party:
            return self._third_party_imports.add(module)
        return self._standard_imports.add(module)

    def add_from_import(
        self,
        module: str,
        names: str | list[str],
        *,
        is_third_party: bool = False,
        is_local: bool = False,
    ) -> None:
        """Add a from...import statement.

        Args:
            module: Module to import from.
            names: Single name or list of names to import.
            is_third_party: Whether this is a third-party module.
            is_local: Whether this is a local/relative import.
        """
        if isinstance(names, str):
            names = [names]

        key: str = f"{module}{PIPE}{'third' if is_third_party else 'local' if is_local else 'std'}"
        if key not in self._from_imports:
            self._from_imports[key] = set()
        self._from_imports[key].update(names)

    def render(self) -> str:
        """Render all imports organized by category.

        Returns:
            Formatted import statements with proper grouping.
        """
        result = BufferHelper()

        if self._future_imports:
            for module in sorted(self._future_imports):
                result.write(f"from {module} import annotations", suffix=NEWLINE)
            result.write(EMPTY_STRING, suffix=NEWLINE)

        std_from: dict[str, set[str]] = {k: v for k, v in self._from_imports.items() if k.endswith("|std")}
        if self._standard_imports or std_from:
            for module in sorted(self._standard_imports):
                result.write(f"import {module}", suffix=NEWLINE)
            for key in sorted(std_from.keys()):
                module = first_token(key.split(PIPE))
                names = COMMA_SPACE.join(sorted(std_from[key]))
                result.write(f"from {module} import {names}", suffix=NEWLINE)
            result.write(EMPTY_STRING, suffix=NEWLINE)

        third_from: dict[str, set[str]] = {k: v for k, v in self._from_imports.items() if k.endswith("|third")}
        if self._third_party_imports or third_from:
            for module in sorted(self._third_party_imports):
                result.write(f"import {module}", suffix=NEWLINE)
            for key in sorted(third_from.keys()):
                module: str = first_token(key.split(PIPE))
                names: str = COMMA_SPACE.join(sorted(third_from[key]))
                result.write(f"from {module} import {names}", suffix=NEWLINE)
            result.write(EMPTY_STRING, suffix=NEWLINE)

        local_from: dict[str, set[str]] = {k: v for k, v in self._from_imports.items() if k.endswith("|local")}
        if self._local_imports or local_from:
            for module in sorted(self._local_imports):
                result.write(f"import {module}", suffix=NEWLINE)
            for key in sorted(local_from.keys()):
                module = first_token(key.split(PIPE))
                names = COMMA_SPACE.join(sorted(local_from[key]))
                result.write(f"from {module} import {names}", suffix=NEWLINE)
        return result.getvalue()

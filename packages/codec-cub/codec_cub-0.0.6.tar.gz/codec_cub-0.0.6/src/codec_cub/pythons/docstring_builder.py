"""Builder for structured Python docstrings in Google style."""

from __future__ import annotations

from typing import Self

from codec_cub.pythons._buffer import BufferHelper
from funcy_bear.constants import characters as ch
from funcy_bear.ops.strings.manipulation import join


class DocstringBuilder:
    """Fluent API for building Google-style docstrings.

    Examples:
        >>> doc = DocstringBuilder() \
        ...     .summary("Get storage backend by name.") \
        ...     .arg("storage", "Backend name") \
        ...     .returns("Storage class")
        >>> print(doc.render())
        Get storage backend by name.

    Args:
            storage: Backend name

    Returns:
            Storage class
    """

    __DOCSTRING_BUILDER__ = True

    def __init__(self, indent: int = 0) -> None:
        """Initialize an empty docstring builder."""
        self._summary: str = ch.EMPTY_STRING
        self._description: str = ch.EMPTY_STRING
        self._args: list[tuple[str, str]] = []
        self._returns: str = ch.EMPTY_STRING
        self._raises: list[tuple[str, str]] = []
        self._yields: str = ch.EMPTY_STRING
        self._examples: list[str] = []
        self._notes: list[str] = []
        self._buffer: BufferHelper | None = None
        self.indent: int = indent

    @property
    def buffer(self) -> BufferHelper:
        """Get or create the internal buffer."""
        if self._buffer is None:
            self._buffer = BufferHelper(indent=self.indent)
        return self._buffer

    def summary(self, text: str) -> Self:
        """Set the summary line (first line of docstring).

        Args:
            text: Summary text (should be one line).

        Returns:
            Self for method chaining.
        """
        self._summary = text
        return self

    def description(self, text: str) -> Self:
        """Set the extended description.

        Args:
            text: Description text (can be multiple lines).

        Returns:
            Self for method chaining.
        """
        self._description = text
        return self

    def arg(self, name: str, description: str) -> Self:
        """Add an argument description.

        Args:
            name: Parameter name.
            description: Parameter description.

        Returns:
            Self for method chaining.
        """
        self._args.append((name, description))
        return self

    def returns(self, description: str) -> Self:
        """Set the return value description.

        Args:
            description: Return value description.

        Returns:
            Self for method chaining.
        """
        self._returns = description
        return self

    def raises(self, exception: str, description: str) -> Self:
        """Add an exception that can be raised.

        Args:
            exception: Exception class name.
            description: When/why the exception is raised.

        Returns:
            Self for method chaining.
        """
        self._raises.append((exception, description))
        return self

    def yields(self, description: str) -> Self:
        """Set the yields description for generators.

        Args:
            description: What the generator yields.

        Returns:
            Self for method chaining.
        """
        self._yields = description
        return self

    def example(self, code: str) -> Self:
        """Add a usage example.

        Args:
            code: Example code (will be indented appropriately).

        Returns:
            Self for method chaining.
        """
        self._examples.append(code)
        return self

    def note(self, text: str) -> Self:
        """Add a note section.

        Args:
            text: Note text.

        Returns:
            Self for method chaining.
        """
        self._notes.append(text)
        return self

    def _header(self, title: str) -> None:
        """Add a section header."""
        self.buffer.newline()
        with self.buffer.indented():
            self.buffer.write(title, suffix=ch.NEWLINE)

    def _add_section(self, header: str, content: str) -> None:
        """Add a simple section with header and single indented line.

        Args:
            b: The buffer to write to.
            header: Section header (e.g., "Returns:").
            content: Section content (will be indented).
        """
        self._header(header)
        with self.buffer.indented(2):
            self.buffer.write(content, suffix=ch.NEWLINE)

    def _add_list_section(self, header: str, items: list[tuple[str, str]]) -> None:
        """Add a section with multiple indented items.

        Args:
            b: The buffer to write to.
            header: Section header (e.g., "Args:", "Raises:").
            items: List of (name, description) tuples.
        """
        self._header(header)
        with self.buffer.indented(2):
            for name, desc in items:
                self.buffer.write(f"{name}: {desc}", suffix=ch.NEWLINE)

    def _add_examples(self, header: str, examples: list[str]) -> None:
        """Add an examples section with multiple code examples.

        Args:
            b: The buffer to write to.
            examples: List of example code strings.
        """
        self._header(header)
        with self.buffer.indented(2):
            for example in examples:
                for line in example.split(ch.NEWLINE):
                    self.buffer.write(line, suffix=ch.NEWLINE) if line else self.buffer.write(ch.NEWLINE)

    def _add_notes(self, header: str, notes: list[str]) -> None:
        """Add a notes section with multiple notes.

        Args:
            b: The buffer to write to.
            notes: List of note strings.
        """
        self._header(header)
        with self.buffer.indented(2):
            for note in notes:
                self.buffer.write(note, suffix=ch.NEWLINE)

    @property
    def empty(self) -> bool:
        """Check if the docstring is empty.

        Returns:
            True if no content has been added, False otherwise.
        """
        return not any(
            [
                self._summary,
                self._description,
                self._args,
                self._returns,
                self._raises,
                self._yields,
                self._examples,
                self._notes,
            ]
        )

    @property
    def multiline(self) -> bool:
        """Check if the docstring is multiline.

        Returns:
            True if the docstring has multiple lines, False otherwise.
        """
        return bool(
            self._description
            or len(self._args) > 0
            or self._returns
            or len(self._raises) > 0
            or self._yields
            or len(self._examples) > 0
            or len(self._notes) > 0
        )

    def render(self) -> str:
        """Render the docstring to a string.

        Returns:
            The formatted docstring content (without triple quotes).
        """
        if self.empty:
            return ch.EMPTY_STRING
        if self._summary:
            self.buffer.write(self._summary, suffix=ch.NEWLINE)
        if self._description:
            self.buffer.newline()
            self.buffer.write(self._description, suffix=ch.NEWLINE)
        if self._args:
            self._add_list_section("Args:", self._args)
        if self._returns:
            self._add_section("Returns:", self._returns)
        if self._yields:
            self._add_section("Yields:", self._yields)
        if self._raises:
            self._add_list_section("Raises:", self._raises)
        if self._examples:
            self._add_examples("Examples:", self._examples)
        if self._notes:
            self._add_notes("Note:", self._notes)
        suffix: str = join(ch.NEWLINE, ch.INDENT) if self.multiline else ch.EMPTY_STRING
        value: str = join(self.buffer.getvalue().rstrip(ch.NEWLINE), suffix)
        self.clear()
        return value

    def clear(self) -> Self:
        """Clear all docstring content."""
        self._summary = ch.EMPTY_STRING
        self._description = ch.EMPTY_STRING
        self._args.clear()
        self._returns = ch.EMPTY_STRING
        self._raises.clear()
        self._yields = ch.EMPTY_STRING
        self._examples.clear()
        self._notes.clear()
        if self._buffer:
            self._buffer = None
        return self

    def __str__(self) -> str:
        """String representation (calls render)."""
        return self.render()

    def __repr__(self) -> str:
        """Repr representation."""
        return f"DocstringBuilder(summary={self._summary!r})"

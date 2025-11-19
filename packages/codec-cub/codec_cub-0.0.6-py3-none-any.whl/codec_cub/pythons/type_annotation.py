"""Type annotation builder for generating Python type hints."""

from __future__ import annotations

from typing import Self

from codec_cub.common import comma_sep, piped
from funcy_bear.ops.strings import manipulation as man


class TypeAnnotation:
    """Builder for Python type annotations with support for generics, unions, and literals.

    Examples:
        >>> TypeAnnotation("int").render()
        'int'
        >>> TypeAnnotation.literal("foo", "bar").render()
        'Literal["foo", "bar"]'
        >>> TypeAnnotation.type_of("Storage").render()
        'type[Storage]'
        >>> TypeAnnotation.dict_of("str", "int").render()
        'dict[str, int]'
        >>> TypeAnnotation.optional("str").render()
        'str | None'
    """

    __TYPE_ANNOTATION__ = True

    def __init__(self, type_name: str) -> None:
        """Initialize a simple type annotation.

        Args:
            type_name: The name of the type (e.g., "int", "str", "MyClass").
        """
        self._annotation: str = type_name

    @classmethod
    def literal(cls, *values: str | int | bool) -> Self:
        """Create a Literal type annotation.

        Args:
            *values: The literal values. Strings will be quoted.

        Returns:
            TypeAnnotation for a Literal type.

        Examples:
            >>> TypeAnnotation.literal("foo", "bar").render()
            'Literal["foo", "bar"]'
            >>> TypeAnnotation.literal(1, 2, 3).render()
            'Literal[1, 2, 3]'
        """
        formatted_values: list[str] = []
        for value in values:
            if isinstance(value, str):
                formatted_values.append(man.quoted(value))
            else:
                formatted_values.append(str(value))

        values_str: str = comma_sep(formatted_values)
        instance: Self = cls.__new__(cls)
        instance._annotation = f"Literal[{values_str}]"
        return instance

    @classmethod
    def type_of(cls, type_name: str) -> Self:
        """Create a type[T] annotation.

        Args:
            type_name: The type name (e.g., "Storage", "BaseModel").

        Returns:
            TypeAnnotation for a type[T].

        Examples:
            >>> TypeAnnotation.type_of("Storage").render()
            'type[Storage]'
        """
        instance: Self = cls.__new__(cls)
        instance._annotation = f"type{man.bracketed(type_name)}"
        return instance

    @classmethod
    def dict_of(cls, key_type: str | TypeAnnotation, value_type: str | TypeAnnotation) -> Self:
        """Create a dict[K, V] annotation.

        Args:
            key_type: The key type.
            value_type: The value type.

        Returns:
            TypeAnnotation for a dict[K, V].

        Examples:
            >>> TypeAnnotation.dict_of("str", "int").render()
            'dict[str, int]'
        """
        key_str: str = key_type.render() if isinstance(key_type, TypeAnnotation) else key_type
        value_str: str = value_type.render() if isinstance(value_type, TypeAnnotation) else value_type
        instance: Self = cls.__new__(cls)
        instance._annotation = f"dict{man.bracketed(f'{key_str}, {value_str}')}"
        return instance

    @classmethod
    def list_of(cls, item_type: str | TypeAnnotation) -> Self:
        """Create a list[T] annotation.

        Args:
            item_type: The item type.

        Returns:
            TypeAnnotation for a list[T].

        Examples:
            >>> TypeAnnotation.list_of("str").render()
            'list[str]'
        """
        item_str: str = item_type.render() if isinstance(item_type, TypeAnnotation) else item_type

        instance: Self = cls.__new__(cls)
        instance._annotation = f"list{man.bracketed(item_str)}"
        return instance

    @classmethod
    def set_of(cls, item_type: str | TypeAnnotation) -> Self:
        """Create a set[T] annotation.

        Args:
            item_type: The item type.

        Returns:
            TypeAnnotation for a set[T].

        Examples:
            >>> TypeAnnotation.set_of("int").render()
            'set[int]'
        """
        item_str: str = item_type.render() if isinstance(item_type, TypeAnnotation) else item_type

        instance: Self = cls.__new__(cls)
        instance._annotation = f"set{man.bracketed(item_str)}"
        return instance

    @classmethod
    def tuple_of(cls, *types: str | TypeAnnotation) -> Self:
        """Create a tuple[T1, T2, ...] annotation.

        Args:
            *types: The element types.

        Returns:
            TypeAnnotation for a tuple.

        Examples:
            >>> TypeAnnotation.tuple_of("str", "int", "bool").render()
            'tuple[str, int, bool]'
        """
        types_str: str = comma_sep([t.render() if isinstance(t, TypeAnnotation) else t for t in types])
        instance: Self = cls.__new__(cls)
        instance._annotation = f"tuple{man.bracketed(types_str)}"
        return instance

    @classmethod
    def optional(cls, type_name: str | TypeAnnotation) -> Self:
        """Create a T | None annotation.

        Args:
            type_name: The type that can be None.

        Returns:
            TypeAnnotation for T | None.

        Examples:
            >>> TypeAnnotation.optional("str").render()
            'str | None'
        """
        type_str: str = type_name if isinstance(type_name, str) else type_name.render()
        instance: Self = cls.__new__(cls)
        instance._annotation = f"{type_str} | None"
        return instance

    @classmethod
    def union(cls, *types: str | TypeAnnotation) -> Self:
        """Create a T1 | T2 | ... union annotation.

        Args:
            *types: The types in the union.

        Returns:
            TypeAnnotation for a union type.

        Examples:
            >>> TypeAnnotation.union("str", "int", "bool").render()
            'str | int | bool'
        """
        union_str: str = piped(*[t.render() if isinstance(t, TypeAnnotation) else t for t in types])
        instance: Self = cls.__new__(cls)
        instance._annotation = union_str
        return instance

    @classmethod
    def generic(cls, base: str, *type_params: str | TypeAnnotation) -> Self:
        """Create a generic type annotation like Generic[T1, T2].

        Args:
            base: The base type name (e.g., "Callable", "Iterator").
            *type_params: The type parameters.

        Returns:
            TypeAnnotation for a generic type.

        Examples:
            >>> TypeAnnotation.generic("Callable", "int", "str").render()
            'Callable[int, str]'
            >>> TypeAnnotation.generic("Iterator", "str").render()
            'Iterator[str]'
        """
        params_str: str = comma_sep([p.render() if isinstance(p, TypeAnnotation) else p for p in type_params])
        instance: Self = cls.__new__(cls)
        instance._annotation = f"{base}{man.bracketed(params_str)}"
        return instance

    def render(self) -> str:
        """Render the type annotation to a string.

        Returns:
            The type annotation as a string.
        """
        return self._annotation

    def __str__(self) -> str:
        """String representation (calls render)."""
        return self.render()

    def __repr__(self) -> str:
        """Repr representation."""
        return f"TypeAnnotation({self._annotation!r})"

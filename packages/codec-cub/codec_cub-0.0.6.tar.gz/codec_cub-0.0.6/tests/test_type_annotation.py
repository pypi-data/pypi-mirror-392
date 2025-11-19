"""Tests for TypeAnnotation builder."""

from __future__ import annotations

from codec_cub.pythons.type_annotation import TypeAnnotation


def test_simple_type() -> None:
    """Test simple type annotations."""
    assert TypeAnnotation("int").render() == "int"
    assert TypeAnnotation("str").render() == "str"
    assert TypeAnnotation("MyClass").render() == "MyClass"


def test_literal_strings() -> None:
    """Test Literal type with string values."""
    result: str = TypeAnnotation.literal("foo", "bar", "baz").render()
    assert result == 'Literal["foo", "bar", "baz"]'


def test_literal_mixed() -> None:
    """Test Literal type with mixed values."""
    result: str = TypeAnnotation.literal("active", 1, True).render()  # noqa: FBT003
    assert result == 'Literal["active", 1, True]'


def test_literal_numbers() -> None:
    """Test Literal type with numeric values."""
    result: str = TypeAnnotation.literal(1, 2, 3).render()
    assert result == "Literal[1, 2, 3]"


def test_type_of() -> None:
    """Test type[T] annotations."""
    assert TypeAnnotation.type_of("Storage").render() == "type[Storage]"
    assert TypeAnnotation.type_of("BaseModel").render() == "type[BaseModel]"


def test_dict_of_strings() -> None:
    """Test dict[K, V] with string types."""
    result: str = TypeAnnotation.dict_of("str", "int").render()
    assert result == "dict[str, int]"


def test_dict_of_nested() -> None:
    """Test dict[K, V] with nested TypeAnnotation."""
    value_type = TypeAnnotation.list_of("str")
    result = TypeAnnotation.dict_of("str", value_type).render()
    assert result == "dict[str, list[str]]"


def test_list_of() -> None:
    """Test list[T] annotations."""
    assert TypeAnnotation.list_of("str").render() == "list[str]"
    assert TypeAnnotation.list_of("int").render() == "list[int]"


def test_list_of_nested() -> None:
    """Test list[T] with nested TypeAnnotation."""
    inner_type: TypeAnnotation = TypeAnnotation.dict_of("str", "int")
    result: str = TypeAnnotation.list_of(inner_type).render()
    assert result == "list[dict[str, int]]"


def test_set_of() -> None:
    """Test set[T] annotations."""
    assert TypeAnnotation.set_of("int").render() == "set[int]"
    assert TypeAnnotation.set_of("str").render() == "set[str]"


def test_tuple_of() -> None:
    """Test tuple[T1, T2, ...] annotations."""
    result = TypeAnnotation.tuple_of("str", "int", "bool").render()
    assert result == "tuple[str, int, bool]"


def test_tuple_of_nested() -> None:
    """Test tuple with nested types."""
    list_type = TypeAnnotation.list_of("str")
    result = TypeAnnotation.tuple_of("int", list_type).render()
    assert result == "tuple[int, list[str]]"


def test_optional() -> None:
    """Test T | None annotations."""
    assert TypeAnnotation.optional("str").render() == "str | None"
    assert TypeAnnotation.optional("int").render() == "int | None"


def test_optional_nested() -> None:
    """Test optional with nested type."""
    list_type = TypeAnnotation.list_of("str")
    result = TypeAnnotation.optional(list_type).render()
    assert result == "list[str] | None"


def test_union() -> None:
    """Test union types."""
    result = TypeAnnotation.union("str", "int", "bool").render()
    assert result == "str | int | bool"


def test_union_nested() -> None:
    """Test union with nested types."""
    list_type: TypeAnnotation = TypeAnnotation.list_of("str")
    dict_type: TypeAnnotation = TypeAnnotation.dict_of("str", "int")
    result = TypeAnnotation.union(list_type, dict_type, "None").render()
    assert result == "list[str] | dict[str, int] | None"


def test_generic() -> None:
    """Test generic type annotations."""
    result = TypeAnnotation.generic("Iterator", "str").render()
    assert result == "Iterator[str]"


def test_generic_callable() -> None:
    """Test Callable generic type."""
    result = TypeAnnotation.generic("Callable", "int", "str").render()
    assert result == "Callable[int, str]"


def test_complex_nested() -> None:
    """Test complex nested type annotations."""
    # dict[str, list[tuple[int, str]]]
    tuple_type = TypeAnnotation.tuple_of("int", "str")
    list_type = TypeAnnotation.list_of(tuple_type)
    result = TypeAnnotation.dict_of("str", list_type).render()
    assert result == "dict[str, list[tuple[int, str]]]"


def test_str_method() -> None:
    """Test __str__ method."""
    type_ann = TypeAnnotation.dict_of("str", "int")
    assert str(type_ann) == "dict[str, int]"


def test_repr_method() -> None:
    """Test __repr__ method."""
    type_ann = TypeAnnotation("int")
    assert repr(type_ann) == "TypeAnnotation('int')"

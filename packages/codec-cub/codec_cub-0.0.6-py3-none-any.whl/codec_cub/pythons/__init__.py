"""A codec and builder for Python files.

Python Database (PyDB) provides a way to store structured data in executable
Python modules. Files are human-readable, version-controllable, and natively
importable without parsing.

The Python builders provide general-purpose code generation for any Python code,
not just PyDB. They support dataclasses, Pydantic models, enums, and more.

Example (PyDB):
    >>> from codec_cub.pythons import PyDBCodec
    >>> codec = PyDBCodec()
    >>> codec.create(Path("data.py"), version=(1, 0, 0), tables={...})
    >>> codec.append_row(Path("data.py"), {"id": 1, "name": "Alice"})
    >>> module = codec.load(Path("data.py"))

Example (Python Builders):
    >>> from codec_cub.pythons import ClassBuilder, Attribute, Decorator
    >>> user_class = ClassBuilder(
    ...     name="User",
    ...     decorators=[Decorator("dataclass")],
    ...     attributes=[
    ...         Attribute("id", int),
    ...         Attribute("name", str),
    ...     ],
    ... )
    >>> print(user_class.render())
"""

from __future__ import annotations

from .class_builder import ClassBuilder
from .codec import PyDBCodec
from .docstring_builder import DocstringBuilder
from .file_builder import EnumBuilder, FileBuilder, ImportManager
from .fluent_builders import DictLiteralBuilder, ListLiteralBuilder, TypeAliasBuilder, VariableBuilder
from .function_builder import FunctionBuilder
from .helpers import (
    generate_all_export,
    generate_dict_literal,
    generate_list_literal,
    get_literal_type,
    get_type_alias,
)
from .parts import Arg, Attribute, Decorator, Docstring, Variable
from .type_annotation import TypeAnnotation

__all__ = [
    "Arg",
    "Attribute",
    "ClassBuilder",
    "Decorator",
    "DictLiteralBuilder",
    "Docstring",
    "DocstringBuilder",
    "EnumBuilder",
    "FileBuilder",
    "FunctionBuilder",
    "ImportManager",
    "ListLiteralBuilder",
    "PyDBCodec",
    "TypeAliasBuilder",
    "TypeAnnotation",
    "Variable",
    "VariableBuilder",
    "generate_all_export",
    "generate_dict_literal",
    "generate_list_literal",
    "get_literal_type",
    "get_type_alias",
]

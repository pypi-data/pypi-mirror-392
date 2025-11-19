"""Type-based handlers for packing Python objects into MessagePack."""

from __future__ import annotations

from collections.abc import Mapping
from functools import partial
from struct import pack as struct_pack
from types import NoneType
from typing import Any

from funcy_bear.tools.dispatcher import Dispatcher
from funcy_bear.type_stuffs.validate import is_instance_of

from .common import ByteFileProtocol, in_range
from .common._fix_families import NEG_FIXINT, POS_FIXINT, FixFamily
from .common._msgpack_tag import INT_TYPES, Tag
from .common.exceptions import PackError

single = Dispatcher(arg="obj")
_int = Dispatcher(arg="x")


@_int.dispatcher()
def pack_ints(x: int, buf: ByteFileProtocol) -> None:  # noqa: ARG001
    """Pack an integer using range-based dispatch."""
    raise ValueError(f"No handler for integer value: {x}")


def _pack_int(x: int, buf: ByteFileProtocol, data_type: FixFamily | Tag) -> None:
    """Pack an integer into the buffer based on its range."""
    if isinstance(data_type, FixFamily):
        fix: FixFamily = data_type
        if data_type == POS_FIXINT:
            return buf.write_byte(x)
        if data_type == NEG_FIXINT:
            return buf.write_byte(fix.meta.base | (x & fix.meta.extract_mask))
    if isinstance(data_type, Tag):
        tag: Tag = data_type
        buf.write_byte(int(tag))
        return buf.write(tag.meta.be_bytes(x))
    raise ValueError(f"Unsupported data type for packing: {data_type}")


_int.register(partial(in_range, enum=POS_FIXINT), data_type=POS_FIXINT)(_pack_int)
_int.register(partial(in_range, enum=NEG_FIXINT), data_type=NEG_FIXINT)(_pack_int)

for int_type in INT_TYPES:
    _int.register(partial(in_range, enum=int_type), data_type=int_type)(_pack_int)


@single.dispatcher()
def pack_into(obj: Any, **kwargs) -> None:  # noqa: ARG001
    """Pack any Python object into MessagePack bytes."""
    raise PackError(f"Unsupported type for packing: {type(obj).__name__}")


@single.register(partial(is_instance_of, types=NoneType))
def pack_nil(obj: NoneType, **kwargs) -> None:  # noqa: ARG001
    """Pack None as NIL tag."""
    buf: ByteFileProtocol = kwargs.pop("buf")
    buf.write_byte(Tag.NIL)


@single.register(partial(is_instance_of, types=bool))
def pack_bool(obj: bool, **kwargs) -> None:
    """Pack boolean as TRUE/FALSE tag."""
    buf: ByteFileProtocol = kwargs.pop("buf")
    buf.write_byte(Tag.TRUE if obj else Tag.FALSE)


@single.register(partial(is_instance_of, types=int))
def pack_int(obj: int, **kwargs) -> None:
    """Pack integer using range-based dispatch."""
    buf: ByteFileProtocol = kwargs.pop("buf")
    pack_ints(x=obj, buf=buf)


@single.register(partial(is_instance_of, types=float))
def pack_float(obj: float, **kwargs) -> None:
    """Pack float as FLOAT64."""
    buf: ByteFileProtocol = kwargs.pop("buf")
    buf.write_byte(Tag.FLOAT64)
    buf.write(struct_pack(">d", obj))


@single.register(partial(is_instance_of, types=str))
def pack_str(obj: str | bytes, **kwargs) -> None:
    """Pack string with appropriate length encoding."""
    buf: ByteFileProtocol = kwargs.pop("buf")
    if isinstance(obj, str):
        obj = obj.encode("utf-8")
    n: int = len(obj)
    if n <= FixFamily.FIXSTR.meta.high:
        buf.write_byte(FixFamily.FIXSTR.meta.base | n)
    elif n <= Tag.UINT8.meta.high:
        buf.write_byte(Tag.STR8)
        buf.write(Tag.UINT8.meta.be_bytes(n))
    elif n <= Tag.UINT16.meta.high:
        buf.write_byte(Tag.STR16)
        buf.write(Tag.UINT16.meta.be_bytes(n))
    else:
        buf.write_byte(Tag.STR32)
        buf.write(Tag.UINT32.meta.be_bytes(n))
    buf.write(obj)


@single.register(partial(is_instance_of, types=bytes))
def pack_bin(obj: bytes, **kwargs) -> None:
    """Pack binary obj with appropriate length encoding."""
    buf: ByteFileProtocol = kwargs.pop("buf")
    n: int = len(obj)
    if n <= Tag.UINT8.meta.high:
        buf.write_byte(Tag.BIN8)
        buf.write(Tag.UINT8.meta.be_bytes(n))
    elif n <= Tag.UINT16.meta.high:
        buf.write_byte(Tag.BIN16)
        buf.write(Tag.UINT16.meta.be_bytes(n))
    else:
        buf.write_byte(Tag.BIN32)
        buf.write(Tag.UINT32.meta.be_bytes(n))
    buf.write(obj)


@single.register(partial(is_instance_of, types=(list, tuple)))
def pack_list(obj: list | tuple, **kwargs) -> None:
    """Pack list/tuple with appropriate length encoding."""
    buf: ByteFileProtocol = kwargs.pop("buf")
    n: int = len(obj)
    if n <= FixFamily.FIXARRAY.meta.high:
        buf.write_byte(FixFamily.FIXARRAY.meta.base | n)
    elif n <= Tag.UINT16.meta.high:
        buf.write_byte(Tag.ARRAY16)
        buf.write(Tag.UINT16.meta.be_bytes(n))
    else:
        buf.write_byte(Tag.ARRAY32)
        buf.write(Tag.UINT32.meta.be_bytes(n))
    for o in obj:
        pack_into(obj=o, buf=buf)


@single.register(partial(is_instance_of, types=Mapping))
def pack_mapping(obj: Mapping, **kwargs) -> None:
    """Pack mapping with appropriate length encoding."""
    buf: ByteFileProtocol = kwargs.pop("buf")
    n: int = len(obj)
    if n <= FixFamily.FIXMAP.meta.high:
        buf.write_byte(FixFamily.FIXMAP.meta.base | n)
    elif n <= Tag.UINT16.meta.high:
        buf.write_byte(Tag.MAP16)
        buf.write(Tag.UINT16.meta.be_bytes(n))
    else:
        buf.write_byte(Tag.MAP32)
        buf.write(Tag.UINT32.meta.be_bytes(n))
    for k, v in sorted(obj.items(), key=lambda kv: kv[0]):
        pack_into(obj=k, buf=buf)
        pack_into(obj=v, buf=buf)

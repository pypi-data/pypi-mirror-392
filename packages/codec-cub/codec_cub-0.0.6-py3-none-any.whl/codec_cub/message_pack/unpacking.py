"""MessagePack unpacking functionality."""

from io import BytesIO
from typing import Any

from codec_cub.message_pack._unpacking import unpack_fix, unpack_tags
from codec_cub.message_pack.common._fix_families import FixFamily
from codec_cub.message_pack.common._msgpack_tag import Tag
from codec_cub.message_pack.common.exceptions import InvalidMsgPackTagError
from codec_cub.text.bytes_handler import BytesFileHandler


def unpack_one(br: BytesFileHandler) -> Any:
    """Unpack a single MessagePack object from the byte reader."""
    b: bytes = br.read(n=1, tick=1)
    byte_val: int = int.from_bytes(b, "big")

    for fix_family in FixFamily.values():
        if fix_family.meta.matches(byte_val):
            return unpack_fix(byte_val, br)

    tag: Tag | None = Tag.get(byte_val, None)
    if tag is not None:
        return unpack_tags(tag, br)
    raise InvalidMsgPackTagError(f"No handler for tag: {tag}")


def unpack(data: bytes) -> Any:
    """Unpack MessagePack bytes into a Python object."""
    buf = BytesFileHandler(buffer=BytesIO(data))
    return unpack_one(buf)

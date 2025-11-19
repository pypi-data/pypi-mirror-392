import os

from arua.compression.core import decompress as core_decompress
from arua.compression.semantic_x import compress, decompress


def test_sx_roundtrip_text() -> None:
    data = ("hello world " * 50).encode("utf-8")
    compressed = compress(data)
    out = decompress(compressed)
    assert out == data


def test_sx_small_random_binaries_fallback() -> None:
    data = os.urandom(256)
    compressed = compress(data)
    # Decompression should return original binary via core decompressor
    out = decompress(compressed)
    assert out == data


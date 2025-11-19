from arua.compression.lz77 import compress, decompress


def test_lz77_roundtrip_simple():
    s = b"hello hello hello hello"
    comp = compress(s)
    out = decompress(comp)
    assert out == s


def test_lz77_random_and_repeat():
    # repeated pattern should compress
    s = b"ab" * 200 + b"cd" * 100 + b"ab" * 200
    comp = compress(s)
    out = decompress(comp)
    assert out == s


def test_lz77_empty():
    assert decompress(compress(b"")) == b""

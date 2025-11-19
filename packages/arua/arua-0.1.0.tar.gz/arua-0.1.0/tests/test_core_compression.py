from arua.compression.core import compress, decompress, METHOD_UNCOMPRESSED, METHOD_LZ77


def test_core_roundtrip_uncompressed_small():
    data = b"short"
    payload = compress(data, method="uncompressed")
    assert payload[0] == METHOD_UNCOMPRESSED
    out = decompress(payload)
    assert out == data


def test_core_roundtrip_lz77_forced():
    data = b"ab" * 100
    payload = compress(data, method="lz77")
    assert payload[0] == METHOD_LZ77
    out = decompress(payload)
    assert out == data


def test_core_auto_never_expands():
    # Random-ish data unlikely to compress
    data = bytes(range(256))
    payload = compress(data, method="auto")
    assert len(payload) <= len(data) + 1
    out = decompress(payload)
    assert out == data

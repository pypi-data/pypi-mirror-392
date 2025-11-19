from arua.compression.grain import compress, decompress
from arua.compression.semantic import semantic_compress, semantic_decompress


def test_grain_roundtrip_direct() -> None:
    data = (b"abc123" * 100) + b"tail"
    comp = compress(data)
    out = decompress(comp)
    assert out == data


def test_sg_semantic_roundtrip() -> None:
    data = (b"xyz" * 200) + b"end"
    payload = semantic_compress(data, codec="Sg", domain_id=1)
    out = semantic_decompress(payload)
    assert out == data

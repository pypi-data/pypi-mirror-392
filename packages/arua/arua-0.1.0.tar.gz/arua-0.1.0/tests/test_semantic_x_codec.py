from arua.compression.semantic import semantic_compress, semantic_decompress


def test_sx_semantic_roundtrip_text() -> None:
    data = ("hello Sx semantic " * 20).encode("utf-8")
    payload = semantic_compress(data, codec="Sx", domain_id=18)
    out = semantic_decompress(payload)
    assert out == data


def test_sx_semantic_roundtrip_binary() -> None:
    # Non-text payloads should fall back to core compressor semantics.
    data = bytes(range(256))
    payload = semantic_compress(data, codec="Sx", domain_id=19)
    out = semantic_decompress(payload)
    assert out == data


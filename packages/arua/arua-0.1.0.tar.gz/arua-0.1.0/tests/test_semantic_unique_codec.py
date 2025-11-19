from arua.compression.semantic import semantic_compress, semantic_decompress
from arua.compression.semantic_unique import reset_unique_store


def test_su_semantic_roundtrip_and_dedup() -> None:
    reset_unique_store()
    data = b"hello unique payload" * 10

    payload1 = semantic_compress(data, codec="Su", domain_id=14)
    payload2 = semantic_compress(data, codec="Su", domain_id=14)

    # Both should roundtrip correctly.
    assert semantic_decompress(payload1) == data
    assert semantic_decompress(payload2) == data

    # First Su body should be a literal (tag 0x00), second a reference (0x01).
    body1 = payload1[4:]
    body2 = payload2[4:]
    assert body1[0] == 0x00
    assert body2[0] == 0x01


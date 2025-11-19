from arua.compression.semantic_hash import encode_hash, decode_hash, verify_hash


def test_hash_roundtrip_sha256() -> None:
    data = b"semantic hash test"
    payload = encode_hash(data, algorithm="sha256")
    alg, digest = decode_hash(payload)
    assert alg == "sha256"
    assert isinstance(digest, bytes)
    assert verify_hash(data, payload) is True


def test_hash_mismatch() -> None:
    data = b"semantic hash test"
    payload = encode_hash(data, algorithm="sha256")
    assert verify_hash(b"other data", payload) is False


from arua.compression.semantic_pattern import (
    encode_pattern_slots,
    decode_pattern_slots,
)


def test_sp_slots_roundtrip_basic() -> None:
    pattern_id = 7
    slots = [None, True, 42, -3, 3.5, "hello", b"world"]
    payload = encode_pattern_slots(pattern_id, slots)
    out_pid, out_slots = decode_pattern_slots(payload)
    assert out_pid == pattern_id
    assert out_slots == [None, True, 42, -3, 3.5, "hello", b"world"]


def test_sp_slots_rejects_unsupported_type() -> None:
    pattern_id = 1
    class X:  # noqa: D401 - simple test helper
        """Dummy class."""
        pass

    try:
        encode_pattern_slots(pattern_id, [X()])  # type: ignore[arg-type]
    except TypeError:
        return
    assert False, "expected TypeError for unsupported slot type"


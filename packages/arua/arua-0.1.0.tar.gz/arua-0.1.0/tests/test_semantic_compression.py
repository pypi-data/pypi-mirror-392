from arua.compression.semantic import (
    semantic_compress,
    semantic_decompress,
    SemanticHeader,
    CODEC_ID_SA,
    CODEC_ID_SB,
    CODEC_ID_SC,
    CODEC_ID_SD,
    CODEC_ID_SE,
    CODEC_ID_SF,
    CODEC_ID_SG,
    SA_THRESHOLD,
)


def test_semantic_sa_tiny_message():
    data = b"ok"
    payload = semantic_compress(data, codec="Sa", domain_id=1)
    header, body = SemanticHeader.from_bytes(payload)
    assert header.codec_id == CODEC_ID_SA
    assert header.domain_id == 1
    assert header.template_id == 0
    out = semantic_decompress(payload)
    assert out == data


def test_semantic_sb_small_message():
    data = b"ab" * 200
    payload = semantic_compress(data, codec="Sb", domain_id=2, template_id=42)
    header, body = SemanticHeader.from_bytes(payload)
    assert header.codec_id == CODEC_ID_SB
    assert header.domain_id == 2
    assert header.template_id == 42
    # With an explicit template_id, Sb should emit a header-only payload
    # and rely on the Sb template table for the body.
    assert body == b""
    out = semantic_decompress(payload)
    assert out == data


def test_semantic_sb_without_template_falls_back_to_core():
    data = b"cd" * 200
    payload = semantic_compress(data, codec="Sb", domain_id=3)
    header, body = SemanticHeader.from_bytes(payload)
    assert header.codec_id == CODEC_ID_SB
    # Without a template_id, Sb should use the legacy core compressor.
    assert body != b""
    out = semantic_decompress(payload)
    assert out == data


def test_semantic_auto_thresholds():
    tiny = b"x" * 50
    small = b"y" * 200

    tiny_payload = semantic_compress(tiny, codec="auto", domain_id=3)
    tiny_header, _ = SemanticHeader.from_bytes(tiny_payload)
    assert tiny_header.codec_id == CODEC_ID_SA

    small_payload = semantic_compress(small, codec="auto", domain_id=4)
    small_header, _ = SemanticHeader.from_bytes(small_payload)
    assert small_header.codec_id == CODEC_ID_SB
    assert semantic_decompress(tiny_payload) == tiny
    assert semantic_decompress(small_payload) == small


def test_semantic_boundary_at_thresholds():
    tiny = b"a" * (SA_THRESHOLD - 1)
    boundary = b"b" * SA_THRESHOLD

    tiny_payload = semantic_compress(tiny, codec="auto", domain_id=5)
    tiny_header, _ = SemanticHeader.from_bytes(tiny_payload)
    assert tiny_header.codec_id == CODEC_ID_SA

    boundary_payload = semantic_compress(boundary, codec="auto", domain_id=6)
    boundary_header, _ = SemanticHeader.from_bytes(boundary_payload)
    assert boundary_header.codec_id == CODEC_ID_SB
    assert semantic_decompress(boundary_payload) == boundary


def test_semantic_non_ascii_bytes_roundtrip():
    data = "héllø 🌍".encode("utf-8")
    payload = semantic_compress(data, codec="auto", domain_id=9)
    out = semantic_decompress(payload)
    assert out == data


def test_semantic_additional_codecs_headers_only():
    data = b"semantic payload"
    for codec, expected_id in [
        ("Sc", CODEC_ID_SC),
        ("Sd", CODEC_ID_SD),
        ("Se", CODEC_ID_SE),
        ("Sf", CODEC_ID_SF),
        ("Sg", CODEC_ID_SG),
    ]:
        payload = semantic_compress(data, codec=codec, domain_id=10)
        header, _ = SemanticHeader.from_bytes(payload)
        assert header.codec_id == expected_id
        assert semantic_decompress(payload) == data

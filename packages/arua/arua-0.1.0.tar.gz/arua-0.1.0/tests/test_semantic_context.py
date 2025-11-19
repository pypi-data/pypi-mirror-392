from arua.compression.semantic_context import (
    ContextSegment,
    compress_context,
    decompress_context,
)


def test_sc_context_roundtrip_basic() -> None:
    segments = [
        ContextSegment(role="system", data=b"You are a helpful AI."),
        ContextSegment(role="user", data=b"Hello, world!"),
    ]
    payload = compress_context(segments, domain_id=30, max_seq=1024, priority="high")

    decoded_segments, meta, sc_header = decompress_context(payload)

    assert sc_header.codec_id != 0
    assert meta.priority == "high"
    assert meta.num_segments == 2
    assert [r for r, *_ in decoded_segments] == ["system", "user"]
    assert decoded_segments[0][1].startswith(b"You are a helpful AI.")
    assert decoded_segments[1][1].startswith(b"Hello, world!")


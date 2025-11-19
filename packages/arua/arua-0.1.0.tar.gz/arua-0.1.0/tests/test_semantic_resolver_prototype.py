from arua.compression.semantic_resolver import (
    resolve_and_compress,
    resolve_and_decompress,
)


def test_sr_with_sb() -> None:
    data = b"Hello world!" * 10
    compressed = resolve_and_compress(data, codec_label="Sb")
    decompressed = resolve_and_decompress(compressed)
    assert decompressed == data


def test_sr_auto() -> None:
    data = b"REPEATED_PATTERN_" * 100
    compressed = resolve_and_compress(data, codec_label=None)
    decompressed = resolve_and_decompress(compressed)
    assert decompressed == data


"""Tests for Semantic Stream (Sw) codec."""

from __future__ import annotations

import pytest

from arua.compression.semantic import semantic_compress, semantic_decompress
from arua.compression.semantic_stream import compress, decompress


class TestStreamCompression:
    """Test Sw codec compression and decompression."""

    def test_compress_decompress_simple_metadata(self):
        """Test compress/decompress with simple stream metadata."""
        data = b"stream data"
        metadata = {"sample_rate": 44100, "format": "pcm"}
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert decompressed == data
        assert decoded_metadata == metadata

    def test_compress_decompress_no_metadata(self):
        """Test compress/decompress with no metadata (empty dict)."""
        data = b"plain stream"
        compressed = compress(data)
        decompressed, decoded_metadata = decompress(compressed)
        assert decompressed == data
        assert decoded_metadata == {}

    def test_compress_decompress_complex_metadata(self):
        """Test compress/decompress with complex stream metadata."""
        data = b"audio stream payload"
        metadata = {
            "sample_rate": 48000,
            "channels": 2,
            "format": "float32",
            "window_size": 1024,
            "hop_length": 512,
            "codec": "opus",
            "bitrate": 128000
        }
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert decompressed == data
        assert decoded_metadata == metadata

    def test_compress_decompress_large_payload(self):
        """Test compress/decompress with larger payload."""
        data = b"x" * 50000
        metadata = {"sample_rate": 16000, "window_size": 512}
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert decompressed == data
        assert decoded_metadata["sample_rate"] == 16000

    def test_compress_decompress_binary_data(self):
        """Test compress/decompress with binary payload."""
        data = bytes(range(256))
        metadata = {"format": "raw", "sample_rate": 8000}
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert decompressed == data
        assert decoded_metadata["format"] == "raw"

    def test_compress_decompress_empty_payload(self):
        """Test compress/decompress with empty payload."""
        data = b""
        metadata = {"empty": True}
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert decompressed == data
        assert decoded_metadata["empty"] is True

    def test_compress_invalid_data_type(self):
        """Test compress raises TypeError for non-bytes input."""
        with pytest.raises(TypeError, match="expects a bytes-like object"):
            compress("not bytes")  # type: ignore

    def test_decompress_invalid_data_type(self):
        """Test decompress raises TypeError for non-bytes input."""
        with pytest.raises(TypeError, match="expects a bytes-like object"):
            decompress("not bytes")  # type: ignore

    def test_decompress_truncated_header(self):
        """Test decompress raises ValueError for truncated length header."""
        with pytest.raises(ValueError, match="too short for length header"):
            decompress(b"\x00")

    def test_decompress_truncated_metadata_blob(self):
        """Test decompress raises ValueError for truncated metadata blob."""
        # Header says 100 bytes, but only 5 bytes follow
        payload = b"\x00\x64" + b"short"
        with pytest.raises(ValueError, match="truncated before stream metadata blob"):
            decompress(payload)

    def test_compress_metadata_too_large(self):
        """Test compress raises ValueError for stream metadata too large."""
        # Create enormous metadata to exceed 65535 bytes
        metadata = {f"key_{i}": "value_" + "x" * 1000 for i in range(100)}
        with pytest.raises(ValueError, match="stream metadata too large"):
            compress(b"data", metadata=metadata)

    def test_wire_format_structure(self):
        """Test the wire format structure."""
        data = b"test"
        metadata = {"sample_rate": 44100}
        compressed = compress(data, metadata=metadata)

        # First 2 bytes are length
        metadata_length = (compressed[0] << 8) | compressed[1]
        assert metadata_length > 0

        # Next metadata_length bytes are the metadata blob
        metadata_blob = compressed[2 : 2 + metadata_length]
        import json
        decoded_metadata = json.loads(metadata_blob.decode("utf-8"))
        assert decoded_metadata == metadata


class TestSwSemanticIntegration:
    """Test Sw codec integration with semantic.py."""

    def test_semantic_compress_sw_codec(self):
        """Test semantic_compress with Sw codec."""
        data = b"audio stream"
        compressed = semantic_compress(data, codec="Sw")
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_compress_sw_roundtrip(self):
        """Test full roundtrip through semantic layer."""
        data = b"A" * 1000
        compressed = semantic_compress(data, codec="Sw")
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_compress_sw_with_domain_template(self):
        """Test Sw codec with domain_id and template_id."""
        data = b"routed stream"
        compressed = semantic_compress(
            data, codec="Sw", domain_id=15, template_id=4000
        )
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_decompress_discards_metadata(self):
        """Test that semantic_decompress returns only data, not metadata.

        Note: The semantic layer doesn't expose stream metadata in the simple
        API. To access metadata, use semantic_stream.decompress() directly.
        """
        data = b"stream message"
        # Compress directly with Sw codec including metadata
        from arua.compression.semantic_stream import compress as sw_compress

        metadata = {"sample_rate": 48000, "channels": 2}
        sw_payload = sw_compress(data, metadata=metadata)

        # Wrap in semantic header
        from arua.compression.semantic import CODEC_ID_SW, SemanticHeader

        header = SemanticHeader(codec_id=CODEC_ID_SW, domain_id=0, template_id=0)
        semantic_payload = header.to_bytes() + sw_payload

        # Decompress via semantic API (metadata is discarded)
        decompressed = semantic_decompress(semantic_payload)
        assert decompressed == data


class TestSwEdgeCases:
    """Test edge cases for Sw codec."""

    def test_metadata_with_numeric_values(self):
        """Test metadata with numeric values."""
        metadata = {"sample_rate": 44100, "bitrate": 192.5, "enabled": True}
        data = b"numeric metadata"
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert decoded_metadata["sample_rate"] == 44100
        assert decoded_metadata["bitrate"] == 192.5
        assert decoded_metadata["enabled"] is True

    def test_metadata_with_null_values(self):
        """Test metadata with null values."""
        metadata = {"codec": None, "format": "raw"}
        data = b"null metadata"
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert decoded_metadata["codec"] is None
        assert decoded_metadata["format"] == "raw"

    def test_metadata_with_unicode(self):
        """Test metadata with unicode characters."""
        metadata = {"format": "données", "qualité": "haute"}
        data = b"unicode metadata"
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert decoded_metadata["format"] == "données"
        assert decoded_metadata["qualité"] == "haute"

    def test_many_metadata_fields(self):
        """Test metadata with many fields."""
        metadata = {f"field_{i}": f"value_{i}" for i in range(100)}
        data = b"many fields"
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert len(decoded_metadata) == 100

    def test_realistic_audio_stream_scenario(self):
        """Test realistic audio stream scenario."""
        data = b"\x00" * 4096  # Audio samples
        metadata = {
            "sample_rate": 48000,
            "channels": 2,
            "bit_depth": 16,
            "format": "pcm_s16le",
            "window_size": 1024,
            "hop_length": 512,
            "codec": "aac",
            "bitrate": 256000,
            "duration_ms": 100,
            "metadata": {
                "artist": "Test Artist",
                "title": "Test Track"
            }
        }
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert decompressed == data
        assert decoded_metadata["sample_rate"] == 48000
        assert decoded_metadata["channels"] == 2
        assert decoded_metadata["metadata"]["artist"] == "Test Artist"

    def test_video_stream_metadata(self):
        """Test video stream with metadata."""
        data = b"video frame data"
        metadata = {
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "codec": "h264",
            "bitrate": 5000000,
            "format": "yuv420p",
            "color_space": "bt709",
            "frame_index": 42
        }
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert decoded_metadata["width"] == 1920
        assert decoded_metadata["fps"] == 30

    def test_sensor_stream_metadata(self):
        """Test sensor stream with metadata."""
        data = b"sensor readings"
        metadata = {
            "sensor_type": "accelerometer",
            "sample_rate": 100,
            "units": "m/s^2",
            "axes": ["x", "y", "z"],
            "calibration": {"offset": [0.01, -0.02, 0.03], "scale": [1.0, 1.0, 1.0]},
            "timestamp_ms": 1705315800000
        }
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert decoded_metadata["sensor_type"] == "accelerometer"
        assert decoded_metadata["units"] == "m/s^2"
        assert decoded_metadata["calibration"]["offset"] == [0.01, -0.02, 0.03]

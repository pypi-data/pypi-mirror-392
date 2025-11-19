"""Tests for Semantic Vector (Sv) codec."""

from __future__ import annotations

import pytest

from arua.compression.semantic import semantic_compress, semantic_decompress
from arua.compression.semantic_vector import compress, decompress


class TestVectorCompression:
    """Test Sv codec compression and decompression."""

    def test_compress_decompress_simple_metadata(self):
        """Test compress/decompress with simple vector metadata."""
        data = b"vector data"
        metadata = {"dimension": 768, "model": "text-embedding-ada-002"}
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert decompressed == data
        assert decoded_metadata == metadata

    def test_compress_decompress_no_metadata(self):
        """Test compress/decompress with no metadata (empty dict)."""
        data = b"plain vector"
        compressed = compress(data)
        decompressed, decoded_metadata = decompress(compressed)
        assert decompressed == data
        assert decoded_metadata == {}

    def test_compress_decompress_complex_metadata(self):
        """Test compress/decompress with complex vector metadata."""
        data = b"embedding payload"
        metadata = {
            "dimension": 1536,
            "model": "text-embedding-3-large",
            "dtype": "float32",
            "normalized": True,
            "source": {"text": "sample document", "chunk_id": 42},
            "pooling": "mean"
        }
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert decompressed == data
        assert decoded_metadata == metadata

    def test_compress_decompress_large_payload(self):
        """Test compress/decompress with larger payload."""
        data = b"x" * 50000
        metadata = {"dimension": 4096, "dtype": "float16"}
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert decompressed == data
        assert decoded_metadata["dimension"] == 4096

    def test_compress_decompress_binary_data(self):
        """Test compress/decompress with binary payload."""
        data = bytes(range(256))
        metadata = {"format": "raw", "dimension": 256, "dtype": "uint8"}
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert decompressed == data
        assert decoded_metadata["dtype"] == "uint8"

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
        with pytest.raises(ValueError, match="truncated before vector metadata blob"):
            decompress(payload)

    def test_compress_metadata_too_large(self):
        """Test compress raises ValueError for vector metadata too large."""
        # Create enormous metadata to exceed 65535 bytes
        metadata = {f"key_{i}": "value_" + "x" * 1000 for i in range(100)}
        with pytest.raises(ValueError, match="vector metadata too large"):
            compress(b"data", metadata=metadata)

    def test_wire_format_structure(self):
        """Test the wire format structure."""
        data = b"test"
        metadata = {"dimension": 512}
        compressed = compress(data, metadata=metadata)

        # First 2 bytes are length
        metadata_length = (compressed[0] << 8) | compressed[1]
        assert metadata_length > 0

        # Next metadata_length bytes are the metadata blob
        metadata_blob = compressed[2 : 2 + metadata_length]
        import json
        decoded_metadata = json.loads(metadata_blob.decode("utf-8"))
        assert decoded_metadata == metadata


class TestSvSemanticIntegration:
    """Test Sv codec integration with semantic.py."""

    def test_semantic_compress_sv_codec(self):
        """Test semantic_compress with Sv codec."""
        data = b"vector embedding"
        compressed = semantic_compress(data, codec="Sv")
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_compress_sv_roundtrip(self):
        """Test full roundtrip through semantic layer."""
        data = b"A" * 1000
        compressed = semantic_compress(data, codec="Sv")
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_compress_sv_with_domain_template(self):
        """Test Sv codec with domain_id and template_id."""
        data = b"routed vector"
        compressed = semantic_compress(
            data, codec="Sv", domain_id=7, template_id=3000
        )
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_decompress_discards_metadata(self):
        """Test that semantic_decompress returns only data, not metadata.

        Note: The semantic layer doesn't expose vector metadata in the simple
        API. To access metadata, use semantic_vector.decompress() directly.
        """
        data = b"vector message"
        # Compress directly with Sv codec including metadata
        from arua.compression.semantic_vector import compress as sv_compress

        metadata = {"dimension": 768, "model": "bert-base"}
        sv_payload = sv_compress(data, metadata=metadata)

        # Wrap in semantic header
        from arua.compression.semantic import CODEC_ID_SV, SemanticHeader

        header = SemanticHeader(codec_id=CODEC_ID_SV, domain_id=0, template_id=0)
        semantic_payload = header.to_bytes() + sv_payload

        # Decompress via semantic API (metadata is discarded)
        decompressed = semantic_decompress(semantic_payload)
        assert decompressed == data


class TestSvEdgeCases:
    """Test edge cases for Sv codec."""

    def test_metadata_with_numeric_values(self):
        """Test metadata with numeric values."""
        metadata = {"dimension": 1024, "score": 0.95, "normalized": True}
        data = b"numeric metadata"
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert decoded_metadata["dimension"] == 1024
        assert decoded_metadata["score"] == 0.95
        assert decoded_metadata["normalized"] is True

    def test_metadata_with_null_values(self):
        """Test metadata with null values."""
        metadata = {"model": None, "dtype": "float32"}
        data = b"null metadata"
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert decoded_metadata["model"] is None
        assert decoded_metadata["dtype"] == "float32"

    def test_metadata_with_unicode(self):
        """Test metadata with unicode characters."""
        metadata = {"modèle": "français", "métadonnées": "données"}
        data = b"unicode metadata"
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert decoded_metadata["modèle"] == "français"
        assert decoded_metadata["métadonnées"] == "données"

    def test_many_metadata_fields(self):
        """Test metadata with many fields."""
        metadata = {f"field_{i}": f"value_{i}" for i in range(100)}
        data = b"many fields"
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert len(decoded_metadata) == 100

    def test_realistic_embedding_scenario(self):
        """Test realistic vector embedding scenario."""
        data = b"\x00" * 768 * 4  # 768-dim float32 vector
        metadata = {
            "dimension": 768,
            "dtype": "float32",
            "model": "text-embedding-ada-002",
            "normalized": True,
            "source": {
                "document_id": "doc-12345",
                "chunk_index": 3,
                "text": "The quick brown fox jumps over the lazy dog"
            },
            "pooling": "mean",
            "version": "v1"
        }
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert decompressed == data
        assert decoded_metadata["dimension"] == 768
        assert decoded_metadata["model"] == "text-embedding-ada-002"
        assert decoded_metadata["source"]["document_id"] == "doc-12345"

    def test_multimodal_embedding_metadata(self):
        """Test multimodal vector with metadata."""
        data = b"multimodal embedding"
        metadata = {
            "dimension": 512,
            "dtype": "float16",
            "modality": "image+text",
            "image_model": "clip-vit-b-32",
            "text_model": "clip-text-b-32",
            "fusion": "concatenate",
            "image_weight": 0.6,
            "text_weight": 0.4
        }
        compressed = compress(data, metadata=metadata)
        decompressed, decoded_metadata = decompress(compressed)
        assert decoded_metadata["modality"] == "image+text"
        assert decoded_metadata["image_weight"] == 0.6

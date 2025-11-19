"""Tests for Semantic Resolver (Sr) codec."""

from __future__ import annotations

import pytest

from arua.compression.semantic import semantic_compress, semantic_decompress
from arua.compression.semantic_resolver import compress, decompress


class TestResolverCompression:
    """Test Sr codec compression and decompression."""

    def test_compress_decompress_simple_hints(self):
        """Test compress/decompress with simple routing hints."""
        data = b"resolver data"
        hints = {"region": "us-west-2", "priority": "high"}
        compressed = compress(data, hints=hints)
        decompressed, decoded_hints = decompress(compressed)
        assert decompressed == data
        assert decoded_hints == hints

    def test_compress_decompress_no_hints(self):
        """Test compress/decompress with no hints (empty dict)."""
        data = b"plain data"
        compressed = compress(data)
        decompressed, decoded_hints = decompress(compressed)
        assert decompressed == data
        assert decoded_hints == {}

    def test_compress_decompress_complex_hints(self):
        """Test compress/decompress with complex nested hints."""
        data = b"routing payload"
        hints = {
            "targets": ["node-1", "node-2", "node-3"],
            "policy": {"retry": 3, "timeout_ms": 5000},
            "metadata": {"source": "api-gateway", "trace_id": "abc-123"}
        }
        compressed = compress(data, hints=hints)
        decompressed, decoded_hints = decompress(compressed)
        assert decompressed == data
        assert decoded_hints == hints

    def test_compress_decompress_large_payload(self):
        """Test compress/decompress with larger payload."""
        data = b"x" * 50000
        hints = {"destination": "cluster-prod", "shard": 42}
        compressed = compress(data, hints=hints)
        decompressed, decoded_hints = decompress(compressed)
        assert decompressed == data
        assert decoded_hints["destination"] == "cluster-prod"

    def test_compress_decompress_binary_data(self):
        """Test compress/decompress with binary payload."""
        data = bytes(range(256))
        hints = {"encoding": "binary", "version": 1}
        compressed = compress(data, hints=hints)
        decompressed, decoded_hints = decompress(compressed)
        assert decompressed == data
        assert decoded_hints["version"] == 1

    def test_compress_decompress_empty_payload(self):
        """Test compress/decompress with empty payload."""
        data = b""
        hints = {"empty": True}
        compressed = compress(data, hints=hints)
        decompressed, decoded_hints = decompress(compressed)
        assert decompressed == data
        assert decoded_hints["empty"] is True

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

    def test_decompress_truncated_resolver_blob(self):
        """Test decompress raises ValueError for truncated resolver blob."""
        # Header says 100 bytes, but only 5 bytes follow
        payload = b"\x00\x64" + b"short"
        with pytest.raises(ValueError, match="truncated before resolver blob"):
            decompress(payload)

    def test_compress_hints_too_large(self):
        """Test compress raises ValueError for resolver metadata too large."""
        # Create enormous hints to exceed 65535 bytes
        hints = {f"key_{i}": "value_" + "x" * 1000 for i in range(100)}
        with pytest.raises(ValueError, match="resolver metadata too large"):
            compress(b"data", hints=hints)

    def test_wire_format_structure(self):
        """Test the wire format structure."""
        data = b"test"
        hints = {"field": "value"}
        compressed = compress(data, hints=hints)

        # First 2 bytes are length
        hints_length = (compressed[0] << 8) | compressed[1]
        assert hints_length > 0

        # Next hints_length bytes are the hints blob
        hints_blob = compressed[2 : 2 + hints_length]
        import json
        decoded_hints = json.loads(hints_blob.decode("utf-8"))
        assert decoded_hints == hints


class TestSrSemanticIntegration:
    """Test Sr codec integration with semantic.py."""

    def test_semantic_compress_sr_codec(self):
        """Test semantic_compress with Sr codec."""
        data = b"routing message"
        compressed = semantic_compress(data, codec="Sr")
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_compress_sr_roundtrip(self):
        """Test full roundtrip through semantic layer."""
        data = b"A" * 1000
        compressed = semantic_compress(data, codec="Sr")
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_compress_sr_with_domain_template(self):
        """Test Sr codec with domain_id and template_id."""
        data = b"routed resolver"
        compressed = semantic_compress(
            data, codec="Sr", domain_id=10, template_id=2000
        )
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_decompress_discards_hints(self):
        """Test that semantic_decompress returns only data, not hints.

        Note: The semantic layer doesn't expose hints metadata in the simple
        API. To access hints info, use semantic_resolver.decompress() directly.
        """
        data = b"resolver message"
        # Compress directly with Sr codec including hints
        from arua.compression.semantic_resolver import compress as sr_compress

        hints = {"region": "eu-west-1", "tier": "premium"}
        sr_payload = sr_compress(data, hints=hints)

        # Wrap in semantic header
        from arua.compression.semantic import CODEC_ID_SR, SemanticHeader

        header = SemanticHeader(codec_id=CODEC_ID_SR, domain_id=0, template_id=0)
        semantic_payload = header.to_bytes() + sr_payload

        # Decompress via semantic API (hints are discarded)
        decompressed = semantic_decompress(semantic_payload)
        assert decompressed == data


class TestSrEdgeCases:
    """Test edge cases for Sr codec."""

    def test_hints_with_numeric_values(self):
        """Test hints with numeric values."""
        hints = {"priority": 10, "weight": 3.14, "enabled": True}
        data = b"numeric hints"
        compressed = compress(data, hints=hints)
        decompressed, decoded_hints = decompress(compressed)
        assert decoded_hints["priority"] == 10
        assert decoded_hints["weight"] == 3.14
        assert decoded_hints["enabled"] is True

    def test_hints_with_null_values(self):
        """Test hints with null values."""
        hints = {"target": None, "fallback": "default"}
        data = b"null hints"
        compressed = compress(data, hints=hints)
        decompressed, decoded_hints = decompress(compressed)
        assert decoded_hints["target"] is None
        assert decoded_hints["fallback"] == "default"

    def test_hints_with_unicode(self):
        """Test hints with unicode characters."""
        hints = {"région": "europe", "métadonnées": "données"}
        data = b"unicode hints"
        compressed = compress(data, hints=hints)
        decompressed, decoded_hints = decompress(compressed)
        assert decoded_hints["région"] == "europe"
        assert decoded_hints["métadonnées"] == "données"

    def test_many_hints(self):
        """Test hints with many keys."""
        hints = {f"hint_{i}": f"value_{i}" for i in range(100)}
        data = b"many hints"
        compressed = compress(data, hints=hints)
        decompressed, decoded_hints = decompress(compressed)
        assert len(decoded_hints) == 100

    def test_realistic_routing_scenario(self):
        """Test realistic routing hints scenario."""
        data = b"application request payload"
        hints = {
            "source": {"service": "api-gateway", "instance": "api-01", "zone": "us-east-1a"},
            "destination": {"service": "data-service", "shard_key": "user:12345"},
            "routing": {
                "strategy": "consistent-hash",
                "replicas": 3,
                "min_acks": 2
            },
            "metadata": {
                "request_id": "req-abc-123",
                "trace_id": "trace-xyz-789",
                "priority": "normal",
                "deadline_ms": 5000
            }
        }
        compressed = compress(data, hints=hints)
        decompressed, decoded_hints = decompress(compressed)
        assert decompressed == data
        assert decoded_hints["source"]["service"] == "api-gateway"
        assert decoded_hints["routing"]["strategy"] == "consistent-hash"
        assert decoded_hints["metadata"]["request_id"] == "req-abc-123"

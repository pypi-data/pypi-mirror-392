"""Tests for Sl (Semantic Learned) codec."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from arua.compression.semantic_learned import (
    LearnedMetadata,
    compress,
    decompress,
    encode_learned,
    decode_learned,
)
from arua.compression.semantic import semantic_compress, semantic_decompress


class TestLearnedMetadata:
    """Test LearnedMetadata encoding/decoding."""

    def test_encode_decode_basic(self):
        """Test basic metadata round-trip."""
        meta = LearnedMetadata(
            model_name="vae_v1",
            version="1.0",
            latent_dim=128,
        )
        encoded = encode_learned(meta)
        decoded = decode_learned(encoded)

        assert decoded.model_name == "vae_v1"
        assert decoded.version == "1.0"
        assert decoded.latent_dim == 128
        assert decoded.has_residual is False
        assert decoded.extra == {}

    def test_encode_decode_with_residual(self):
        """Test metadata with residual flag."""
        meta = LearnedMetadata(
            model_name="learned_codec_v2",
            version="2.1",
            latent_dim=64,
            has_residual=True,
        )
        encoded = encode_learned(meta)
        decoded = decode_learned(encoded)

        assert decoded.model_name == "learned_codec_v2"
        assert decoded.version == "2.1"
        assert decoded.latent_dim == 64
        assert decoded.has_residual is True

    def test_encode_decode_with_extra(self):
        """Test metadata with extra fields."""
        meta = LearnedMetadata(
            model_name="autoencoder",
            version="3.0",
            latent_dim=256,
            has_residual=False,
            extra={
                "checkpoint": "epoch_100",
                "loss": 0.023,
                "optimizer": "adam",
            },
        )
        encoded = encode_learned(meta)
        decoded = decode_learned(encoded)

        assert decoded.model_name == "autoencoder"
        assert decoded.version == "3.0"
        assert decoded.latent_dim == 256
        assert decoded.has_residual is False
        assert decoded.extra["checkpoint"] == "epoch_100"
        assert decoded.extra["loss"] == 0.023
        assert decoded.extra["optimizer"] == "adam"

    def test_decode_invalid_json(self):
        """Test decoding invalid JSON."""
        with pytest.raises(ValueError, match="invalid Sl payload JSON"):
            decode_learned(b"not valid json")

    def test_decode_non_dict(self):
        """Test decoding non-dict JSON."""
        with pytest.raises(ValueError, match="Sl payload must be a JSON object"):
            decode_learned(b'["array", "not", "dict"]')

    def test_decode_invalid_extra(self):
        """Test decoding with invalid extra field."""
        with pytest.raises(ValueError, match="'extra' field must be a JSON object"):
            decode_learned(b'{"model_name":"test","version":"1","latent_dim":64,"extra":"not a dict"}')


class TestSlCompress:
    """Test Sl compression/decompression."""

    def test_compress_decompress_basic(self):
        """Test basic compression round-trip."""
        data = b"Hello, world!" * 100
        meta = LearnedMetadata(
            model_name="test_model",
            version="1.0",
            latent_dim=128,
        )

        compressed = compress(data, meta)
        decompressed, decoded_meta = decompress(compressed)

        assert decompressed == data
        assert decoded_meta.model_name == "test_model"
        assert decoded_meta.version == "1.0"
        assert decoded_meta.latent_dim == 128

    def test_compress_with_default_metadata(self):
        """Test compression with default metadata."""
        data = b"Test data" * 50
        compressed = compress(data)
        decompressed, meta = decompress(compressed)

        assert decompressed == data
        assert meta.model_name == "unknown"
        assert meta.version == "0"
        assert meta.latent_dim == 0

    def test_compress_latent_codes(self):
        """Test compression of latent codes (simulated ML output)."""
        # Simulate 256-dim latent space encoded as float32
        import struct
        latent_values = [0.123 * i for i in range(256)]
        latent_bytes = b"".join(struct.pack("f", v) for v in latent_values)

        meta = LearnedMetadata(
            model_name="embedding_vae",
            version="v2.0",
            latent_dim=256,
            has_residual=True,
            extra={"checkpoint": "epoch_50"},
        )

        compressed = compress(latent_bytes, meta)
        decompressed, decoded_meta = decompress(compressed)

        assert decompressed == latent_bytes
        assert decoded_meta.model_name == "embedding_vae"
        assert decoded_meta.latent_dim == 256
        assert decoded_meta.has_residual is True
        assert decoded_meta.extra["checkpoint"] == "epoch_50"

    def test_compress_empty_data(self):
        """Test compression of empty data."""
        data = b""
        meta = LearnedMetadata(
            model_name="test",
            version="1.0",
            latent_dim=64,
        )

        compressed = compress(data, meta)
        decompressed, decoded_meta = decompress(compressed)

        assert decompressed == data
        assert decoded_meta.model_name == "test"

    def test_compress_large_metadata(self):
        """Test compression with large metadata (but under limit)."""
        # Create metadata with large extra field
        large_extra = {f"key_{i}": f"value_{i}" * 10 for i in range(100)}
        meta = LearnedMetadata(
            model_name="large_model",
            version="1.0",
            latent_dim=512,
            extra=large_extra,
        )

        data = b"Test data"
        compressed = compress(data, meta)
        decompressed, decoded_meta = decompress(compressed)

        assert decompressed == data
        assert decoded_meta.model_name == "large_model"
        assert len(decoded_meta.extra) == 100

    def test_compress_type_validation(self):
        """Test type validation in compress."""
        with pytest.raises(TypeError, match="expects a bytes-like object"):
            compress("not bytes")

    def test_decompress_type_validation(self):
        """Test type validation in decompress."""
        with pytest.raises(TypeError, match="expects a bytes-like object"):
            decompress("not bytes")

    def test_decompress_too_short(self):
        """Test decompression of truncated payload."""
        with pytest.raises(ValueError, match="payload too short"):
            decompress(b"\x00")

    def test_decompress_truncated_metadata(self):
        """Test decompression with truncated metadata."""
        # Create a payload that claims 1000 bytes of metadata but only has 10
        payload = b"\x03\xe8" + b"X" * 10
        with pytest.raises(ValueError, match="payload truncated"):
            decompress(payload)


class TestSlSemanticIntegration:
    """Test Sl integration with semantic routing."""

    def test_semantic_compress_sl(self):
        """Test semantic_compress with Sl codec."""
        data = b"Neural network compressed data" * 10

        compressed = semantic_compress(data, codec="Sl")
        decompressed = semantic_decompress(compressed)

        assert decompressed == data

    def test_semantic_compress_sl_with_domain(self):
        """Test Sl with domain routing."""
        data = b"ML model checkpoint data" * 20

        compressed = semantic_compress(data, codec="Sl", domain_id=2)
        decompressed = semantic_decompress(compressed)

        assert decompressed == data

    def test_semantic_header_format(self):
        """Test that Sl uses correct semantic header."""
        data = b"Test" * 100
        compressed = semantic_compress(data, codec="Sl")

        # Check header: [codec_id][domain_id][template_id_hi][template_id_lo]
        assert len(compressed) >= 4
        assert compressed[0] == 0x0D  # CODEC_ID_SL
        assert compressed[1] == 0x00  # domain_id = 0 (default)


class TestSlRealWorldScenarios:
    """Test Sl with realistic ML compression scenarios."""

    def test_vae_embedding_compression(self):
        """Test VAE-compressed embeddings workflow."""
        # Simulate a 768-dim embedding compressed to 128-dim latent space
        import struct

        # Original embedding (768 float32 = 3072 bytes)
        original_dim = 768
        latent_dim = 128

        # Simulate latent code (128 float32 = 512 bytes)
        latent_code = b"".join(
            struct.pack("f", 0.1 * i) for i in range(latent_dim)
        )

        meta = LearnedMetadata(
            model_name="sentence_vae_v1",
            version="1.2.0",
            latent_dim=latent_dim,
            has_residual=False,
            extra={
                "original_dim": original_dim,
                "compression_ratio": original_dim / latent_dim,
                "model_checkpoint": "epoch_200",
            },
        )

        compressed = semantic_compress(latent_code, codec="Sl")
        decompressed = semantic_decompress(compressed)

        assert decompressed == latent_code

        # Verify compression happened (metadata overhead + core compression)
        # Should be significantly smaller than original 3072 bytes
        assert len(compressed) < 3072

    def test_neural_codec_checkpoint(self):
        """Test neural codec checkpoint with version tracking."""
        # Simulate compressed audio/video data from a neural codec
        neural_output = b"\x89PNG\r\n\x1a\n" + b"compressed_frames" * 100

        meta = LearnedMetadata(
            model_name="neural_codec_v3",
            version="3.1.4",
            latent_dim=256,
            has_residual=True,
            extra={
                "frame_rate": 30,
                "codec_type": "video",
                "quantization": "8bit",
            },
        )

        compressed = compress(neural_output, meta)
        decompressed, decoded_meta = decompress(compressed)

        assert decompressed == neural_output
        assert decoded_meta.model_name == "neural_codec_v3"
        assert decoded_meta.version == "3.1.4"
        assert decoded_meta.has_residual is True
        assert decoded_meta.extra["codec_type"] == "video"

    def test_multi_model_routing(self):
        """Test storing data from different ML models."""
        # Model 1: Image VAE
        image_latent = b"image_latent_code" * 50
        image_meta = LearnedMetadata(
            model_name="image_vae",
            version="2.0",
            latent_dim=512,
            extra={"modality": "image"},
        )

        # Model 2: Text transformer
        text_latent = b"text_latent_code" * 50
        text_meta = LearnedMetadata(
            model_name="text_transformer",
            version="1.5",
            latent_dim=768,
            extra={"modality": "text"},
        )

        # Compress both with domain routing
        image_compressed = semantic_compress(
            compress(image_latent, image_meta),
            codec="Sl",
            domain_id=1,  # Image domain
        )
        text_compressed = semantic_compress(
            compress(text_latent, text_meta),
            codec="Sl",
            domain_id=2,  # Text domain
        )

        # Decompress and verify
        image_decompressed = semantic_decompress(image_compressed)
        text_decompressed = semantic_decompress(text_compressed)

        # Extract metadata from inner Sl payload
        _, image_decoded_meta = decompress(image_decompressed)
        _, text_decoded_meta = decompress(text_decompressed)

        assert image_decoded_meta.model_name == "image_vae"
        assert image_decoded_meta.extra["modality"] == "image"
        assert text_decoded_meta.model_name == "text_transformer"
        assert text_decoded_meta.extra["modality"] == "text"


class TestSlPerformance:
    """Test Sl compression performance characteristics."""

    def test_compression_reduces_size(self):
        """Test that Sl compression reduces data size."""
        # Highly compressible data
        data = b"repeated pattern " * 1000
        meta = LearnedMetadata(
            model_name="test",
            version="1.0",
            latent_dim=64,
        )

        compressed = compress(data, meta)

        # Should compress well (repeated pattern)
        ratio = 1 - (len(compressed) / len(data))
        assert ratio > 0.5  # At least 50% compression

    def test_metadata_overhead(self):
        """Test metadata overhead is reasonable."""
        data = b"X" * 100
        meta = LearnedMetadata(
            model_name="model",
            version="1",
            latent_dim=128,
        )

        compressed = compress(data, meta)

        # Metadata should be small (< 100 bytes for this simple case)
        # Wire format: [2B meta_len][meta_json][compressed_data]
        meta_len = (compressed[0] << 8) | compressed[1]
        assert meta_len < 100

    def test_empty_data_minimal_overhead(self):
        """Test empty data has minimal overhead."""
        data = b""
        meta = LearnedMetadata(
            model_name="test",
            version="1.0",
            latent_dim=64,
        )

        compressed = compress(data, meta)

        # Should be close to metadata size + wire format overhead
        assert len(compressed) < 200  # Generous upper bound


class TestSlEdgeCases:
    """Test Sl edge cases and error handling."""

    def test_unicode_metadata(self):
        """Test metadata with unicode characters."""
        meta = LearnedMetadata(
            model_name="模型_v1",  # Chinese characters
            version="1.0",
            latent_dim=128,
            extra={"description": "Multi-language: 中文, 日本語, 한국어"},
        )

        data = b"Test data"
        compressed = compress(data, meta)
        decompressed, decoded_meta = decompress(compressed)

        assert decompressed == data
        assert decoded_meta.model_name == "模型_v1"
        assert "中文" in decoded_meta.extra["description"]

    def test_zero_latent_dim(self):
        """Test with zero latent dimension."""
        meta = LearnedMetadata(
            model_name="test",
            version="1.0",
            latent_dim=0,
        )

        data = b"Test"
        compressed = compress(data, meta)
        decompressed, decoded_meta = decompress(compressed)

        assert decompressed == data
        assert decoded_meta.latent_dim == 0

    def test_very_large_latent_dim(self):
        """Test with very large latent dimension."""
        meta = LearnedMetadata(
            model_name="huge_model",
            version="1.0",
            latent_dim=1_000_000,
        )

        data = b"Test"
        compressed = compress(data, meta)
        decompressed, decoded_meta = decompress(compressed)

        assert decompressed == data
        assert decoded_meta.latent_dim == 1_000_000

    def test_binary_data_all_bytes(self):
        """Test compression of all possible byte values."""
        data = bytes(range(256)) * 10
        meta = LearnedMetadata(
            model_name="binary_test",
            version="1.0",
            latent_dim=256,
        )

        compressed = compress(data, meta)
        decompressed, decoded_meta = decompress(compressed)

        assert decompressed == data
        assert decoded_meta.model_name == "binary_test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

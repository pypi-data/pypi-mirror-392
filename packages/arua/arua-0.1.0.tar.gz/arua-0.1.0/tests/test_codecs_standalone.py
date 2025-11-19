#!/usr/bin/env python3
"""Standalone test for AI data types - imports modules directly."""

import json
import struct
import sys
from pathlib import Path

# Direct imports
sys.path.insert(0, str(Path(__file__).parent / "src" / "arua" / "compression"))

import core
import semantic_resolver
import semantic_vector
import semantic_stream
import semantic_table


def test_vector_embeddings():
    """Test realistic text embedding vectors (Sv codec)."""
    print("\n=== Testing Vector Embeddings (Sv) ===")

    # Simulate a 768-dim text embedding (BERT-like)
    embedding_dim = 768
    embedding_data = struct.pack(f"{embedding_dim}f", *[0.1 * i % 1.0 for i in range(embedding_dim)])

    metadata = {
        "dimension": embedding_dim,
        "model": "text-embedding-ada-002",
        "dtype": "float32",
        "normalized": True,
        "source": {
            "document_id": "doc-12345",
            "chunk_index": 5,
            "text": "Machine learning models process data through neural networks"
        },
        "pooling": "mean",
        "timestamp": 1705315800000
    }

    # Compress
    compressed = semantic_vector.compress(embedding_data, metadata=metadata)
    print(f"Original size: {len(embedding_data)} bytes")
    print(f"Compressed size: {len(compressed)} bytes")
    print(f"Compression ratio: {len(embedding_data) / len(compressed):.2f}x")

    # Decompress
    decompressed_data, decoded_metadata = semantic_vector.decompress(compressed)

    # Verify
    assert decompressed_data == embedding_data, "Vector data mismatch!"
    assert decoded_metadata == metadata, "Vector metadata mismatch!"
    assert decoded_metadata["dimension"] == 768
    assert decoded_metadata["source"]["document_id"] == "doc-12345"

    print("✓ Vector embedding roundtrip successful")
    print(f"✓ Metadata preserved: dimension={decoded_metadata['dimension']}, model={decoded_metadata['model']}")
    return True


def test_audio_stream():
    """Test audio stream data (Sw codec)."""
    print("\n=== Testing Audio Stream (Sw) ===")

    # Simulate 0.1 seconds of 16kHz mono audio (PCM)
    sample_rate = 16000
    duration_seconds = 0.1
    num_samples = int(sample_rate * duration_seconds)

    # Generate sine wave at 440Hz (A note)
    import math
    frequency = 440.0
    audio_samples = [
        int(32767 * 0.5 * math.sin(2 * math.pi * frequency * i / sample_rate))
        for i in range(num_samples)
    ]
    audio_data = struct.pack(f"{num_samples}h", *audio_samples)

    metadata = {
        "sample_rate": sample_rate,
        "channels": 1,
        "bit_depth": 16,
        "format": "pcm_s16le",
        "duration_ms": int(duration_seconds * 1000),
        "codec": "raw",
    }

    compressed = semantic_stream.compress(audio_data, metadata=metadata)
    print(f"Original size: {len(audio_data)} bytes")
    print(f"Compressed size: {len(compressed)} bytes")
    print(f"Compression ratio: {len(audio_data) / len(compressed):.2f}x")

    decompressed_data, decoded_metadata = semantic_stream.decompress(compressed)

    assert decompressed_data == audio_data
    assert decoded_metadata["sample_rate"] == sample_rate

    print("✓ Audio stream roundtrip successful")
    print(f"✓ Format: {decoded_metadata['format']}, {decoded_metadata['sample_rate']}Hz")
    return True


def test_training_data_table():
    """Test ML training data table (St codec)."""
    print("\n=== Testing Training Data Table (St) ===")

    # Simulate a dataset of training examples
    rows = [
        {
            "example_id": 1,
            "input_text": "The weather is sunny today",
            "label": "positive",
            "confidence": 0.95,
        },
        {
            "example_id": 2,
            "input_text": "I am feeling sad",
            "label": "negative",
            "confidence": 0.87,
        },
    ]

    # Encode table
    encoded = semantic_table.encode_table(rows, domain_id=10, template_id=100)
    print(f"Table size: {len(rows)} rows")
    print(f"Encoded size: {len(encoded)} bytes")

    # Decode table
    decoded_rows, schema, header, plan = semantic_table.decode_table(encoded)

    # Verify
    assert len(decoded_rows) == len(rows)
    assert decoded_rows[0]["input_text"] == "The weather is sunny today"
    assert decoded_rows[1]["label"] == "negative"

    print("✓ Training data table roundtrip successful")
    print(f"✓ Schema: {len(schema.columns)} columns")
    for col in schema.columns:
        print(f"  - {col.name}: {col.type}")
    return True


def test_routing_hints():
    """Test model routing/inference hints (Sr codec)."""
    print("\n=== Testing Routing Hints (Sr) ===")

    # Simulate inference request with routing hints
    request_data = json.dumps({
        "prompt": "Translate the following text to French: Hello",
        "max_tokens": 100,
        "temperature": 0.7
    }).encode("utf-8")

    hints = {
        "model": {
            "name": "gpt-4",
            "version": "2024-01",
            "deployment": "production"
        },
        "routing": {
            "region": "us-west-2",
            "tier": "premium",
            "priority": "high",
        },
        "resources": {
            "min_gpus": 1,
            "preferred_gpu": "A100",
        }
    }

    compressed = semantic_resolver.compress(request_data, hints=hints)
    print(f"Request size: {len(request_data)} bytes")
    print(f"Compressed size: {len(compressed)} bytes")

    decompressed_data, decoded_hints = semantic_resolver.decompress(compressed)

    assert decompressed_data == request_data
    assert decoded_hints["model"]["name"] == "gpt-4"
    assert decoded_hints["routing"]["region"] == "us-west-2"
    assert decoded_hints["resources"]["preferred_gpu"] == "A100"

    print("✓ Routing hints roundtrip successful")
    print(f"✓ Model: {decoded_hints['model']['name']}, Region: {decoded_hints['routing']['region']}")
    return True


def main():
    """Run all AI data roundtrip tests."""
    print("=" * 60)
    print("Testing AI Data Types Through Semantic Codecs")
    print("=" * 60)

    tests = [
        ("Vector Embeddings", test_vector_embeddings),
        ("Audio Stream", test_audio_stream),
        ("Training Data Table", test_training_data_table),
        ("Routing Hints", test_routing_hints),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            failed += 1
            print(f"✗ {name} FAILED: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 60)

    if failed == 0:
        print("\n🎉 All AI data types compress/decompress cleanly!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Quick test of Ss (Semantic Cache) codec."""

import sys
sys.path.insert(0, 'src')

# Bypass FastAPI import issue
import arua.compression.core as core_mod
import arua.compression.semantic_cache as cache_mod

def test_cache():
    """Test cache codec."""
    print("Testing Ss (Semantic Cache) codec...")
    print("=" * 60)

    # Test 1: Repetitive data
    print("\n1. Repetitive data (good candidate for caching):")
    data = b"hello world " * 100
    compressed = cache_mod.compress(data)
    decompressed, metadata = cache_mod.decompress(compressed)

    assert decompressed == data, "Roundtrip failed!"
    compression_ratio = (1 - len(compressed) / len(data)) * 100

    print(f"   Original: {len(data)} bytes")
    print(f"   Compressed: {len(compressed)} bytes")
    print(f"   Ratio: {compression_ratio:.1f}% compression")
    print(f"   Dictionary size: {metadata.dict_size} entries")
    print("   ✓ PASS")

    # Test 2: LLM-style prompt
    print("\n2. LLM prompt with repeated system message:")
    system = b"You are a helpful assistant. "
    prompt = system + b"User: Hello " + system + b"User: Hi " + system
    compressed = cache_mod.compress(prompt)
    decompressed, metadata = cache_mod.decompress(compressed)

    assert decompressed == prompt, "Roundtrip failed!"
    compression_ratio = (1 - len(compressed) / len(prompt)) * 100

    print(f"   Original: {len(prompt)} bytes")
    print(f"   Compressed: {len(compressed)} bytes")
    print(f"   Ratio: {compression_ratio:.1f}% compression")
    print(f"   Dictionary size: {metadata.dict_size} entries")
    print("   ✓ PASS")

    # Test 3: Random data (poor candidate)
    print("\n3. Random data (poor compression candidate):")
    data = bytes(range(256))
    compressed = cache_mod.compress(data)
    decompressed, metadata = cache_mod.decompress(compressed)

    assert decompressed == data, "Roundtrip failed!"

    print(f"   Original: {len(data)} bytes")
    print(f"   Compressed: {len(compressed)} bytes")
    print(f"   Dictionary size: {metadata.dict_size} entries")
    print("   ✓ PASS (handles non-compressible data)")

    # Test 4: Function calling patterns
    print("\n4. Function calling patterns (JSON-like):")
    data = b'{"fn":"calc","args":[1,2]} ' * 30
    compressed = cache_mod.compress(data)
    decompressed, metadata = cache_mod.decompress(compressed)

    assert decompressed == data, "Roundtrip failed!"
    compression_ratio = (1 - len(compressed) / len(data)) * 100

    print(f"   Original: {len(data)} bytes")
    print(f"   Compressed: {len(compressed)} bytes")
    print(f"   Ratio: {compression_ratio:.1f}% compression")
    print(f"   Dictionary size: {metadata.dict_size} entries")
    print("   ✓ PASS")

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED - Ss (Semantic Cache) codec working!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        test_cache()
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

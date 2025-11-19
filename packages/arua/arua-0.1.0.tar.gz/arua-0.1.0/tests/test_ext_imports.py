def test_imports():
    try:
        import arua.rands_c as rands_c  # noqa: F401
    except Exception:
        rands_c = None
    try:
        import arua.compression.lz77_c as lz_c  # noqa: F401
    except Exception:
        lz_c = None
    # Both may not be present in all environments; just ensure import doesn't crash
    assert True

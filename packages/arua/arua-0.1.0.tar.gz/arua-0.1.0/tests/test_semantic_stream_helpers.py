from arua.compression.semantic_stream import encode_wave, decode_wave


def test_wave_roundtrip_simple() -> None:
    samples = [i / 10.0 for i in range(-5, 6)]
    payload = encode_wave(samples)
    decoded = decode_wave(payload)
    assert len(decoded) == len(samples)
    for a, b in zip(samples, decoded):
        assert abs(a - b) <= 1e-3


def test_wave_empty() -> None:
    samples: list[float] = []
    payload = encode_wave(samples)
    decoded = decode_wave(payload)
    assert decoded == samples


import pytest

from arua.rands import RNG


def test_rng_repeatability():
    r1 = RNG(12345)
    r2 = RNG(12345)
    out1 = [r1.rand64() for _ in range(10)]
    out2 = [r2.rand64() for _ in range(10)]
    assert out1 == out2


def test_randbytes_length_and_seed():
    r = RNG(42)
    b1 = r.randbytes(10)
    r.seed(42)
    b2 = r.randbytes(10)
    assert b1 == b2
    assert len(b1) == 10


def test_rand32_range():
    r = RNG(9001)
    val = r.rand32()
    assert 0 <= val <= (1 << 32) - 1

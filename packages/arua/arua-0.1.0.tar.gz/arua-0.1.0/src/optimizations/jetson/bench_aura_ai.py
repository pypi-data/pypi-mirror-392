"""Benchmark AURA ProductionHybridCompressor on simulated AI-like data."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Iterable


def _ensure_aura_on_path() -> None:
    aura_src = Path("/Users/hendrixx./AURA/src")
    if str(aura_src) not in sys.path:
        sys.path.insert(0, str(aura_src))


def _gen_chat_like(size: int) -> bytes:
    base = (
        "User: Please explain how this works.\n"
        "Assistant: Sure, I will walk through the main steps and "
        "provide examples where useful.\n"
    )
    text = (base * (size // len(base) + 1))[:size]
    return text.encode("utf-8")


def _gen_code_like(size: int) -> bytes:
    base = (
        "def foo(x):\n"
        "    if x % 2 == 0:\n"
        "        return x * 2\n"
        "    return x + 1\n\n"
    )
    text = (base * (size // len(base) + 1))[:size]
    return text.encode("utf-8")


def _gen_log_like(size: int) -> bytes:
    base = (
        "2025-01-01T12:00:00Z INFO service=api path=/chat status=200 latency_ms=45\n"
        "2025-01-01T12:00:01Z INFO service=api path=/chat status=200 latency_ms=47\n"
    )
    text = (base * (size // len(base) + 1))[:size]
    return text.encode("utf-8")


def _bench_one(label: str, sizes: Iterable[int], runs: int = 100) -> None:
    _ensure_aura_on_path()
    from aura_compression import ProductionHybridCompressor, TemplateLibrary

    compressor = ProductionHybridCompressor(template_cache_dir=".aura_cache")

    print(f"== AURA {label} ==")
    for size in sizes:
        if label == "chat":
            data = _gen_chat_like(size)
        elif label == "code":
            data = _gen_code_like(size)
        else:
            data = _gen_log_like(size)

        # Warm-up
        payload, method, meta = compressor.compress(
            data.decode("utf-8", errors="ignore")
        )
        text_out, meta2 = compressor.decompress(payload, return_metadata=True)
        assert text_out == data.decode("utf-8", errors="ignore")

        t0 = time.perf_counter()
        for _ in range(runs):
            payload, method, meta = compressor.compress(
                data.decode("utf-8", errors="ignore")
            )
        t1 = time.perf_counter()

        t2 = time.perf_counter()
        for _ in range(runs):
            _ = compressor.decompress(payload)
        t3 = time.perf_counter()

        original_size = len(data)
        compressed_size = len(payload)
        ratio = original_size / compressed_size if compressed_size else 1.0
        print(
            f"size={size:6d}B  ratio={ratio:5.2f}  "
            f"compress={((t1 - t0)/runs)*1e3:7.3f} ms  "
            f"decompress={((t3 - t2)/runs)*1e3:7.3f} ms  "
            f"method={method.name.lower()}"
        )
    print()


if __name__ == "__main__":
    sizes = (1024, 4096, 16384)
    _bench_one("chat", sizes)
    _bench_one("code", sizes)
    _bench_one("log", sizes)

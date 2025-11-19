"""Quick benchmark for ARUA core compressor on simulated AI-like data."""

from __future__ import annotations

import time
from typing import Iterable, Tuple

from arua.compression.core import compress, decompress


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


def _bench_one(label: str, sizes: Iterable[int], runs: int = 200) -> None:
    print(f"== {label} ==")
    for size in sizes:
        if label == "chat":
            data = _gen_chat_like(size)
        elif label == "code":
            data = _gen_code_like(size)
        else:
            data = _gen_log_like(size)

        # Warm-up
        comp_payload = compress(data, method="auto")
        decomp = decompress(comp_payload)
        assert decomp == data

        t0 = time.perf_counter()
        for _ in range(runs):
            comp_payload = compress(data, method="auto")
        t1 = time.perf_counter()

        t2 = time.perf_counter()
        for _ in range(runs):
            _ = decompress(comp_payload)
        t3 = time.perf_counter()

        ratio = len(data) / len(comp_payload) if len(comp_payload) else 1.0
        print(
            f"size={size:6d}B  ratio={ratio:5.2f}  "
            f"compress={((t1 - t0)/runs)*1e3:7.3f} ms  "
            f"decompress={((t3 - t2)/runs)*1e3:7.3f} ms"
        )
    print()


if __name__ == "__main__":
    sizes = (1024, 4096, 16384)
    _bench_one("chat", sizes)
    _bench_one("code", sizes)
    _bench_one("log", sizes)

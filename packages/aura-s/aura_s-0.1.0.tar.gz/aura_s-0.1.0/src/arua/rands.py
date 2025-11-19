"""Deterministic pseudo-random number generator utilities.

This module provides a small RNG class used in tests. The implementation
aims to be:

* simple and self-contained,
* fully deterministic and repeatable given a seed,
* independent of ``random`` from the standard library.
"""

from __future__ import annotations


class RNG:
    """Simple 64-bit linear congruential generator.

    The generator maintains a 64-bit state and exposes methods used in tests:

    * :meth:`rand64` – produce a 64-bit unsigned integer.
    * :meth:`rand32` – produce a 32-bit unsigned integer.
    * :meth:`randbytes` – produce a sequence of random bytes.
    * :meth:`seed` – reset the internal state.
    """

    _MOD = 1 << 64
    _MASK64 = _MOD - 1
    _MASK32 = (1 << 32) - 1

    # Parameters from Numerical Recipes LCG
    _A = 6364136223846793005
    _C = 1

    def __init__(self, seed: int) -> None:
        self._state = 0
        self.seed(seed)

    def seed(self, seed: int) -> None:
        """Reset the RNG state with the given seed."""
        self._state = seed & self._MASK64
        if self._state == 0:
            self._state = 1

    def _next(self) -> int:
        """Advance and return the internal 64-bit state."""
        self._state = (self._A * self._state + self._C) & self._MASK64
        return self._state

    def rand64(self) -> int:
        """Return the next 64-bit unsigned integer."""
        return self._next()

    def rand32(self) -> int:
        """Return the next 32-bit unsigned integer."""
        return self._next() & self._MASK32

    def randbytes(self, n: int) -> bytes:
        """Return ``n`` pseudo-random bytes."""
        if n <= 0:
            return b""
        out: list[int] = []
        while len(out) < n:
            value = self._next()
            for shift in range(0, 64, 8):
                if len(out) >= n:
                    break
                out.append((value >> shift) & 0xFF)
        return bytes(out)


class FastRNG(RNG):
    """Alias for :class:`RNG` kept for compatibility."""

    pass

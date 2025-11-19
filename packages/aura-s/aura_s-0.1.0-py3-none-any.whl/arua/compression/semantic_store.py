"""Shared store interfaces for Su/Sm/Sz/Ss.

This module defines a small, pluggable key/value store abstraction used
by stateful codecs such as Su (Semantic Unique), Sz (Semantic Z), and
Sm (Semantic Memory). The default implementation is a process-local
dict with a lock; callers can later swap in sharded, GPU, or remote
stores without changing codec wire formats.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Dict, Protocol


class SemanticStore(Protocol):
    """Minimal interface for semantic chunk stores."""

    def put(self, key: bytes, value: bytes) -> None:  # pragma: no cover - interface
        ...

    def get(self, key: bytes) -> bytes | None:  # pragma: no cover - interface
        ...

    def reset(self) -> None:  # pragma: no cover - interface
        ...

    def snapshot(self) -> Dict[bytes, bytes]:  # pragma: no cover - interface
        ...


@dataclass
class InMemoryStore(SemanticStore):
    """Simple process-local dict-based store with a lock."""

    _data: Dict[bytes, bytes] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def put(self, key: bytes, value: bytes) -> None:
        with self._lock:
            self._data[key] = value

    def get(self, key: bytes) -> bytes | None:
        with self._lock:
            return self._data.get(key)

    def reset(self) -> None:
        with self._lock:
            self._data.clear()

    def snapshot(self) -> Dict[bytes, bytes]:
        with self._lock:
            return dict(self._data)


@dataclass
class ShardedStore(SemanticStore):
    """Sharded in-memory store to reduce lock contention.

    Keys are assigned to shards using a simple hash modulo
    ``num_shards``. Each shard is an independent ``InMemoryStore``.
    """

    num_shards: int = 256
    _shards: Dict[int, InMemoryStore] = field(init=False)

    def __post_init__(self) -> None:
        if self.num_shards <= 0:
            raise ValueError("num_shards must be positive")
        self._shards = {i: InMemoryStore() for i in range(self.num_shards)}

    def _shard_for(self, key: bytes) -> InMemoryStore:
        index = hash(key) % self.num_shards
        return self._shards[index]

    def put(self, key: bytes, value: bytes) -> None:
        shard = self._shard_for(key)
        shard.put(key, value)

    def get(self, key: bytes) -> bytes | None:
        shard = self._shard_for(key)
        return shard.get(key)

    def reset(self) -> None:
        for shard in self._shards.values():
            shard.reset()

    def snapshot(self) -> Dict[bytes, bytes]:
        combined: Dict[bytes, bytes] = {}
        for shard in self._shards.values():
            combined.update(shard.snapshot())
        return combined

"""L1 In-Memory TTL Cache (ADR-001 Dual-Tier Caching)."""

import threading
import time
from typing import Any


class L1MemoryCache:
    """Thread-safe L1 In-Memory TTL Cache for ultra-low-latency hot path decision caching."""

    def __init__(self, default_ttl_seconds: float = 5.0) -> None:
        self.default_ttl = default_ttl_seconds
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = threading.Lock()
        self._stats = {"hits": 0, "misses": 0, "evictions": 0}

    def get(self, key: str) -> Any | None:
        with self._lock:
            if key in self._store:
                value, expires_at = self._store[key]
                if time.time() < expires_at:
                    self._stats["hits"] += 1
                    return value
                else:
                    del self._store[key]
                    self._stats["evictions"] += 1

            self._stats["misses"] += 1
            return None

    def set(self, key: str, value: Any, ttl_seconds: float | None = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expires_at = time.time() + ttl
        with self._lock:
            self._store[key] = (value, expires_at)

    def invalidate(self, key: str) -> None:
        with self._lock:
            if key in self._store:
                del self._store[key]

    def get_stats(self) -> dict[str, int]:
        with self._lock:
            return {
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "evictions": self._stats["evictions"],
                "size": len(self._store),
            }

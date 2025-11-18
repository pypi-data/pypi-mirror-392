"""
Thread Safety Utilities

This module provides thread-safe data structures and utilities for concurrent access.
"""

import time
import threading
from threading import Lock, RLock
from typing import Any, Optional, Dict, Dict
from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging


class AtomicCounter:
    """Thread-safe atomic counter for metrics."""

    def __init__(self, initial_value: int = 0):
        self._value = initial_value
        self._lock = Lock()

    def increment(self, delta: int = 1) -> int:
        """Increment counter and return new value."""
        with self._lock:
            self._value += delta
            return self._value

    def decrement(self, delta: int = 1) -> int:
        """Decrement counter and return new value."""
        with self._lock:
            self._value -= delta
            return self._value

    def get(self) -> int:
        """Get current value."""
        with self._lock:
            return self._value

    def set(self, value: int) -> None:
        """Set counter value."""
        with self._lock:
            self._value = value

    def compare_and_swap(self, expected: int, new_value: int) -> bool:
        """Compare and swap operation."""
        with self._lock:
            if self._value == expected:
                self._value = new_value
                return True
            return False


class TimeoutLock:
    """Lock with timeout support."""

    def __init__(self, timeout: float = 5.0, name: str = "TimeoutLock"):
        self._lock = RLock()
        self._timeout = timeout
        self._name = name
        self._acquired_time = None
        self._acquired_by = None

    def acquire(self, blocking: bool = True, timeout: Optional[float] = None) -> bool:
        """Acquire the lock with optional timeout."""
        if timeout is None:
            timeout = self._timeout

        try:
            acquired = self._lock.acquire(blocking=blocking, timeout=timeout)
            if acquired:
                self._acquired_time = time.time()
                self._acquired_by = threading.current_thread().name
            return acquired
        except Exception:
            return False

    def release(self) -> None:
        """Release the lock."""
        if self._lock._is_owned():
            self._acquired_time = None
            self._acquired_by = None
            self._lock.release()

    def __enter__(self):
        if not self.acquire(blocking=True, timeout=self._timeout):
            raise TimeoutError(f"Failed to acquire {self._name} within {self._timeout}s")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def is_locked(self) -> bool:
        """Check if lock is currently held."""
        return self._lock._is_owned()

    def get_lock_info(self) -> Dict[str, Any]:
        """Get information about the lock state."""
        return {
            "name": self._name,
            "is_locked": self.is_locked(),
            "acquired_by": self._acquired_by,
            "acquired_time": self._acquired_time,
            "held_duration": time.time() - self._acquired_time if self._acquired_time else None
        }


@dataclass
class CacheEntry:
    """Cache entry with TTL support."""
    value: Any
    created_at: float = field(default_factory=time.time)
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)


class ThreadSafeCache:
    """Thread-safe cache with TTL and size limits."""

    def __init__(self, max_size: int = 1000, ttl_seconds: Optional[float] = None):
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_accesses": 0
        }

    def put(self, key: str, value: Any) -> None:
        """Put a value in the cache."""
        with self._lock:
            current_time = time.time()

            # Check if key already exists
            if key in self._cache:
                self._cache[key].value = value
                self._cache[key].last_accessed = current_time
                return

            # Enforce size limit
            if len(self._cache) >= self._max_size:
                self._evict_lru()

            # Add new entry
            self._cache[key] = CacheEntry(value=value, created_at=current_time, last_accessed=current_time)

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        with self._lock:
            self._stats["total_accesses"] += 1
            current_time = time.time()

            if key not in self._cache:
                self._stats["misses"] += 1
                return None

            entry = self._cache[key]

            # Check TTL
            if self._ttl_seconds and (current_time - entry.created_at) > self._ttl_seconds:
                del self._cache[key]
                self._stats["misses"] += 1
                return None

            # Update access info
            entry.access_count += 1
            entry.last_accessed = current_time
            self._stats["hits"] += 1
            return entry.value

    def remove(self, key: str) -> bool:
        """Remove a key from the cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._cache.clear()
            self._stats = {
                "hits": 0,
                "misses": 0,
                "evictions": 0,
                "total_accesses": 0
            }

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._cache:
            return

        # Find LRU entry
        lru_key = min(self._cache.keys(), key=lambda k: self._cache[k].last_accessed)
        del self._cache[lru_key]
        self._stats["evictions"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_accesses = self._stats["total_accesses"]
            hit_rate = self._stats["hits"] / max(1, total_accesses)

            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "evictions": self._stats["evictions"],
                "total_accesses": total_accesses,
                "hit_rate": hit_rate,
                "ttl_seconds": self._ttl_seconds
            }

    def get_keys(self) -> list:
        """Get all keys in the cache."""
        with self._lock:
            return list(self._cache.keys())

    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self._cache)

    def cleanup_expired(self) -> int:
        """Clean up expired entries and return count of cleaned entries."""
        if not self._ttl_seconds:
            return 0

        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, entry in self._cache.items()
                if (current_time - entry.created_at) > self._ttl_seconds
            ]

            for key in expired_keys:
                del self._cache[key]

            return len(expired_keys)
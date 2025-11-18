"""
Persistent Rate Limiting Storage

ARCH-003: This module provides persistent rate limiting storage to prevent
data loss on restart and eliminate security blind spots.

Features:
1. File-based persistent storage (default)
2. Redis-based distributed storage (optional)
3. Automatic cleanup of expired entries
4. Graceful fallback to in-memory storage
5. Thread-safe operations
6. Configurable retention policies
"""

import json
import os
import time
import threading
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
import hashlib
import logging

from .security_events import RateLimitInfo


@dataclass
class PersistentRateLimitEntry:
    """Persistent rate limit data structure."""
    source: str
    event_timestamps: List[float]
    window_seconds: int
    threshold: int
    last_updated: str
    total_events: int
    blocked_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersistentRateLimitEntry':
        """Create from dictionary for deserialization."""
        return cls(**data)


class RateLimitStorage(ABC):
    """Abstract interface for rate limit storage."""

    @abstractmethod
    def get_rate_limit_info(self, source: str, window_seconds: int = 300, threshold: int = 100) -> RateLimitInfo:
        """Get rate limit info for a source."""
        pass

    @abstractmethod
    def update_rate_limit(self, source: str, timestamp: float, window_seconds: int = 300, threshold: int = 100) -> bool:
        """Update rate limit for a source. Returns True if rate limited."""
        pass

    @abstractmethod
    def cleanup_expired_entries(self) -> int:
        """Clean up expired entries. Returns number of entries cleaned."""
        pass

    @abstractmethod
    def get_all_sources(self) -> Set[str]:
        """Get all sources with rate limit data."""
        pass

    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Get storage metrics."""
        pass


class FileBasedRateLimitStorage(RateLimitStorage):
    """File-based persistent rate limit storage."""

    def __init__(self, storage_file: str = "security_rate_limits.json",
                 cleanup_interval: int = 300, max_file_size: int = 10 * 1024 * 1024):
        """
        Initialize file-based storage.

        Args:
            storage_file: Path to the storage file
            cleanup_interval: Seconds between automatic cleanups
            max_file_size: Maximum file size in bytes (default 10MB)
        """
        self.storage_file = Path(storage_file)
        self.cleanup_interval = cleanup_interval
        self.max_file_size = max_file_size
        self._lock = threading.RLock()
        self._data: Dict[str, PersistentRateLimitEntry] = {}
        self._dirty = False
        self._last_cleanup = time.time()
        self._logger = logging.getLogger(__name__)

        # Load existing data
        self._load_data()

        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self._cleanup_thread.start()

    def _load_data(self) -> None:
        """Load rate limit data from file."""
        try:
            if self.storage_file.exists() and self.storage_file.stat().st_size > 0:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)

                for source, entry_data in file_data.items():
                    try:
                        entry = PersistentRateLimitEntry.from_dict(entry_data)
                        # Only load recent entries (within last hour)
                        entry_time = datetime.fromisoformat(entry.last_updated)
                        if datetime.now(timezone.utc) - entry_time < timedelta(hours=1):
                            self._data[source] = entry
                    except Exception as e:
                        self._logger.warning(f"Failed to load rate limit entry for {source}: {e}")

                self._logger.info(f"Loaded {len(self._data)} rate limit entries from {self.storage_file}")

        except Exception as e:
            self._logger.error(f"Failed to load rate limit data: {e}")
            self._data = {}

    def _save_data(self) -> None:
        """Save rate limit data to file."""
        if not self._dirty:
            return

        try:
            # Create backup of existing file
            if self.storage_file.exists():
                backup_file = self.storage_file.with_suffix('.json.bak')
                self.storage_file.rename(backup_file)

            # Convert data to serializable format
            serializable_data = {}
            for source, entry in self._data.items():
                try:
                    serializable_data[source] = entry.to_dict()
                except Exception as e:
                    self._logger.warning(f"Failed to serialize entry for {source}: {e}")

            # Write to temporary file first
            temp_file = self.storage_file.with_suffix('.json.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)

            # Move temp file to final location
            temp_file.rename(self.storage_file)
            self._dirty = False

            # Check file size and rotate if necessary
            if self.storage_file.stat().st_size > self.max_file_size:
                self._rotate_file()

        except Exception as e:
            self._logger.error(f"Failed to save rate limit data: {e}")

    def _rotate_file(self) -> None:
        """Rotate the storage file if it's too large."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archive_file = self.storage_file.with_name(f"{self.storage_file.stem}_{timestamp}.json")

            if self.storage_file.exists():
                self.storage_file.rename(archive_file)
                self._logger.info(f"Rotated rate limit file to {archive_file}")

        except Exception as e:
            self._logger.error(f"Failed to rotate rate limit file: {e}")

    def _cleanup_worker(self) -> None:
        """Background worker for periodic cleanup."""
        while True:
            try:
                time.sleep(self.cleanup_interval)
                cleaned = self.cleanup_expired_entries()
                if cleaned > 0:
                    self._logger.debug(f"Cleaned up {cleaned} expired rate limit entries")
            except Exception as e:
                self._logger.error(f"Error in cleanup worker: {e}")

    def get_rate_limit_info(self, source: str, window_seconds: int = 300, threshold: int = 100) -> RateLimitInfo:
        """Get rate limit info for a source."""
        with self._lock:
            current_time = time.time()

            if source not in self._data:
                self._data[source] = PersistentRateLimitEntry(
                    source=source,
                    event_timestamps=[],
                    window_seconds=window_seconds,
                    threshold=threshold,
                    last_updated=datetime.now(timezone.utc).isoformat(),
                    total_events=0,
                    blocked_count=0
                )
                self._dirty = True

            entry = self._data[source]

            # Clean old entries
            cutoff_time = current_time - window_seconds
            entry.event_timestamps = [ts for ts in entry.event_timestamps if ts > cutoff_time]

            # Update window and threshold if they changed
            if entry.window_seconds != window_seconds or entry.threshold != threshold:
                entry.window_seconds = window_seconds
                entry.threshold = threshold
                self._dirty = True

            return RateLimitInfo(
                source=source,
                event_timestamps=entry.event_timestamps.copy(),
                window_seconds=window_seconds,
                threshold=threshold
            )

    def update_rate_limit(self, source: str, timestamp: float, window_seconds: int = 300, threshold: int = 100) -> bool:
        """Update rate limit for a source. Returns True if rate limited."""
        with self._lock:
            if source not in self._data:
                self.get_rate_limit_info(source, window_seconds, threshold)

            entry = self._data[source]
            current_time = time.time()

            # Clean old entries
            cutoff_time = current_time - window_seconds
            entry.event_timestamps = [ts for ts in entry.event_timestamps if ts > cutoff_time]

            # Add new timestamp
            entry.event_timestamps.append(timestamp)
            entry.total_events += 1
            entry.last_updated = datetime.now(timezone.utc).isoformat()
            self._dirty = True

            # Check if rate limited
            is_limited = len(entry.event_timestamps) > threshold
            if is_limited:
                entry.blocked_count += 1

            # Periodically save data
            if self._dirty and (len(self._data) % 10 == 0 or current_time - self._last_cleanup > 60):
                self._save_data()

            return is_limited

    def cleanup_expired_entries(self) -> int:
        """Clean up expired entries. Returns number of entries cleaned."""
        with self._lock:
            current_time = time.time()
            cleaned = 0
            sources_to_remove = []

            for source, entry in self._data.items():
                # Remove entries older than 1 hour with no recent activity
                entry_time = datetime.fromisoformat(entry.last_updated)
                if (current_time - entry.timestamp > 3600 and
                    current_time - entry_time > timedelta(hours=1)):
                    sources_to_remove.append(source)
                else:
                    # Clean old timestamps within the entry
                    cutoff_time = current_time - entry.window_seconds
                    original_count = len(entry.event_timestamps)
                    entry.event_timestamps = [ts for ts in entry.event_timestamps if ts > cutoff_time]
                    if len(entry.event_timestamps) != original_count:
                        self._dirty = True

            # Remove expired entries
            for source in sources_to_remove:
                del self._data[source]
                cleaned += 1
                self._dirty = True

            self._last_cleanup = current_time

            if self._dirty:
                self._save_data()

            return cleaned

    def get_all_sources(self) -> Set[str]:
        """Get all sources with rate limit data."""
        with self._lock:
            return set(self._data.keys())

    def get_metrics(self) -> Dict[str, Any]:
        """Get storage metrics."""
        with self._lock:
            total_sources = len(self._data)
            total_events = sum(entry.total_events for entry in self._data.values())
            total_blocked = sum(entry.blocked_count for entry in self._data.values())
            active_sources = sum(1 for entry in self._data.values() if entry.event_timestamps)

            try:
                file_size = self.storage_file.stat().st_size if self.storage_file.exists() else 0
            except OSError:
                file_size = 0

            return {
                "storage_type": "file_based",
                "total_sources": total_sources,
                "total_events": total_events,
                "total_blocked": total_blocked,
                "active_sources": active_sources,
                "file_size_bytes": file_size,
                "storage_file": str(self.storage_file),
                "last_cleanup": self._last_cleanup
            }

    def __del__(self):
        """Cleanup on deletion."""
        try:
            if self._dirty:
                self._save_data()
        except Exception:
            pass


class RedisRateLimitStorage(RateLimitStorage):
    """Redis-based distributed rate limit storage."""

    def __init__(self, redis_url: str = "redis://localhost:6379",
                 key_prefix: str = "rate_limit:", ttl: int = 3600):
        """
        Initialize Redis storage.

        Args:
            redis_url: Redis connection URL
            key_prefix: Prefix for Redis keys
            ttl: Time-to-live for keys in seconds
        """
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.ttl = ttl
        self._logger = logging.getLogger(__name__)

        try:
            import redis
            self._redis = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self._redis.ping()
            self._logger.info("Connected to Redis for rate limiting")
        except ImportError:
            self._logger.error("redis package not installed. Use: pip install redis")
            raise
        except Exception as e:
            self._logger.error(f"Failed to connect to Redis: {e}")
            raise

    def _get_key(self, source: str, window_seconds: int, threshold: int) -> str:
        """Generate Redis key for rate limit data."""
        # Create a stable key based on source, window, and threshold
        key_data = f"{source}:{window_seconds}:{threshold}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:16]
        return f"{self.key_prefix}{key_hash}"

    def get_rate_limit_info(self, source: str, window_seconds: int = 300, threshold: int = 100) -> RateLimitInfo:
        """Get rate limit info for a source."""
        key = self._get_key(source, window_seconds, threshold)
        current_time = time.time()
        cutoff_time = current_time - window_seconds

        try:
            # Use Redis sorted set for efficient time-based queries
            self._redis.zremrangebyscore(key, 0, cutoff_time)
            timestamps = [float(ts) for ts in self._redis.zrange(key, 0, -1, withscores=True)]

            return RateLimitInfo(
                source=source,
                event_timestamps=timestamps,
                window_seconds=window_seconds,
                threshold=threshold
            )
        except Exception as e:
            self._logger.error(f"Failed to get rate limit info from Redis: {e}")
            # Fallback to empty rate limit info
            return RateLimitInfo(source=source, window_seconds=window_seconds, threshold=threshold)

    def update_rate_limit(self, source: str, timestamp: float, window_seconds: int = 300, threshold: int = 100) -> bool:
        """Update rate limit for a source. Returns True if rate limited."""
        key = self._get_key(source, window_seconds, threshold)
        current_time = time.time()
        cutoff_time = current_time - window_seconds

        try:
            # Clean old entries and add new one
            pipe = self._redis.pipeline()
            pipe.zremrangebyscore(key, 0, cutoff_time)
            pipe.zadd(key, {str(timestamp): timestamp})
            pipe.expire(key, self.ttl)
            pipe.execute()

            # Check current count
            count = self._redis.zcard(key)
            return count > threshold

        except Exception as e:
            self._logger.error(f"Failed to update rate limit in Redis: {e}")
            return False

    def cleanup_expired_entries(self) -> int:
        """Clean up expired entries. Returns number of entries cleaned."""
        # Redis handles TTL automatically, so this is mainly for monitoring
        try:
            keys = self._redis.keys(f"{self.key_prefix}*")
            cleaned = 0
            for key in keys:
                ttl = self._redis.ttl(key)
                if ttl == -1:  # No TTL set, set one
                    self._redis.expire(key, self.ttl)
                elif ttl == -2:  # Key expired but not yet cleaned
                    cleaned += 1
            return cleaned
        except Exception as e:
            self._logger.error(f"Failed to cleanup Redis entries: {e}")
            return 0

    def get_all_sources(self) -> Set[str]:
        """Get all sources with rate limit data."""
        try:
            keys = self._redis.keys(f"{self.key_prefix}*")
            # Extract source info from keys (this is approximate since we hash the key)
            return set(key.split(':')[-1] for key in keys)
        except Exception as e:
            self._logger.error(f"Failed to get all sources from Redis: {e}")
            return set()

    def get_metrics(self) -> Dict[str, Any]:
        """Get storage metrics."""
        try:
            info = self._redis.info()
            keys = self._redis.keys(f"{self.key_prefix}*")

            return {
                "storage_type": "redis",
                "total_keys": len(keys),
                "redis_memory_used": info.get('used_memory', 0),
                "redis_connected_clients": info.get('connected_clients', 0),
                "redis_url": self.redis_url,
                "key_prefix": self.key_prefix,
                "ttl": self.ttl
            }
        except Exception as e:
            self._logger.error(f"Failed to get Redis metrics: {e}")
            return {"storage_type": "redis", "error": str(e)}


class MemoryRateLimitStorage(RateLimitStorage):
    """In-memory rate limit storage (fallback)."""

    def __init__(self):
        """Initialize in-memory storage."""
        self._data: Dict[str, RateLimitInfo] = {}
        self._lock = threading.RLock()
        self._logger = logging.getLogger(__name__)

    def get_rate_limit_info(self, source: str, window_seconds: int = 300, threshold: int = 100) -> RateLimitInfo:
        """Get rate limit info for a source."""
        with self._lock:
            if source not in self._data:
                self._data[source] = RateLimitInfo(source, [], window_seconds, threshold)
            return self._data[source]

    def update_rate_limit(self, source: str, timestamp: float, window_seconds: int = 300, threshold: int = 100) -> bool:
        """Update rate limit for a source. Returns True if rate limited."""
        with self._lock:
            info = self.get_rate_limit_info(source, window_seconds, threshold)
            return info.is_rate_limited(timestamp)

    def cleanup_expired_entries(self) -> int:
        """Clean up expired entries. Returns number of entries cleaned."""
        with self._lock:
            current_time = time.time()
            cleaned = 0
            sources_to_remove = []

            for source, info in self._data.items():
                cutoff_time = current_time - info.window_seconds
                original_count = len(info.event_timestamps)
                info.event_timestamps = [ts for ts in info.event_timestamps if ts > cutoff_time]

                if len(info.event_timestamps) == 0:
                    sources_to_remove.append(source)
                elif len(info.event_timestamps) != original_count:
                    cleaned += original_count - len(info.event_timestamps)

            for source in sources_to_remove:
                del self._data[source]

            return cleaned

    def get_all_sources(self) -> Set[str]:
        """Get all sources with rate limit data."""
        with self._lock:
            return set(self._data.keys())

    def get_metrics(self) -> Dict[str, Any]:
        """Get storage metrics."""
        with self._lock:
            total_events = sum(len(info.event_timestamps) for info in self._data.values())
            return {
                "storage_type": "memory",
                "total_sources": len(self._data),
                "total_events": total_events,
                "active_sources": sum(1 for info in self._data.values() if info.event_timestamps)
            }


class RateLimitStorageFactory:
    """Factory for creating rate limit storage instances."""

    @staticmethod
    def create_storage(storage_type: str = "auto", **kwargs) -> RateLimitStorage:
        """
        Create a rate limit storage instance.

        Args:
            storage_type: Type of storage ("file", "redis", "memory", "auto")
            **kwargs: Additional arguments for the storage implementation

        Returns:
            RateLimitStorage instance
        """
        if storage_type == "file":
            return FileBasedRateLimitStorage(**kwargs)
        elif storage_type == "redis":
            return RedisRateLimitStorage(**kwargs)
        elif storage_type == "memory":
            return MemoryRateLimitStorage()
        elif storage_type == "auto":
            # Auto-detect best storage option
            try:
                # Try Redis first
                return RedisRateLimitStorage(**kwargs)
            except Exception:
                # Fall back to file-based storage
                try:
                    return FileBasedRateLimitStorage(**kwargs)
                except Exception:
                    # Final fallback to memory storage
                    return MemoryRateLimitStorage()
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")


# Global storage instance
_storage_instance: Optional[RateLimitStorage] = None
_storage_lock = threading.Lock()


def get_rate_limit_storage(storage_type: str = "auto", **kwargs) -> RateLimitStorage:
    """
    Get the global rate limit storage instance.

    Args:
        storage_type: Type of storage to create
        **kwargs: Additional arguments for storage creation

    Returns:
        RateLimitStorage instance
    """
    global _storage_instance
    if _storage_instance is None:
        with _storage_lock:
            if _storage_instance is None:
                _storage_instance = RateLimitStorageFactory.create_storage(storage_type, **kwargs)
    return _storage_instance


def reset_rate_limit_storage() -> None:
    """Reset the global rate limit storage (useful for testing)."""
    global _storage_instance
    with _storage_lock:
        _storage_instance = None
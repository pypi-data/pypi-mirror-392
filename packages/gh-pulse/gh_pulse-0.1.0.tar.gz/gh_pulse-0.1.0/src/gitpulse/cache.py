"""Simple file-based caching system for GitHub API responses."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .models import CacheEntry


class CacheManager:
    """Manages file-based cache for GitHub API data."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize cache manager.

        Args:
            cache_dir: Directory for cache files. Defaults to ~/.gitpulse/cache
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".gitpulse" / "cache"

        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for a given key."""
        # Sanitize key for filesystem
        safe_key = key.replace("/", "_").replace(":", "_")
        return self.cache_dir / f"{safe_key}.json"

    def get(self, key: str) -> Optional[dict]:
        """Get cached data if exists and not expired.

        Args:
            key: Cache key (e.g., 'repo:owner/name' or 'user:username')

        Returns:
            Cached data or None if not found/expired
        """
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            # Parse as CacheEntry
            entry = CacheEntry(
                data=cache_data["data"],
                cached_at=datetime.fromisoformat(cache_data["cached_at"]),
                ttl_seconds=cache_data.get("ttl_seconds", 3600),
            )

            # Check if expired
            if entry.is_expired():
                cache_path.unlink()  # Remove expired cache
                return None

            return entry.data

        except (json.JSONDecodeError, KeyError, ValueError):
            # Invalid cache file, remove it
            cache_path.unlink(missing_ok=True)
            return None

    def set(self, key: str, data: dict, ttl_seconds: int = 3600) -> None:
        """Store data in cache.

        Args:
            key: Cache key
            data: Data to cache
            ttl_seconds: Time-to-live in seconds (default: 1 hour)
        """
        cache_path = self._get_cache_path(key)

        entry = CacheEntry(
            data=data,
            cached_at=datetime.now(),
            ttl_seconds=ttl_seconds,
        )

        cache_data = {
            "data": entry.data,
            "cached_at": entry.cached_at.isoformat(),
            "ttl_seconds": entry.ttl_seconds,
        }

        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2)

    def clear(self, key: Optional[str] = None) -> None:
        """Clear cache.

        Args:
            key: Specific key to clear. If None, clears all cache.
        """
        if key is None:
            # Clear all cache
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
        else:
            # Clear specific key
            cache_path = self._get_cache_path(key)
            cache_path.unlink(missing_ok=True)


# Global cache instance
_cache = CacheManager()


def get_cache() -> CacheManager:
    """Get global cache instance."""
    return _cache

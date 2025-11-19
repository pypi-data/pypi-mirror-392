"""
Performance caching module for public domain validation results.
"""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Optional

from cachetools import TTLCache, LRUCache


class ValidationCache:
    """
    Multi-level caching system for validation results.

    L1: In-memory LRU cache for recent results
    L2: TTL cache for computed PD status (1 hour)
    L3: Optional persistent cache for expensive computations
    """

    def __init__(self, l1_size: int = 1000, l2_ttl: int = 3600):
        self._lock = RLock()

        # L1: Fast in-memory cache for recent validations
        self.l1_cache = LRUCache(maxsize=l1_size)

        # L2: Time-based cache for PD status
        self.l2_cache = TTLCache(maxsize=5000, ttl=l2_ttl)

        # Cache statistics
        self.hits = 0
        self.misses = 0

    def get_cache_key(
        self, title: str, content: Optional[str] = None, snippet: Optional[str] = None
    ) -> str:
        """
        Generate deterministic cache key from content.
        """
        # Combine relevant fields for cache key
        cache_content = f"{title}|{content or ''}|{snippet or ''}"
        return hashlib.sha256(cache_content.encode("utf-8")).hexdigest()

    def get(
        self, title: str, content: Optional[str] = None, snippet: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached validation result.
        """
        key = self.get_cache_key(title, content, snippet)

        with self._lock:
            # Check L1 cache first
            if key in self.l1_cache:
                self.hits += 1
                return self.l1_cache[key]

            # Check L2 cache
            if key in self.l2_cache:
                result = self.l2_cache[key]
                # Promote to L1
                self.l1_cache[key] = result
                self.hits += 1
                return result

            self.misses += 1
            return None

    def set(
        self,
        title: str,
        result: Dict[str, Any],
        content: Optional[str] = None,
        snippet: Optional[str] = None,
    ) -> None:
        """
        Cache validation result.
        """
        key = self.get_cache_key(title, content, snippet)

        with self._lock:
            # Store in both caches
            self.l1_cache[key] = result
            self.l2_cache[key] = result

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.
        """
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_percent": round(hit_rate, 2),
            "l1_size": len(self.l1_cache),
            "l2_size": len(self.l2_cache),
        }

    def clear(self) -> None:
        """
        Clear all caches.
        """
        with self._lock:
            self.l1_cache.clear()
            self.l2_cache.clear()
            self.hits = 0
            self.misses = 0


class ConfigCache:
    """
    Lazy loading cache for configuration data.
    """

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._lock = RLock()

    def get_config(self, config_path: str, loader_func) -> Any:
        """
        Get configuration with lazy loading.
        """
        with self._lock:
            if config_path not in self._cache:
                self._cache[config_path] = loader_func(config_path)
            return self._cache[config_path]

    def preload_configs(self, configs: Dict[str, str]) -> None:
        """
        Preload common configurations.
        """
        with self._lock:
            for name, path in configs.items():
                from pathlib import Path

                if Path(path).exists() and name not in self._cache:
                    # This would be called with appropriate loader functions
                    pass


# Global cache instance
_validation_cache = ValidationCache()
_config_cache = ConfigCache()


def get_validation_cache() -> ValidationCache:
    """Get the global validation cache instance."""
    return _validation_cache


def get_config_cache() -> ConfigCache:
    """Get the global configuration cache instance."""
    return _config_cache


@lru_cache(maxsize=128)
def cached_string_lower(s: str) -> str:
    """
    Cache lowercase conversions to avoid repeated computations.
    """
    return s.lower()


@lru_cache(maxsize=64)
def cached_content_hash(content: str) -> str:
    """
    Cache content hash computations.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

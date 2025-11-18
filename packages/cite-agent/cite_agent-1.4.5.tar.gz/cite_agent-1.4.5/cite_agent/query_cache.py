#!/usr/bin/env python3
"""
Query Cache Module

Simple LRU cache for repeated queries to save API costs and improve response time.
Features:
- TTL-based expiration (default 1 hour)
- LRU eviction for cache size management
- Query normalization for better hit rates
- Persistence to disk (optional)
"""

import hashlib
import json
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class CacheEntry:
    """Single cache entry with metadata"""
    query_hash: str
    query: str
    response: str
    tools_used: list
    tokens_used: int
    created_at: float
    access_count: int = 1
    last_accessed: float = None

    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at


class QueryCache:
    """
    LRU cache for query responses.

    Features:
    - Automatic TTL expiration
    - LRU eviction when cache is full
    - Query normalization for better hit rates
    - Optional disk persistence
    """

    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600, persist: bool = True):
        """
        Initialize cache.

        Args:
            max_size: Maximum number of entries (default 100)
            ttl_seconds: Time-to-live in seconds (default 1 hour)
            persist: Whether to persist cache to disk (default True)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.persist = persist
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expirations": 0,
        }

        # Persistence path
        self.cache_dir = Path.home() / ".cite_agent" / "cache"
        self.cache_file = self.cache_dir / "query_cache.json"

        # Load from disk if persistence enabled
        if self.persist:
            self._load_from_disk()

    def _normalize_query(self, query: str) -> str:
        """
        Normalize query for better cache hit rates.
        - Lowercase
        - Strip extra whitespace
        - Remove punctuation variations
        """
        normalized = query.lower().strip()
        # Remove extra spaces
        normalized = " ".join(normalized.split())
        # Remove trailing punctuation that doesn't change meaning
        normalized = normalized.rstrip("?!.")
        return normalized

    def _hash_query(self, query: str) -> str:
        """Create hash of normalized query"""
        normalized = self._normalize_query(query)
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached response for query.

        Returns:
            Dict with response, tools_used, tokens_used if found, None otherwise
        """
        query_hash = self._hash_query(query)

        if query_hash not in self._cache:
            self._stats["misses"] += 1
            return None

        entry = self._cache[query_hash]

        # Check TTL
        if time.time() - entry.created_at > self.ttl_seconds:
            # Entry expired
            del self._cache[query_hash]
            self._stats["expirations"] += 1
            self._stats["misses"] += 1
            if self.persist:
                self._save_to_disk()
            return None

        # Update access stats and move to end (most recently used)
        entry.access_count += 1
        entry.last_accessed = time.time()
        self._cache.move_to_end(query_hash)
        self._stats["hits"] += 1

        return {
            "response": entry.response,
            "tools_used": entry.tools_used,
            "tokens_used": entry.tokens_used,
            "cached": True,
            "cache_age": time.time() - entry.created_at,
        }

    def put(self, query: str, response: str, tools_used: list, tokens_used: int):
        """
        Store query response in cache.

        Args:
            query: Original query string
            response: Response text
            tools_used: List of tools used
            tokens_used: Number of tokens consumed
        """
        query_hash = self._hash_query(query)

        # Update existing entry or create new one
        if query_hash in self._cache:
            # Update existing
            entry = self._cache[query_hash]
            entry.response = response
            entry.tools_used = tools_used
            entry.tokens_used = tokens_used
            entry.access_count += 1
            entry.last_accessed = time.time()
            self._cache.move_to_end(query_hash)
        else:
            # Create new entry
            entry = CacheEntry(
                query_hash=query_hash,
                query=query,
                response=response,
                tools_used=tools_used,
                tokens_used=tokens_used,
                created_at=time.time(),
            )
            self._cache[query_hash] = entry

            # Evict LRU if over capacity
            if len(self._cache) > self.max_size:
                # Remove oldest (first) entry
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._stats["evictions"] += 1

        if self.persist:
            self._save_to_disk()

    def clear(self):
        """Clear all cache entries"""
        self._cache.clear()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expirations": 0,
        }
        if self.persist:
            self._save_to_disk()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            "entries": len(self._cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds,
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "hit_rate": f"{hit_rate:.1f}%",
            "evictions": self._stats["evictions"],
            "expirations": self._stats["expirations"],
        }

    def _save_to_disk(self):
        """Persist cache to disk"""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

            # Convert to serializable format
            cache_data = {
                "version": 1,
                "stats": self._stats,
                "entries": [asdict(entry) for entry in self._cache.values()],
            }

            with open(self.cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            # Silent fail - caching is non-critical
            pass

    def _load_from_disk(self):
        """Load cache from disk"""
        try:
            if not self.cache_file.exists():
                return

            with open(self.cache_file, "r") as f:
                cache_data = json.load(f)

            if cache_data.get("version") != 1:
                return  # Incompatible version

            self._stats = cache_data.get("stats", self._stats)

            # Rebuild cache (maintaining order)
            for entry_data in cache_data.get("entries", []):
                entry = CacheEntry(**entry_data)

                # Skip expired entries
                if time.time() - entry.created_at > self.ttl_seconds:
                    self._stats["expirations"] += 1
                    continue

                self._cache[entry.query_hash] = entry

            # Trim to max_size if needed
            while len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._stats["evictions"] += 1

        except Exception as e:
            # Silent fail - start with empty cache
            pass


# Global cache instance
_global_cache: Optional[QueryCache] = None


def get_cache() -> QueryCache:
    """Get global cache instance (singleton)"""
    global _global_cache
    if _global_cache is None:
        _global_cache = QueryCache()
    return _global_cache


def cache_query(query: str, response: str, tools_used: list, tokens_used: int):
    """Convenience function to cache a query"""
    get_cache().put(query, response, tools_used, tokens_used)


def get_cached_response(query: str) -> Optional[Dict[str, Any]]:
    """Convenience function to get cached response"""
    return get_cache().get(query)


def clear_cache():
    """Convenience function to clear cache"""
    get_cache().clear()


def cache_stats() -> Dict[str, Any]:
    """Convenience function to get cache stats"""
    return get_cache().get_stats()

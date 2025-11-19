"""
Cache storage and fingerprinting engine
"""

import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, Optional


class CacheEngine:
    """SQLite-based cache storage with fingerprinting"""

    def __init__(self, cache_dir: Optional[str] = None, ttl: Optional[int] = None):
        """
        Initialize cache engine

        Args:
            cache_dir: Directory for cache database (default: ~/.ai-cache/)
            ttl: Time-to-live in seconds for cache entries (None = no expiration)
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".ai-cache"
        else:
            cache_dir = Path(cache_dir)

        cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = cache_dir / "cache.db"
        self.ttl = ttl
        self.stats = {"hits": 0, "misses": 0}

        self._init_db()

    def _init_db(self):
        """Initialize SQLite database with schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    fingerprint TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    response TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    accessed_at INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_created_at ON cache(created_at)"
            )
            conn.commit()

    def _compute_fingerprint(
        self, provider: str, model: str, request_data: Dict[str, Any]
    ) -> str:
        """
        Compute unique fingerprint for a request

        Args:
            provider: API provider name (e.g., 'openai', 'anthropic')
            model: Model identifier
            request_data: Request parameters (prompt, messages, etc.)

        Returns:
            SHA256 fingerprint as hex string
        """
        # Create deterministic representation
        fingerprint_data = {
            "provider": provider,
            "model": model,
            "request": request_data,
        }

        # Sort keys for deterministic JSON
        json_str = json.dumps(fingerprint_data, sort_keys=True, ensure_ascii=True)

        # Compute SHA256 hash
        return hashlib.sha256(json_str.encode("utf-8")).hexdigest()

    def get(
        self, provider: str, model: str, request_data: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Retrieve cached response if available

        Args:
            provider: API provider name
            model: Model identifier
            request_data: Request parameters

        Returns:
            Cached response or None if not found/expired
        """
        fingerprint = self._compute_fingerprint(provider, model, request_data)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT response, created_at FROM cache WHERE fingerprint = ?",
                (fingerprint,),
            )
            row = cursor.fetchone()

            if row is None:
                self.stats["misses"] += 1
                return None

            response_json, created_at = row

            # Check TTL if configured
            if self.ttl is not None:
                age = time.time() - created_at
                if age > self.ttl:
                    # Expired - delete and return None
                    conn.execute("DELETE FROM cache WHERE fingerprint = ?", (fingerprint,))
                    conn.commit()
                    self.stats["misses"] += 1
                    return None

            # Update access time
            conn.execute(
                "UPDATE cache SET accessed_at = ? WHERE fingerprint = ?",
                (int(time.time()), fingerprint),
            )
            conn.commit()

            self.stats["hits"] += 1
            return json.loads(response_json)

    def set(
        self, provider: str, model: str, request_data: Dict[str, Any], response: Any
    ):
        """
        Store response in cache

        Args:
            provider: API provider name
            model: Model identifier
            request_data: Request parameters
            response: API response to cache
        """
        fingerprint = self._compute_fingerprint(provider, model, request_data)
        response_json = json.dumps(response, ensure_ascii=True)
        timestamp = int(time.time())

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache 
                (fingerprint, provider, model, response, created_at, accessed_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (fingerprint, provider, model, response_json, timestamp, timestamp),
            )
            conn.commit()

    def clear(self):
        """Clear all cache entries"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache")
            conn.commit()
        self.stats = {"hits": 0, "misses": 0}

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with hits, misses, total entries, and savings
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            total_entries = cursor.fetchone()[0]

        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (
            (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        )

        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": f"{hit_rate:.1f}%",
            "total_entries": total_entries,
        }

    def invalidate(self, provider: Optional[str] = None, model: Optional[str] = None):
        """
        Invalidate cache entries by provider/model

        Args:
            provider: Filter by provider (None = all)
            model: Filter by model (None = all)
        """
        with sqlite3.connect(self.db_path) as conn:
            if provider is None and model is None:
                conn.execute("DELETE FROM cache")
            elif model is None:
                conn.execute("DELETE FROM cache WHERE provider = ?", (provider,))
            elif provider is None:
                conn.execute("DELETE FROM cache WHERE model = ?", (model,))
            else:
                conn.execute(
                    "DELETE FROM cache WHERE provider = ? AND model = ?",
                    (provider, model),
                )
            conn.commit()

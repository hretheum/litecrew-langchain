"""
Response caching for LLM calls.
"""

import hashlib
import json
import time
from collections import OrderedDict
from typing import Any, Dict, Optional


class ResponseCache:
    """LRU cache for LLM responses."""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize response cache.

        Args:
            max_size: Maximum number of cached items
            ttl_seconds: Time to live for cache entries
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
        }

    def _generate_key(
        self, prompt: str, provider: Optional[str] = None, **kwargs
    ) -> str:
        """Generate cache key from prompt and parameters."""
        key_data = {"prompt": prompt, "provider": provider, **kwargs}
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(
        self, prompt: str, provider: Optional[str] = None, **kwargs
    ) -> Optional[str]:
        """
        Get cached response.

        Args:
            prompt: The prompt to look up
            provider: LLM provider name
            **kwargs: Additional parameters that affect the response

        Returns:
            Cached response or None if not found/expired
        """
        key = self._generate_key(prompt, provider, **kwargs)

        if key in self._cache:
            entry = self._cache[key]

            # Check if expired
            if time.time() - entry["timestamp"] > self.ttl_seconds:
                del self._cache[key]
                self._stats["misses"] += 1
                return None

            # Move to end (LRU)
            self._cache.move_to_end(key)
            self._stats["hits"] += 1
            return entry["response"]

        self._stats["misses"] += 1
        return None

    def add(self, prompt: str, response: str, provider: Optional[str] = None, **kwargs):
        """
        Add response to cache.

        Args:
            prompt: The prompt
            response: The response to cache
            provider: LLM provider name
            **kwargs: Additional parameters
        """
        key = self._generate_key(prompt, provider, **kwargs)

        # Add to cache
        self._cache[key] = {
            "response": response,
            "timestamp": time.time(),
            "provider": provider,
        }

        # Move to end
        self._cache.move_to_end(key)

        # Evict oldest if over capacity
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)
            self._stats["evictions"] += 1

    def clear(self):
        """Clear the cache."""
        self._cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0.0

        return {
            **self._stats,
            "size": len(self._cache),
            "hit_rate": hit_rate,
            "total_requests": total_requests,
        }

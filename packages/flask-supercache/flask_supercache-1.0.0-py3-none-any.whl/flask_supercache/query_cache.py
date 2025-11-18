"""
Query caching utilities using Python's built-in functools.lru_cache.

This provides in-memory caching with TTL support without external dependencies.
Perfect for read-heavy data that doesn't change often.

Example:
    from flask_supercache import cached_query

    @cached_query(maxsize=1000, ttl_seconds=300)
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    # First call - hits database
    user = get_user_by_id(123)

    # Second call - from cache (instant!)
    user = get_user_by_id(123)

    # After 5 minutes (300s), cache expires and fresh data is fetched
"""

import time
from functools import lru_cache, wraps
from typing import Any, Callable, Optional


def cached_query(maxsize: int = 128, ttl_seconds: int = 300):
    """
    Decorator for caching function results with TTL (time-to-live).

    This decorator combines Python's built-in LRU cache with time-based expiration.
    It's perfect for caching database queries, API calls, or expensive computations.

    Args:
        maxsize: Maximum number of cached items (LRU eviction when exceeded)
        ttl_seconds: Time-to-live in seconds (default: 5 minutes)

    Returns:
        Decorated function with caching capabilities

    Example:
        @cached_query(maxsize=500, ttl_seconds=600)
        def get_active_products(store_id):
            return Product.query.filter_by(
                store_id=store_id,
                is_active=True
            ).all()

        # Cache stats
        print(get_active_products.cache_info())

        # Manual invalidation
        get_active_products.cache_clear()

    Cache Management:
        - Automatic TTL-based expiration (time-bucket approach)
        - LRU eviction when maxsize is reached
        - Manual invalidation via cache_clear()
        - Statistics via cache_info()

    Performance:
        - O(1) lookup time
        - Minimal memory overhead
        - No external dependencies
        - Thread-safe (uses functools.lru_cache internally)
    """
    def decorator(func: Callable) -> Callable:
        # Create LRU cache with timestamp parameter for TTL
        @lru_cache(maxsize=maxsize)
        def cached_func_with_ttl(*args, _cache_timestamp: Optional[int] = None, **kwargs):
            """Internal cached function with timestamp parameter."""
            return func(*args, **kwargs)

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            """Wrapper that adds TTL functionality to LRU cache."""
            # Calculate current time bucket based on TTL
            # This ensures cache expires after TTL seconds
            current_time_bucket = int(time.time() // ttl_seconds)

            # Call cached function with time bucket
            # Cache automatically expires when time bucket changes
            return cached_func_with_ttl(
                *args,
                _cache_timestamp=current_time_bucket,
                **kwargs
            )

        # Expose cache methods for manual control
        wrapper.cache_info = cached_func_with_ttl.cache_info
        wrapper.cache_clear = cached_func_with_ttl.cache_clear

        return wrapper

    return decorator


# Alias for backwards compatibility
cached_decorator = cached_query


class CacheStats:
    """Helper class for aggregating cache statistics."""

    def __init__(self):
        self.functions = []

    def register(self, name: str, func: Callable):
        """Register a cached function for statistics tracking."""
        if hasattr(func, 'cache_info'):
            self.functions.append((name, func))

    def get_stats(self) -> dict:
        """
        Get statistics for all registered cached functions.

        Returns:
            Dict with cache stats for each function including:
            - hits: Number of cache hits
            - misses: Number of cache misses
            - size: Current cache size
            - maxsize: Maximum cache size
            - hit_rate: Hit rate percentage
        """
        stats = {}

        for func_name, func in self.functions:
            info = func.cache_info()
            total_calls = info.hits + info.misses

            stats[func_name] = {
                "hits": info.hits,
                "misses": info.misses,
                "size": info.currsize,
                "maxsize": info.maxsize,
                "hit_rate": (
                    f"{info.hits / total_calls * 100:.1f}%"
                    if total_calls > 0
                    else "0%"
                ),
                "total_calls": total_calls
            }

        return stats

    def clear_all(self):
        """Clear all registered caches."""
        for _, func in self.functions:
            func.cache_clear()

    def print_stats(self):
        """Print formatted cache statistics."""
        stats = self.get_stats()

        if not stats:
            print("No cached functions registered")
            return

        print("\n" + "=" * 80)
        print("CACHE STATISTICS")
        print("=" * 80)

        for func_name, info in stats.items():
            print(f"\n{func_name}:")
            print(f"  Hits:      {info['hits']:,}")
            print(f"  Misses:    {info['misses']:,}")
            print(f"  Hit Rate:  {info['hit_rate']}")
            print(f"  Size:      {info['size']}/{info['maxsize']}")

        print("\n" + "=" * 80 + "\n")


# Global cache stats tracker
cache_stats = CacheStats()

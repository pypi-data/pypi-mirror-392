"""
Caching backends for Flask applications.

Provides a 3-tier caching strategy:
1. Redis (preferred - fast, distributed)
2. Filesystem (fallback - no dependencies)
3. In-memory LRU (always available via query_cache module)

The setup_cache() function automatically selects the best available backend.
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def setup_cache(app, config: Optional[dict] = None):
    """
    Initialize Flask-Caching with automatic backend selection.

    This function sets up caching with the following priority:
    1. Try Redis (if available and configured)
    2. Fall back to filesystem cache (always works, no dependencies)
    3. In-memory LRU cache is always available via @cached_query

    Args:
        app: Flask application instance
        config: Optional cache configuration dict. If None, uses app.config

    Returns:
        Cache instance attached to app.cache

    Configuration Options:
        CACHE_REDIS_URL: Redis URL (e.g., 'redis://localhost:6379/0')
        CACHE_DEFAULT_TIMEOUT: Default TTL in seconds (default: 300)
        CACHE_DIR: Directory for filesystem cache (default: instance/cache)
        CACHE_THRESHOLD: Max items for filesystem cache (default: 1000)

    Example:
        from flask import Flask
        from flask_supercache import setup_cache

        app = Flask(__name__)
        app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'
        cache = setup_cache(app)

        # Use it
        @app.route('/expensive')
        def expensive_route():
            result = cache.get('key')
            if result is None:
                result = expensive_computation()
                cache.set('key', result, timeout=300)
            return result

    Production Tips:
        - Redis: Best for multi-worker deployments (shared cache)
        - Filesystem: Good for single-worker or development
        - In-memory: Use @cached_query for per-worker caching

    Backend Selection Logic:
        1. Check if CACHE_REDIS_URL is configured
        2. Test Redis connection with ping()
        3. On success: use Redis backend
        4. On failure: fall back to filesystem
        5. Log which backend is active
    """
    try:
        from flask_caching import Cache
    except ImportError:
        logger.error(
            "flask-caching not installed. "
            "Install it with: pip install flask-caching"
        )
        raise

    cache_config = config or {}

    # Try Redis first (best for production)
    redis_url = cache_config.get("CACHE_REDIS_URL") or app.config.get("CACHE_REDIS_URL")

    if redis_url:
        cache_config = _try_redis_cache(app, redis_url, cache_config)
    else:
        cache_config = _get_filesystem_cache_config(app, cache_config)

    # Initialize Flask-Caching
    cache = Cache(app, config=cache_config)
    app.cache = cache
    return cache


def _try_redis_cache(app, redis_url: str, base_config: dict) -> dict:
    """
    Attempt to connect to Redis and return Redis cache config.

    If Redis is unavailable, falls back to filesystem cache.
    """
    try:
        import redis

        # Test Redis connection (1 second timeout)
        r = redis.from_url(redis_url, socket_connect_timeout=1)
        r.ping()

        logger.info(f"✅ Cache using Redis at {redis_url}")

        return {
            "CACHE_TYPE": "redis",
            "CACHE_REDIS_URL": redis_url,
            "CACHE_DEFAULT_TIMEOUT": base_config.get(
                "CACHE_DEFAULT_TIMEOUT",
                app.config.get("CACHE_DEFAULT_TIMEOUT", 300)
            ),
            "CACHE_KEY_PREFIX": base_config.get(
                "CACHE_KEY_PREFIX",
                app.config.get("CACHE_KEY_PREFIX", "supercache_")
            ),
        }

    except ImportError:
        logger.warning(
            "Redis library not installed. "
            "Install it with: pip install redis"
        )
        return _get_filesystem_cache_config(app, base_config)

    except Exception as e:
        logger.warning(
            f"Redis unavailable ({type(e).__name__}: {e}), "
            f"falling back to filesystem cache"
        )
        return _get_filesystem_cache_config(app, base_config)


def _get_filesystem_cache_config(app, base_config: dict) -> dict:
    """
    Get filesystem cache configuration.

    This is the fallback option that always works with zero dependencies.
    """
    cache_dir = base_config.get("CACHE_DIR") or app.config.get(
        "CACHE_DIR",
        os.path.join(app.instance_path, "cache")
    )

    # Ensure cache directory exists
    os.makedirs(cache_dir, exist_ok=True)

    logger.info(f"💾 Cache using filesystem at {cache_dir}")

    return {
        "CACHE_TYPE": "filesystem",
        "CACHE_DIR": cache_dir,
        "CACHE_DEFAULT_TIMEOUT": base_config.get(
            "CACHE_DEFAULT_TIMEOUT",
            app.config.get("CACHE_DEFAULT_TIMEOUT", 300)
        ),
        "CACHE_THRESHOLD": base_config.get(
            "CACHE_THRESHOLD",
            app.config.get("CACHE_THRESHOLD", 1000)
        ),
    }


def invalidate_cache(app, pattern: Optional[str] = None):
    """
    Invalidate cache entries.

    Args:
        app: Flask application instance
        pattern: Optional pattern to match keys (Redis only).
                 If None, clears all cache.

    Example:
        # Clear all cache
        invalidate_cache(app)

        # Clear specific pattern (Redis only)
        invalidate_cache(app, pattern='user_*')

    Note:
        Pattern matching only works with Redis backend.
        Filesystem backend clears all cache when pattern is provided.
    """
    if not hasattr(app, 'cache'):
        logger.warning("No cache configured on app")
        return

    if pattern and hasattr(app.cache.cache, '_write_client'):
        # Redis backend - use pattern matching
        try:
            import redis
            r = app.cache.cache._write_client
            keys = r.keys(f"{app.config.get('CACHE_KEY_PREFIX', 'supercache_')}{pattern}")
            if keys:
                r.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache keys matching '{pattern}'")
        except Exception as e:
            logger.error(f"Error invalidating cache pattern: {e}")
    else:
        # Filesystem or no pattern - clear all
        app.cache.clear()
        logger.info("Cleared all cache")

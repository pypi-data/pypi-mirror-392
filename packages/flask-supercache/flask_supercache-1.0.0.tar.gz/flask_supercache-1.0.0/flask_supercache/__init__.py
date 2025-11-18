"""
Flask-SuperCache
================

A 3-tier caching system for Flask applications with zero external dependencies.

Features:
- LRU cache with TTL (time-to-live) support
- Redis backend with filesystem fallback
- Query caching decorator
- Cache statistics and monitoring
- Production-tested at scale

Usage:
    from flask_supercache import cached_query, setup_cache

    # Initialize in your Flask app
    setup_cache(app)

    # Cache expensive queries
    @cached_query(maxsize=1000, ttl_seconds=300)
    def get_user_by_id(user_id):
        return User.query.get(user_id)

Author: wallmarkets Team
License: MIT
"""

__version__ = "1.0.0"
__author__ = "wallmarkets Team"
__license__ = "MIT"

from .backends import setup_cache
from .query_cache import cached_query, cached_decorator

__all__ = ["cached_query", "cached_decorator", "setup_cache"]

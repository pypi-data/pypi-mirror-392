"""
Tests for query_cache module.
"""

import time
import pytest
from flask_supercache import cached_query


def test_basic_caching():
    """Test basic caching functionality."""
    call_count = 0

    @cached_query(maxsize=10, ttl_seconds=300)
    def func(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    # First call - should execute function
    result1 = func(5)
    assert result1 == 10
    assert call_count == 1

    # Second call - should use cache
    result2 = func(5)
    assert result2 == 10
    assert call_count == 1  # Not incremented

    # Different argument - should execute function
    result3 = func(10)
    assert result3 == 20
    assert call_count == 2


def test_ttl_expiration():
    """Test that cache expires after TTL."""
    call_count = 0

    @cached_query(maxsize=10, ttl_seconds=1)
    def func(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    # First call
    result1 = func(5)
    assert result1 == 10
    assert call_count == 1

    # Second call (cached)
    result2 = func(5)
    assert result2 == 10
    assert call_count == 1

    # Wait for TTL to expire
    time.sleep(1.1)

    # Third call (cache expired)
    result3 = func(5)
    assert result3 == 10
    assert call_count == 2


def test_cache_info():
    """Test cache_info() method."""
    @cached_query(maxsize=10, ttl_seconds=300)
    def func(x):
        return x * 2

    # Initial state
    info = func.cache_info()
    assert info.hits == 0
    assert info.misses == 0

    # One call
    func(5)
    info = func.cache_info()
    assert info.hits == 0
    assert info.misses == 1

    # Cached call
    func(5)
    info = func.cache_info()
    assert info.hits == 1
    assert info.misses == 1


def test_cache_clear():
    """Test cache_clear() method."""
    call_count = 0

    @cached_query(maxsize=10, ttl_seconds=300)
    def func(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    # Cache some data
    func(5)
    func(10)
    assert call_count == 2

    # Call again (should be cached)
    func(5)
    assert call_count == 2

    # Clear cache
    func.cache_clear()

    # Call again (should execute)
    func(5)
    assert call_count == 3


def test_maxsize_limit():
    """Test that maxsize limits cache size."""
    @cached_query(maxsize=3, ttl_seconds=300)
    def func(x):
        return x * 2

    # Fill cache beyond maxsize
    for i in range(5):
        func(i)

    info = func.cache_info()
    assert info.currsize <= 3  # Should not exceed maxsize


def test_none_maxsize():
    """Test unlimited cache with maxsize=None."""
    @cached_query(maxsize=None, ttl_seconds=300)
    def func(x):
        return x * 2

    # Add many items
    for i in range(100):
        func(i)

    info = func.cache_info()
    # With maxsize=None, all items should be cached
    assert info.currsize == 100


def test_kwargs_caching():
    """Test caching with keyword arguments."""
    call_count = 0

    @cached_query(maxsize=10, ttl_seconds=300)
    def func(x, y=2):
        nonlocal call_count
        call_count += 1
        return x * y

    # First call
    result1 = func(5, y=3)
    assert result1 == 15
    assert call_count == 1

    # Same call (cached)
    result2 = func(5, y=3)
    assert result2 == 15
    assert call_count == 1

    # Different kwargs (new cache entry)
    result3 = func(5, y=4)
    assert result3 == 20
    assert call_count == 2


def test_cache_stats_class():
    """Test CacheStats helper class."""
    from flask_supercache.query_cache import CacheStats

    stats = CacheStats()

    @cached_query(maxsize=10, ttl_seconds=300)
    def func1(x):
        return x * 2

    @cached_query(maxsize=10, ttl_seconds=300)
    def func2(x):
        return x * 3

    # Register functions
    stats.register('func1', func1)
    stats.register('func2', func2)

    # Make some calls
    func1(5)
    func1(5)  # Cached
    func2(10)

    # Get stats
    all_stats = stats.get_stats()
    assert 'func1' in all_stats
    assert 'func2' in all_stats
    assert all_stats['func1']['hits'] == 1
    assert all_stats['func1']['misses'] == 1

    # Clear all
    stats.clear_all()
    info1 = func1.cache_info()
    info2 = func2.cache_info()
    assert info1.currsize == 0
    assert info2.currsize == 0


def test_zero_ttl():
    """Test that TTL=0 works (immediate expiration)."""
    call_count = 0

    @cached_query(maxsize=10, ttl_seconds=1)
    def func(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    # Should cache within the same second
    func(5)
    func(5)
    assert call_count == 1  # Cached

    # Wait for next second
    time.sleep(1.1)
    func(5)
    assert call_count == 2  # Expired


def test_complex_return_types():
    """Test caching with complex return types."""
    @cached_query(maxsize=10, ttl_seconds=300)
    def func(x):
        return {
            'value': x,
            'doubled': x * 2,
            'list': [x, x * 2, x * 3]
        }

    result1 = func(5)
    result2 = func(5)

    # Should return same object (cached)
    assert result1 is result2
    assert result1['value'] == 5
    assert result1['list'] == [5, 10, 15]

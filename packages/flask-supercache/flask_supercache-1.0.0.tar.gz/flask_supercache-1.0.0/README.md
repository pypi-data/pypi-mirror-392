# Flask-SuperCache

3-tier caching for Flask applications. Adds TTL support to Python's LRU cache.

## What it does

- **LRU cache with TTL**: Combines `functools.lru_cache` with time-based expiration
- **3-tier fallback**: Redis → Filesystem → In-memory
- **No external dependencies required**: Works with just Python standard library

Built while working on [wallmarkets](https://wallmarkets.store).

## Installation

```bash
pip install flask-supercache
```

## Usage

### Basic LRU cache with TTL

```python
from flask_supercache import cached_query

@cached_query(maxsize=1000, ttl_seconds=300)
def get_user_by_id(user_id):
    return User.query.get(user_id)

# First call - hits database
user = get_user_by_id(123)

# Second call - from cache
user = get_user_by_id(123)

# After 5 minutes - cache expires, hits database again
```

### Flask-Caching integration

```python
from flask import Flask
from flask_supercache import setup_cache

app = Flask(__name__)
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'

cache = setup_cache(app)  # Auto-selects Redis or filesystem
```

## How TTL on LRU works

Standard `functools.lru_cache` doesn't support TTL. We add it using time-bucketing:

```python
# Cache key includes current time bucket
time_bucket = int(time.time() // ttl_seconds)
cache_key = (args, kwargs, time_bucket)

# When time_bucket changes, it's a cache miss
# Old entries get evicted by LRU automatically
```

No background threads, no timers. O(1) lookup.

## Cache statistics

```python
info = get_user_by_id.cache_info()
print(f"Hits: {info.hits}, Misses: {info.misses}")
print(f"Hit rate: {info.hits / (info.hits + info.misses) * 100:.1f}%")
```

## Configuration

```python
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300
app.config['CACHE_DIR'] = '/tmp/flask_cache'
```

## License

MIT

## Contributing

Pull requests welcome. Please add tests.

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

from __future__ import annotations
import hashlib
import json
import os
from functools import wraps
from typing import Any

import diskcache

from core.config import get_settings

_cache: diskcache.Cache | None = None


def _get_cache() -> diskcache.Cache:
    global _cache
    if _cache is None:
        settings = get_settings()
        cache_dir = os.path.expanduser(settings.cache_dir)
        os.makedirs(cache_dir, exist_ok=True)
        _cache = diskcache.Cache(cache_dir)
    return _cache


def _make_key(qualname: str, args: tuple, kwargs: dict) -> str:
    payload = json.dumps({"fn": qualname, "args": list(args), "kwargs": kwargs}, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()


def cached(ttl: int | None = None):
    """Decorator that caches the return value of a provider method to disk."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            effective_ttl = ttl if ttl is not None else get_settings().cache_ttl_hours * 3600
            key = _make_key(fn.__qualname__, args[1:], kwargs)
            cache = _get_cache()
            if key in cache:
                return cache[key]
            result = fn(*args, **kwargs)
            cache.set(key, result, expire=effective_ttl)
            return result
        return wrapper
    return decorator


def clear_domain_cache(domain: str) -> int:
    """Remove all cached entries containing the domain string. Returns count removed."""
    cache = _get_cache()
    removed = 0
    for key in list(cache.iterkeys()):
        try:
            if domain in str(cache.get(key, default="")):
                cache.delete(key)
                removed += 1
        except Exception:
            pass
    return removed


def cache_info() -> dict[str, Any]:
    cache = _get_cache()
    return {"size": len(cache), "directory": cache.directory}

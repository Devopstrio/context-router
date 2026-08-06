"""Unit tests for L1 Memory Cache & L2 Redis Cache."""

import time
from context_router.cache.l1_memory import L1MemoryCache
from context_router.cache.l2_redis import L2RedisCache


def test_l1_cache_set_and_get():
    cache = L1MemoryCache(default_ttl_seconds=1.0)
    cache.set("key1", {"val": 100})
    val = cache.get("key1")
    assert val == {"val": 100}

    stats = cache.get_stats()
    assert stats["hits"] == 1


def test_l1_cache_ttl_expiration():
    cache = L1MemoryCache(default_ttl_seconds=0.1)
    cache.set("key_exp", "expired_val")
    time.sleep(0.15)

    assert cache.get("key_exp") is None
    stats = cache.get_stats()
    assert stats["evictions"] == 1


def test_l2_cache_key_construction():
    cache = L2RedisCache()
    key = cache.build_key("session", "tenant-alpha", "sess-99")
    assert key == "ctx_router:session:tenant-alpha:sess-99"

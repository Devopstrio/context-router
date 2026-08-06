"""L2 Redis Cache & Key Namespaces."""

import json
from typing import Any
import redis


class L2RedisCache:
    """L2 Distributed Redis Cache for Session & Policy Pointers."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0") -> None:
        self.redis_url = redis_url
        self._fallback_store: dict[str, str] = {}
        try:
            self.client = redis.Redis.from_url(redis_url, decode_responses=True)
            self._use_redis = True
        except Exception:
            self._use_redis = False

    def build_key(self, namespace: str, tenant_id: str, identifier: str) -> str:
        """Constructs canonical Redis key namespace: e.g. ctx_router:session:{tenant_id}:{session_id}."""
        return f"ctx_router:{namespace}:{tenant_id}:{identifier}"

    def get_json(self, key: str) -> dict[str, Any] | None:
        try:
            if self._use_redis:
                data = self.client.get(key)
                if data and isinstance(data, str):
                    return json.loads(data)
            elif key in self._fallback_store:
                return json.loads(self._fallback_store[key])
        except Exception:
            pass
        return None

    def set_json(self, key: str, value: dict[str, Any], ttl_seconds: int = 300) -> None:
        try:
            serialized = json.dumps(value)
            if self._use_redis:
                self.client.setex(key, ttl_seconds, serialized)
            else:
                self._fallback_store[key] = serialized
        except Exception:
            pass

    def ping(self) -> bool:
        if not self._use_redis:
            return True
        try:
            return bool(self.client.ping())
        except Exception:
            return False

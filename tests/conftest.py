"""Pytest Configuration and Shared Test Fixtures."""

import pytest
from fastapi.testclient import TestClient

from context_router.cache.l1_memory import L1MemoryCache
from context_router.cache.l2_redis import L2RedisCache
from context_router.config.model_registry import ModelRegistry
from context_router.config.settings import ContextRouterSettings
from context_router.main import app
from context_router.resiliency.circuit_breaker import ResiliencyController
from context_router.routing.matrix import RouteDecisionMatrix
from context_router.security.jwt_auth import JWTAuthenticator


@pytest.fixture
def settings():
    return ContextRouterSettings(environment="test")


@pytest.fixture
def authenticator(settings):
    return JWTAuthenticator(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
    )


@pytest.fixture
def valid_token(authenticator):
    return authenticator.generate_test_token(tenant_id="tenant-corp-alpha")


@pytest.fixture
def model_registry():
    return ModelRegistry()


@pytest.fixture
def route_matrix(model_registry, settings):
    return RouteDecisionMatrix(model_registry, settings)


@pytest.fixture
def resiliency():
    return ResiliencyController(failure_threshold=3, recovery_timeout_seconds=5.0)


@pytest.fixture
def l1_cache():
    return L1MemoryCache(default_ttl_seconds=5.0)


@pytest.fixture
def l2_cache():
    return L2RedisCache(redis_url="redis://localhost:6379/0")


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

"""Main Application Entrypoint for Enterprise Context Router Platform."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from context_router.api.health import router as health_router
from context_router.api.routes import router as api_router
from context_router.cache.l1_memory import L1MemoryCache
from context_router.cache.l2_redis import L2RedisCache
from context_router.config.model_registry import ModelRegistry
from context_router.config.settings import ContextRouterSettings
from context_router.contracts.audit_service_client import AuditServiceClient
from context_router.contracts.context_assembler_client import ContextAssemblerClient
from context_router.contracts.memory_manager_client import MemoryManagerClient
from context_router.contracts.policy_engine_client import PolicyEngineClient
from context_router.contracts.token_budget_client import TokenBudgetClient
from context_router.observability.logging import setup_logging
from context_router.resiliency.circuit_breaker import ResiliencyController
from context_router.routing.matrix import RouteDecisionMatrix
from context_router.routing.rules import PriorityRuleEngine
from context_router.security.jwt_auth import JWTAuthenticator
from context_router.security.middleware import SecurityMiddleware
from context_router.security.rbac_abac import RBACABACEngine
from context_router.security.tenant_guard import SecurityBoundaryViolation, TenantIsolationGuard
from context_router.validation.error_handler import (
    RouterBaseException,
    router_base_exception_handler,
    security_boundary_exception_handler,
    validation_exception_handler,
)

settings = ContextRouterSettings()
setup_logging(settings.log_level)

# Instantiate Core Domain Services
authenticator = JWTAuthenticator(
    secret_key=settings.jwt_secret_key,
    algorithm=settings.jwt_algorithm,
    issuer=settings.jwt_issuer,
    audience=settings.jwt_audience,
)
tenant_guard = TenantIsolationGuard()
rbac_engine = RBACABACEngine()
model_registry = ModelRegistry()
route_matrix = RouteDecisionMatrix(model_registry, settings)
rule_engine = PriorityRuleEngine()
resiliency = ResiliencyController(
    failure_threshold=settings.circuit_breaker_failure_threshold,
    recovery_timeout_seconds=float(settings.circuit_breaker_recovery_timeout_seconds),
)
l1_cache = L1MemoryCache(default_ttl_seconds=float(settings.l1_cache_ttl_seconds))
l2_cache = L2RedisCache(redis_url=settings.redis_primary_url)

# Contract Clients
memory_client = MemoryManagerClient(settings.memory_manager_host, settings.memory_manager_port)
budget_client = TokenBudgetClient(settings.token_budget_host, settings.token_budget_port)
policy_client = PolicyEngineClient(settings.policy_engine_host, settings.policy_engine_port)
assembler_client = ContextAssemblerClient(settings.context_assembler_host, settings.context_assembler_port)
audit_client = AuditServiceClient(settings.audit_service_host, settings.audit_service_port)


@asynccontextmanager
async def lifespan(app_instance: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager."""
    yield


app = FastAPI(
    title="Context Router API",
    description="Enterprise Context Orchestration, Routing, and Dispatch Service.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Attach components to app.state
app.state.settings = settings
app.state.authenticator = authenticator
app.state.tenant_guard = tenant_guard
app.state.rbac_engine = rbac_engine
app.state.model_registry = model_registry
app.state.route_matrix = route_matrix
app.state.rule_engine = rule_engine
app.state.resiliency = resiliency
app.state.l1_cache = l1_cache
app.state.l2_cache = l2_cache
app.state.memory_client = memory_client
app.state.budget_client = budget_client
app.state.policy_client = policy_client
app.state.assembler_client = assembler_client
app.state.audit_client = audit_client

# Exception Handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
app.add_exception_handler(SecurityBoundaryViolation, security_boundary_exception_handler)  # type: ignore
app.add_exception_handler(RouterBaseException, router_base_exception_handler)  # type: ignore

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SecurityMiddleware,
    authenticator=authenticator,
    tenant_guard=tenant_guard,
)

# Routers
app.include_router(health_router)
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(
        "context_router.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )  # nosec B104

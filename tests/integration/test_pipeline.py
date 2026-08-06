"""Integration tests for context routing decision pipeline."""

from context_router.config.model_registry import ModelRegistry
from context_router.config.settings import ContextRouterSettings
from context_router.routing.matrix import RouteDecisionMatrix
from context_router.security.jwt_auth import JWTAuthenticator
from context_router.security.tenant_guard import TenantIsolationGuard
from context_router.validation.schemas import RequestContext, RouteRequest


def test_full_routing_pipeline(settings, model_registry, route_matrix):
    authenticator = JWTAuthenticator()
    token = authenticator.generate_test_token(tenant_id="tenant-corp-alpha")
    claims = authenticator.decode_and_validate(token)

    guard = TenantIsolationGuard()
    guard.verify_tenant_boundary("tenant-corp-alpha", claims)

    req = RouteRequest(
        tenant_id="tenant-corp-alpha",
        session_id="sess-integration-1",
        request_context=RequestContext(user_query="Customer support inquiry", latency_priority="ultra-low"),
    )

    circuit_statuses = {m.model_id: True for m in model_registry.get_all_active_models()}
    best_model, fallbacks = route_matrix.evaluate_route(
        req,
        total_tokens=1500,
        circuit_statuses=circuit_statuses,
        tenant_allowed_regions=claims.data_residency,
        override_weights={"w_l": 0.8, "w_c": 0.1, "w_h": 0.05, "w_a": 0.05},
    )

    assert best_model is not None
    assert best_model.model_id in ("gpt-4o-mini", "llama-3-70b", "gpt-4o", "claude-3-5-sonnet")

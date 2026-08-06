"""REST API Routes for Context Orchestration & Model Routing Control Plane."""

import time
import uuid
from typing import Any, cast
from fastapi import APIRouter, Header, HTTPException, Request

from context_router.config.model_registry import ModelProfile
from context_router.observability.metrics import (
    FALLBACK_TOTAL,
    LATENCY_SECONDS,
    REQUESTS_TOTAL,
)
from context_router.routing.matrix import RouteDecisionMatrix
from context_router.routing.rules import PriorityRuleEngine
from context_router.routing.state_machine import RequestState, RequestStateMachine
from context_router.security.jwt_auth import JWTClaims
from context_router.security.rbac_abac import RBACABACEngine
from context_router.security.tenant_guard import SecurityBoundaryViolation, TenantIsolationGuard
from context_router.validation.schemas import (
    BatchRouteRequest,
    BatchRouteResponse,
    ExecutionPlan,
    RouteRequest,
    RouteResponse,
    RouteTelemetry,
    TargetModel,
)

router = APIRouter()


def _get_authenticated_claims(request: Request, authorization: str | None) -> JWTClaims:
    """Helper to extract and validate JWTClaims from request or authorization header."""
    claims = getattr(request.state, "claims", None)
    if not claims:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="ERR-2001: Missing or invalid Authorization Bearer header",
            )
        token = authorization.split(" ", 1)[1]
        authenticator = request.app.state.authenticator
        try:
            claims = authenticator.decode_and_validate(token)
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"ERR-2001: {str(e)}") from e
    return cast(JWTClaims, claims)


def _process_single_route(
    request_obj: RouteRequest,
    headers: dict[str, str],
    req: Request,
    claims: JWTClaims,
    x_tenant_id: str,
) -> RouteResponse:
    start_time = time.time()
    route_id = f"route-{uuid.uuid4().hex[:12]}"
    state_machine = RequestStateMachine(route_id)

    # 1. Tenant boundary check
    tenant_guard: TenantIsolationGuard = req.app.state.tenant_guard
    tenant_guard.verify_tenant_boundary(x_tenant_id, claims)
    state_machine.transition_to(RequestState.AUTHENTICATED)

    # 2. RBAC & ABAC Auth check
    rbac_engine: RBACABACEngine = req.app.state.rbac_engine
    rbac_engine.authorize_route_request(
        claims,
        {"data_classification": request_obj.request_context.data_classification},
    )

    # 3. L1/L2 Cache lookup
    cache_key = f"route:{x_tenant_id}:{request_obj.session_id}:{hash(request_obj.request_context.user_query)}"
    l1_cache = req.app.state.l1_cache
    cached_res = l1_cache.get(cache_key)
    if cached_res:
        state_machine.transition_to(RequestState.ROUTE_DISPATCHED, {"cache": "hit"})
        return cast(RouteResponse, cached_res)

    # 4. Fetch Memory State Pointer
    memory_client = req.app.state.memory_client
    memory_state = memory_client.get_session_state_pointer(x_tenant_id, request_obj.session_id)
    state_machine.transition_to(RequestState.SESSION_RESOLVED)

    # 5. Evaluate Token Budget
    budget_client = req.app.state.budget_client
    total_tokens = budget_client.estimate_payload_tokens(
        request_obj.request_context.user_query, memory_state.estimated_history_tokens
    )

    # 6. Evaluate Policy Constraints
    policy_client = req.app.state.policy_client
    policy_res = policy_client.evaluate_tenant_policy(
        x_tenant_id, request_obj.request_context.data_classification
    )
    tenant_guard.enforce_data_residency(claims, policy_res.restricted_regions)

    # 7. Check Header Rules & Overrides
    rule_engine: PriorityRuleEngine = req.app.state.rule_engine
    override_weights, force_model_id = rule_engine.resolve_header_overrides(headers)

    matrix: RouteDecisionMatrix = req.app.state.route_matrix
    resiliency = req.app.state.resiliency

    # Get circuit statuses for all models
    model_registry = req.app.state.model_registry
    circuit_statuses = {
        m.model_id: resiliency.is_healthy(m.model_id)
        for m in model_registry.get_all_active_models()
    }

    best_model: ModelProfile
    fallback_models: list[ModelProfile]

    if force_model_id:
        forced = model_registry.get_model(force_model_id)
        if forced:
            best_model = forced
            fallback_models = []
        else:
            best_model, fallback_models = matrix.evaluate_route(
                request_obj, total_tokens, circuit_statuses, policy_res.restricted_regions, override_weights
            )
    else:
        best_model, fallback_models = matrix.evaluate_route(
            request_obj, total_tokens, circuit_statuses, policy_res.restricted_regions, override_weights
        )

    state_machine.transition_to(RequestState.ROUTE_EVALUATED, {"selected_model": best_model.model_id})

    # 8. Check primary model health & trigger fallback state if needed
    if not resiliency.is_healthy(best_model.model_id):
        if fallback_models:
            state_machine.transition_to(RequestState.FAILED_OVER, {"primary": best_model.model_id})
            FALLBACK_TOTAL.labels(primary_target=best_model.model_id, fallback_target=fallback_models[0].model_id).inc()
            best_model = fallback_models[0]
            fallback_models = fallback_models[1:]
        else:
            raise HTTPException(
                status_code=503,
                detail="ERR-5001: All target models in provider matrix are circuit-broken.",
            )

    # 9. Dispatch to context-assembler
    assembler_client = req.app.state.assembler_client
    assembler_client.dispatch_assembly_job(
        route_id=route_id,
        tenant_id=x_tenant_id,
        session_id=request_obj.session_id,
        provider=best_model.provider,
        model_id=best_model.model_id,
        endpoint=best_model.endpoint,
    )
    state_machine.transition_to(RequestState.ROUTE_DISPATCHED)

    # 10. Compute telemetry & publish audit event
    elapsed_ms = round((time.time() - start_time) * 1000, 2)
    estimated_cost = round((total_tokens / 1000.0) * best_model.cost_per_1k_input_tokens, 6)

    audit_client = req.app.state.audit_client
    audit_client.publish_route_event(
        route_id=route_id,
        tenant_id=x_tenant_id,
        session_id=request_obj.session_id,
        model_id=best_model.model_id,
        latency_ms=elapsed_ms,
        cost_usd=estimated_cost,
    )
    state_machine.transition_to(RequestState.AUDITED)

    response = RouteResponse(
        route_id=route_id,
        target_model=TargetModel(
            provider=best_model.provider,
            model_id=best_model.model_id,
            endpoint=best_model.endpoint,
        ),
        execution_plan=ExecutionPlan(
            session_lookup_required=True,
            max_token_budget=best_model.context_window,
            fallback_chain=[m.model_id for m in fallback_models],
        ),
        telemetry=RouteTelemetry(
            routing_time_ms=elapsed_ms,
            estimated_cost_usd=estimated_cost,
        ),
    )

    # Cache response in L1
    l1_cache.set(cache_key, response, ttl_seconds=5.0)

    # Metrics
    REQUESTS_TOTAL.labels(tenant_id=x_tenant_id, status="200").inc()
    LATENCY_SECONDS.labels(target_model=best_model.model_id, provider=best_model.provider).observe(elapsed_ms / 1000.0)

    return response


@router.post("/v1/context/route", response_model=RouteResponse)
def evaluate_and_route(
    request_obj: RouteRequest,
    req: Request,
    authorization: str | None = Header(default=None),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
    x_correlation_id: str | None = Header(default=None, alias="X-Correlation-ID"),
    x_routing_preference: str | None = Header(default=None, alias="X-Routing-Preference"),
    x_routing_force_model: str | None = Header(default=None, alias="X-Routing-Force-Model"),
) -> RouteResponse:
    """Evaluates ingress payload, calculates optimal model target, and dispatches context execution plan."""
    claims = _get_authenticated_claims(req, authorization)

    tenant_id = x_tenant_id or request_obj.tenant_id
    if not tenant_id:
        raise HTTPException(status_code=400, detail="ERR-1001: Missing X-Tenant-ID header or tenant_id field")

    headers = {
        "x-routing-preference": x_routing_preference or "",
        "x-routing-force-model": x_routing_force_model or "",
    }

    try:
        return _process_single_route(request_obj, headers, req, claims, tenant_id)
    except SecurityBoundaryViolation as e:
        REQUESTS_TOTAL.labels(tenant_id=tenant_id, status="403").inc()
        raise HTTPException(status_code=403, detail=f"ERR-4001: {e.message}") from e


@router.post("/v1/context/route/batch", response_model=BatchRouteResponse)
def batch_evaluate_and_route(
    batch_req: BatchRouteRequest,
    req: Request,
    authorization: str | None = Header(default=None),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
) -> BatchRouteResponse:
    """Processes up to 100 route evaluations in parallel for multi-agent workflows."""
    start = time.time()
    claims = _get_authenticated_claims(req, authorization)

    results: list[RouteResponse] = []
    headers: dict[str, str] = {}

    for single_req in batch_req.requests:
        tenant_id = x_tenant_id or single_req.tenant_id
        res = _process_single_route(single_req, headers, req, claims, tenant_id)
        results.append(res)

    total_time = round((time.time() - start) * 1000, 2)
    return BatchRouteResponse(
        results=results,
        total_processed=len(results),
        total_time_ms=total_time,
    )


@router.post("/v1/registry/models", response_model=ModelProfile)
def register_model_profile(
    profile: ModelProfile,
    req: Request,
    authorization: str | None = Header(default=None),
) -> ModelProfile:
    """Registers or updates model target profiles in active scoring matrix (Admin)."""
    claims = _get_authenticated_claims(req, authorization)
    rbac: RBACABACEngine = req.app.state.rbac_engine
    try:
        rbac.authorize_admin_request(claims)
    except SecurityBoundaryViolation as e:
        raise HTTPException(status_code=403, detail=f"ERR-4001: {e.message}") from e

    registry: ModelProfile = req.app.state.model_registry
    registry.register_model(profile)  # type: ignore
    return profile


@router.get("/v1/registry/models", response_model=None)
def list_model_profiles(req: Request) -> list[dict[str, Any]]:
    """Lists registered model capability profiles."""
    registry = req.app.state.model_registry
    return [m.model_dump() for m in registry.list_models()]

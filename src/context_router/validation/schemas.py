"""OpenAPI 3.1 Pydantic Validation Schemas."""

from typing import Literal

from pydantic import BaseModel, Field


class RequestContext(BaseModel):
    """Payload request context."""

    user_query: str
    latency_priority: Literal["ultra-low", "balanced", "high-accuracy"] = "balanced"
    data_classification: str = "PUBLIC"


class RouteConstraints(BaseModel):
    """Optional routing budget and provider constraints."""

    max_cost_per_1k_tokens: float | None = None
    allowed_providers: list[str] | None = None


class RouteRequest(BaseModel):
    """Ingress context route evaluation payload."""

    tenant_id: str = Field(..., example="tenant-corp-alpha")
    session_id: str = Field(..., example="sess-9923-bf34-9981")
    agent_id: str | None = Field(default=None, example="agent-customer-support")
    request_context: RequestContext
    constraints: RouteConstraints | None = None


class TargetModel(BaseModel):
    """Selected target model endpoint details."""

    provider: str
    model_id: str
    endpoint: str


class ExecutionPlan(BaseModel):
    """Downstream execution assembly plan."""

    session_lookup_required: bool = True
    max_token_budget: int = 4096
    fallback_chain: list[str] = Field(default_factory=list)


class RouteTelemetry(BaseModel):
    """Route decision telemetry and SLA metrics."""

    routing_time_ms: float
    estimated_cost_usd: float


class RouteResponse(BaseModel):
    """Egress context route decision response."""

    route_id: str
    target_model: TargetModel
    execution_plan: ExecutionPlan
    telemetry: RouteTelemetry


class BatchRouteRequest(BaseModel):
    """Batch route evaluation request (up to 100 items)."""

    requests: list[RouteRequest] = Field(..., max_length=100)


class BatchRouteResponse(BaseModel):
    """Batch route evaluation response."""

    results: list[RouteResponse]
    total_processed: int
    total_time_ms: float


class ProblemDetails(BaseModel):
    """RFC 7807 Problem Details Standard Error Schema."""

    type: str
    title: str
    status: int
    detail: str
    instance: str
    code: str
    timestamp: str

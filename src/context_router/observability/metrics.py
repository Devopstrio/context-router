"""Prometheus Metrics Declarations and Telemetry Collection."""

from prometheus_client import REGISTRY, Counter, Gauge, Histogram


# Avoid duplicate registration when reloading
def get_or_create_counter(name: str, documentation: str, labelnames: list[str]) -> Counter:
    try:
        return Counter(name, documentation, labelnames)
    except ValueError:
        return REGISTRY._names_to_collectors[name]  # type: ignore


def get_or_create_histogram(name: str, documentation: str, labelnames: list[str]) -> Histogram:
    try:
        return Histogram(name, documentation, labelnames)
    except ValueError:
        return REGISTRY._names_to_collectors[name]  # type: ignore


def get_or_create_gauge(name: str, documentation: str, labelnames: list[str]) -> Gauge:
    try:
        return Gauge(name, documentation, labelnames)
    except ValueError:
        return REGISTRY._names_to_collectors[name]  # type: ignore


REQUESTS_TOTAL = get_or_create_counter(
    "context_router_requests_total",
    "Total incoming context route requests",
    ["tenant_id", "status"],
)

LATENCY_SECONDS = get_or_create_histogram(
    "context_router_latency_seconds",
    "Route decision execution latency",
    ["target_model", "provider"],
)

CIRCUIT_BREAKER_STATE = get_or_create_gauge(
    "context_router_circuit_breaker_state",
    "Circuit breaker status (0=Closed/Healthy, 1=Open/Unhealthy)",
    ["provider", "model_id"],
)

FALLBACK_TOTAL = get_or_create_counter(
    "context_router_fallback_total",
    "Count of failover routes triggered",
    ["primary_target", "fallback_target"],
)

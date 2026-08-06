"""Observability package."""

from context_router.observability.logging import get_logger, setup_logging
from context_router.observability.metrics import (
    CIRCUIT_BREAKER_STATE,
    FALLBACK_TOTAL,
    LATENCY_SECONDS,
    REQUESTS_TOTAL,
)
from context_router.observability.tracing import get_tracer

__all__ = [
    "setup_logging",
    "get_logger",
    "get_tracer",
    "REQUESTS_TOTAL",
    "LATENCY_SECONDS",
    "CIRCUIT_BREAKER_STATE",
    "FALLBACK_TOTAL",
]

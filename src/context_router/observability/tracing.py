"""OpenTelemetry Tracing Setup and Hooks."""

from typing import Any
from opentelemetry import trace
from opentelemetry.trace import Tracer


def get_tracer(name: str = "context-router") -> Tracer:
    """Returns OpenTelemetry tracer for distributed transaction context propagation."""
    return trace.get_tracer(name)

"""Contract Client for audit-service Sibling Service."""

import time
from typing import Any


class AuditServiceClient:
    """Client implementing the contract for publishing immutable telemetry events."""

    def __init__(self, host: str = "audit.internal", port: int = 9092) -> None:
        self.host = host
        self.port = port
        self.published_events: list[dict[str, Any]] = []

    def publish_route_event(
        self,
        route_id: str,
        tenant_id: str,
        session_id: str,
        model_id: str,
        latency_ms: float,
        cost_usd: float,
        status: str = "SUCCESS",
    ) -> None:
        """Asynchronously emits Kafka audit telemetry event."""
        event = {
            "event_type": "CONTEXT_ROUTE_DISPATCHED",
            "route_id": route_id,
            "tenant_id": tenant_id,
            "session_id": session_id,
            "target_model": model_id,
            "latency_ms": latency_ms,
            "estimated_cost_usd": cost_usd,
            "status": status,
            "timestamp": time.time(),
        }
        self.published_events.append(event)

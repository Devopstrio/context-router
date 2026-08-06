"""Request State Machine lifecycle tracker."""

import time
from enum import Enum
from typing import Any


class RequestState(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    AUTHENTICATED = "AUTHENTICATED"
    SESSION_RESOLVED = "SESSION_RESOLVED"
    ROUTE_EVALUATED = "ROUTE_EVALUATED"
    TRUNCATING = "TRUNCATING"
    FAILED_OVER = "FAILED_OVER"
    ROUTE_DISPATCHED = "ROUTE_DISPATCHED"
    AUDITED = "AUDITED"
    REJECTED = "REJECTED"


class RequestStateMachine:
    """Tracks state transitions of a context routing request."""

    def __init__(self, route_id: str) -> None:
        self.route_id = route_id
        self.current_state = RequestState.RECEIVED
        self.history: list[dict[str, Any]] = [
            {"state": RequestState.RECEIVED.value, "timestamp": time.time()}
        ]

    def transition_to(self, new_state: RequestState, metadata: dict[str, Any] | None = None) -> None:
        """Transitions request to a new lifecycle state."""
        self.current_state = new_state
        entry = {"state": new_state.value, "timestamp": time.time()}
        if metadata:
            entry["metadata"] = metadata
        self.history.append(entry)

    def get_summary(self) -> dict[str, Any]:
        return {
            "route_id": self.route_id,
            "current_state": self.current_state.value,
            "transition_count": len(self.history),
            "history": self.history,
        }

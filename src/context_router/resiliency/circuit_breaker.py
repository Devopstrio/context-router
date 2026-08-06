"""Resiliency Controller & Circuit Breaker."""

import time
from enum import Enum


class BreakerState(str, Enum):
    CLOSED = "CLOSED"  # Healthy
    OPEN = "OPEN"      # Tripped / Unhealthy
    HALF_OPEN = "HALF_OPEN"  # Testing recovery


class ResiliencyController:
    """Manages real-time provider circuit breaker states and failover tracking."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout_seconds: float = 30.0,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self._states: dict[str, BreakerState] = {}
        self._failure_counts: dict[str, int] = {}
        self._last_state_change: dict[str, float] = {}

    def is_healthy(self, model_id: str) -> bool:
        """Returns True if circuit is CLOSED or HALF_OPEN (healthy enough to attempt)."""
        state = self.get_circuit_status(model_id)
        return state != BreakerState.OPEN

    def get_circuit_status(self, model_id: str) -> BreakerState:
        state = self._states.get(model_id, BreakerState.CLOSED)
        if state == BreakerState.OPEN:
            last_change = self._last_state_change.get(model_id, 0.0)
            if time.time() - last_change > self.recovery_timeout_seconds:
                # Transition to HALF_OPEN to test recovery
                self._states[model_id] = BreakerState.HALF_OPEN
                self._last_state_change[model_id] = time.time()
                return BreakerState.HALF_OPEN
        return state

    def record_success(self, model_id: str) -> None:
        """Records successful execution, resetting failure counters."""
        self._failure_counts[model_id] = 0
        if self._states.get(model_id) in (BreakerState.OPEN, BreakerState.HALF_OPEN):
            self._states[model_id] = BreakerState.CLOSED
            self._last_state_change[model_id] = time.time()

    def record_failure(self, model_id: str) -> None:
        """Records a provider failure (e.g. 5xx or timeout), tripping circuit if threshold reached."""
        count = self._failure_counts.get(model_id, 0) + 1
        self._failure_counts[model_id] = count
        if count >= self.failure_threshold:
            self.trip_circuit(model_id)

    def trip_circuit(self, model_id: str) -> None:
        """Forcefully trips a model target circuit to OPEN."""
        self._states[model_id] = BreakerState.OPEN
        self._last_state_change[model_id] = time.time()

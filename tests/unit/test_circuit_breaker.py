"""Unit tests for ResiliencyController and CircuitBreaker."""

from context_router.resiliency.circuit_breaker import BreakerState, ResiliencyController


def test_circuit_breaker_initial_state_closed():
    resiliency = ResiliencyController(failure_threshold=3)
    assert resiliency.get_circuit_status("model-a") == BreakerState.CLOSED
    assert resiliency.is_healthy("model-a") is True


def test_circuit_breaker_trips_after_failures():
    resiliency = ResiliencyController(failure_threshold=3)
    resiliency.record_failure("model-a")
    resiliency.record_failure("model-a")
    assert resiliency.is_healthy("model-a") is True

    resiliency.record_failure("model-a")  # 3rd failure
    assert resiliency.get_circuit_status("model-a") == BreakerState.OPEN
    assert resiliency.is_healthy("model-a") is False


def test_circuit_breaker_recovery_to_half_open():
    resiliency = ResiliencyController(failure_threshold=2, recovery_timeout_seconds=0.1)
    resiliency.record_failure("model-b")
    resiliency.record_failure("model-b")
    assert resiliency.get_circuit_status("model-b") == BreakerState.OPEN

    import time
    time.sleep(0.15)

    assert resiliency.get_circuit_status("model-b") == BreakerState.HALF_OPEN
    assert resiliency.is_healthy("model-b") is True

    resiliency.record_success("model-b")
    assert resiliency.get_circuit_status("model-b") == BreakerState.CLOSED

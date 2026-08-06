"""Unit tests for RequestStateMachine lifecycle tracking."""

from context_router.routing.state_machine import RequestState, RequestStateMachine


def test_state_machine_transitions():
    sm = RequestStateMachine("route-123")
    assert sm.current_state == RequestState.RECEIVED

    sm.transition_to(RequestState.AUTHENTICATED)
    sm.transition_to(RequestState.SESSION_RESOLVED)
    sm.transition_to(RequestState.ROUTE_DISPATCHED)

    assert sm.current_state == RequestState.ROUTE_DISPATCHED
    summary = sm.get_summary()
    assert summary["transition_count"] == 4
    assert summary["route_id"] == "route-123"

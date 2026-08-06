"""Unit tests for RouteDecisionMatrix mathematical scoring equation."""

import pytest

from context_router.config.model_registry import ModelProfile
from context_router.validation.schemas import RequestContext, RouteRequest


def test_score_model_calculation(route_matrix):
    model = ModelProfile(
        model_id="test-model",
        provider="test-provider",
        endpoint="https://test.internal",
        context_window=100000,
        cost_per_1k_input_tokens=0.001,
        historical_p99_latency_ms=5.0,
        supported_regions=["EU", "US"],
    )
    score = route_matrix.score_model(
        model=model,
        max_cost=0.01,
        max_latency=10.0,
        circuit_health=1.0,
        tenant_affinity=1.0,
        weight_cost=0.3,
        weight_latency=0.3,
        weight_health=0.2,
        weight_affinity=0.2,
    )
    assert 0.0 <= score <= 1.0
    assert score > 0.5


def test_evaluate_route_selection(route_matrix):
    req = RouteRequest(
        tenant_id="tenant-corp-alpha",
        session_id="sess-100",
        request_context=RequestContext(user_query="Hello AI model", latency_priority="balanced"),
    )
    circuit_statuses = {
        "gpt-4o": True,
        "gpt-4o-mini": True,
        "claude-3-5-sonnet": True,
        "llama-3-70b": True,
    }
    best, fallbacks = route_matrix.evaluate_route(
        req, total_tokens=2000, circuit_statuses=circuit_statuses, tenant_allowed_regions=["EU", "US"]
    )
    assert best is not None
    assert isinstance(fallbacks, list)
    assert len(fallbacks) >= 1


def test_evaluate_route_no_eligible_models_raises_value_error(route_matrix):
    req = RouteRequest(
        tenant_id="tenant-corp-alpha",
        session_id="sess-100",
        request_context=RequestContext(user_query="Hello AI model"),
    )
    # Circuit break everything
    circuit_statuses = {
        "gpt-4o": False,
        "gpt-4o-mini": False,
        "claude-3-5-sonnet": False,
        "llama-3-70b": False,
    }
    with pytest.raises(ValueError):
        route_matrix.evaluate_route(
            req, total_tokens=2000, circuit_statuses=circuit_statuses, tenant_allowed_regions=["EU"]
        )

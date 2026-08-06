"""API Endpoint Functional & Edge Case Test Suite."""


def test_health_live_endpoint(client):
    res = client.get("/health/live")
    assert res.status_code == 200
    assert res.json()["status"] == "UP"


def test_health_ready_endpoint(client):
    res = client.get("/health/ready")
    assert res.status_code == 200
    assert res.json()["status"] == "UP"


def test_health_startup_endpoint(client):
    res = client.get("/health/startup")
    assert res.status_code == 200
    assert res.json()["status"] == "UP"


def test_route_context_unauthorized_returns_401(client):
    res = client.post(
        "/v1/context/route",
        json={
            "tenant_id": "tenant-corp-alpha",
            "session_id": "sess-9923",
            "request_context": {"user_query": "hello"},
        },
    )
    assert res.status_code == 401
    assert "ERR-2001" in res.json()["detail"]


def test_route_context_tenant_mismatch_returns_403(client, valid_token):
    res = client.post(
        "/v1/context/route",
        headers={
            "Authorization": f"Bearer {valid_token}",
            "X-Tenant-ID": "tenant-mismatch-id",
        },
        json={
            "tenant_id": "tenant-mismatch-id",
            "session_id": "sess-9923",
            "request_context": {"user_query": "hello"},
        },
    )
    assert res.status_code == 403
    assert "ERR-4001" in res.json()["detail"]


def test_route_context_success(client, valid_token):
    res = client.post(
        "/v1/context/route",
        headers={
            "Authorization": f"Bearer {valid_token}",
            "X-Tenant-ID": "tenant-corp-alpha",
            "X-Correlation-ID": "corr-123-abc",
        },
        json={
            "tenant_id": "tenant-corp-alpha",
            "session_id": "sess-9923-bf34-9981",
            "agent_id": "agent-support",
            "request_context": {
                "user_query": "How do I reset my credentials?",
                "latency_priority": "balanced",
            },
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "route_id" in data
    assert "target_model" in data
    assert "execution_plan" in data
    assert "telemetry" in data
    assert data["target_model"]["provider"] is not None


def test_batch_route_context_success(client, valid_token):
    res = client.post(
        "/v1/context/route/batch",
        headers={
            "Authorization": f"Bearer {valid_token}",
            "X-Tenant-ID": "tenant-corp-alpha",
        },
        json={
            "requests": [
                {
                    "tenant_id": "tenant-corp-alpha",
                    "session_id": "sess-b1",
                    "request_context": {"user_query": "Query 1"},
                },
                {
                    "tenant_id": "tenant-corp-alpha",
                    "session_id": "sess-b2",
                    "request_context": {"user_query": "Query 2"},
                },
            ]
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_processed"] == 2
    assert len(data["results"]) == 2


def test_list_and_register_models(client, authenticator):
    # List models
    res = client.get("/v1/registry/models")
    assert res.status_code == 200
    assert len(res.json()) > 0

    admin_token = authenticator.generate_test_token(
        tenant_id="tenant-corp-alpha",
        roles=["admin:models", "context:route"],
    )

    # Register new model profile
    res_reg = client.post(
        "/v1/registry/models",
        headers={
            "Authorization": f"Bearer {admin_token}",
        },
        json={
            "model_id": "gpt-4o-new",
            "provider": "azure_openai",
            "endpoint": "https://test.endpoint",
            "context_window": 128000,
            "cost_per_1k_input_tokens": 0.002,
            "historical_p99_latency_ms": 7.0,
            "supported_regions": ["EU", "US"],
        },
    )
    assert res_reg.status_code == 200
    assert res_reg.json()["model_id"] == "gpt-4o-new"

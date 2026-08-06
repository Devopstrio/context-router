# Prometheus Metrics Reference

| Metric Name | Type | Labels | Description |
| :--- | :--- | :--- | :--- |
| `context_router_requests_total` | Counter | `tenant_id`, `status` | Total incoming route requests |
| `context_router_latency_seconds` | Histogram | `target_model`, `provider` | Route decision execution latency |
| `context_router_circuit_breaker_state` | Gauge | `provider`, `model_id` | Circuit breaker status (0=Closed, 1=Open) |
| `context_router_fallback_total` | Counter | `primary_target`, `fallback_target` | Count of failover routes triggered |
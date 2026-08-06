# Environment Variable Declarations

| Environment Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | String | `production` | Deployment stage |
| `PORT` | Integer | `8080` | Application HTTP port |
| `REDIS_PRIMARY_URL` | String | `redis://...` | L2 Redis connection string |
| `POLICY_ENGINE_GRPC_HOST` | String | `policy.internal` | Policy engine gRPC endpoint |
| `MAX_ROUTING_TIMEOUT_MS` | Integer | `15` | Hard deadline for route calculations |
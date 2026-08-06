# Request State Machine Specification

Every context routing request progresses through a deterministic state transition lifecycle.

```mermaid
stateDiagram-v2
    [*] --> RECEIVED
    RECEIVED --> VALIDATED : Ingress Validation Pass
    RECEIVED --> REJECTED : Schema Failure (400)
    
    VALIDATED --> AUTHENTICATED : Tenant & JWT Verified
    VALIDATED --> REJECTED : Auth / ABAC Failure (401/403)
    
    AUTHENTICATED --> SESSION_RESOLVED : Memory State Fetched
    SESSION_RESOLVED --> ROUTE_EVALUATED : Routing Matrix Executed
    
    ROUTE_EVALUATED --> TRUNCATING : Token Mass > Target Limit
    TRUNCATING --> ROUTE_EVALUATED : Token Budget Adjusted
    
    ROUTE_EVALUATED --> ROUTE_DISPATCHED : Execution Plan Emitted
    ROUTE_DISPATCHED --> AUDITED : Kafka Audit Log ACK
    
    ROUTE_EVALUATED --> FAILED_OVER : Primary Model Unhealthy
    FAILED_OVER --> ROUTE_DISPATCHED : Backup Route Selected
    
    AUDITED --> [*]
    REJECTED --> [*]
```

## State Definitions
* **`RECEIVED`**: Ingress payload accepted at API gateway layer.
* **`VALIDATED`**: Structural JSON schema and input constraints verified.
* **`AUTHENTICATED`**: JWT token claims and tenant isolation boundaries validated.
* **`SESSION_RESOLVED`**: Conversation history pointers loaded from `memory-manager`.
* **`ROUTE_EVALUATED`**: Decision algorithm selected target model and fallback hierarchy.
* **`TRUNCATING`**: Request delegated to `token-budget-optimizer` due to token overflow.
* **`FAILED_OVER`**: Circuit breaker triggered; fallback model target selected.
* **`ROUTE_DISPATCHED`**: Plan sent to `context-assembler`.
* **`AUDITED`**: Telemetry event published to `audit-service`.
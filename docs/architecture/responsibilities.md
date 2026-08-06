# Responsibilities & System Boundaries

To maintain low latency and architectural modularity, `context-router` strictly enforces system boundaries.

## In-Scope Responsibilities
* **Request Schema Validation:** Ingress payload validation and parameter sanitization.
* **Tenant Isolation:** Enforcing tenant cryptographic boundaries and ABAC policy checks.
* **Model Capability Matching:** Dynamic selection of target model providers based on context window size, model tier, and real-time SLA metrics.
* **Session Lookup Routing:** Interfacing with `memory-manager` to locate active state pointers.
* **Dynamic Failover:** Rerouting requests upon provider error, HTTP 429 rate-limiting, or circuit-breaker trips.
* **Route Dispatching:** Handing off structured execution plans to `context-assembler`.

## Out-of-Scope Responsibilities (Strictly Delegated)
* **Physical Prompt Assembly:** Jinja/Mustache template rendering and token formatting is delegated to `context-assembler`.
* **Raw State Storage:** Storing vectors, message histories, or embeddings is delegated to `memory-manager`.
* **Vector Similarity Search:** Executing dense vector KNN searches is delegated to `retrieval-integrator`.
* **Heavy Tokenization Logic:** Byte Pair Encoding (BPE) calculations are delegated to `token-budget-optimizer`.
* **Compliance Policy Definition:** Rules are authored in `policy-engine` and read by `context-router`.
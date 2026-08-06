# Dynamic Routing Rules & Policy Engine Integration

## 1. Rule Types
`context-router` enforces three distinct layers of routing rules:

1. **System Governance Rules:** Non-bypassable platform limits (e.g., global max token limit = 2M tokens).
2. **Tenant Policy Rules:** Compliance boundaries defined per tenant (e.g., GDPR EU-only models).
3. **Request SLA Flags:** Ephemeral client preferences passed via header or request context.

## 2. Priority Rule Matrix

| Priority Rank | Rule Name | Evaluator | Behavior on Violation |
| :--- | :--- | :--- | :--- |
| **1 (Highest)** | `TenantDataResidency` | `TenantIsolationGuard` | Immediate `403 Forbidden` |
| **2** | `CircuitBreakerStatus` | `ResiliencyController` | Evict model target from scoring matrix |
| **3** | `ContextWindowBound` | `TokenMassCalculator` | Trigger `token-budget-optimizer` truncation |
| **4** | `MaxCostThreshold` | `RouteDecisionMatrix` | Route to lower-cost SLM alternative |
| **5 (Lowest)** | `LatencyPreference` | `RouteDecisionMatrix` | Favor model target with lowest P99 metric |

## 3. Dynamic Rule Overrides via Request Headers
Clients with appropriate scope permissions can pass operational override hints:
* `X-Routing-Preference: ultra-low-latency` $\rightarrow$ Sets $w_l = 0.8, w_c = 0.1$.
* `X-Routing-Preference: cost-optimized` $\rightarrow$ Sets $w_c = 0.8, w_l = 0.1$.
* `X-Routing-Force-Model: azure_openai.gpt-4o` $\rightarrow$ Bypasses scoring matrix if permitted by policy.
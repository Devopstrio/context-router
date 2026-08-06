# Tenant Isolation Architecture

1. **Cryptographic Tagging:** Every context frame is tagged with a verified `TenantID` extracted from JWT claims.
2. **Context Memory Sandboxing:** Routing queries to memory stores include hard tenant namespaces (`tenant_id:session_id`).
3. **Cross-Tenant Guardrail:** `TenantIsolationGuard` throws an unhandled exception and raises a security security incident if `X-Tenant-ID` header deviates from JWT claims.
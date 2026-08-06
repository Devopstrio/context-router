# Diagnostic & Error Code Taxonomy

All error payloads follow RFC 7807 Problem Details formatting.

```json
{
  "type": "https://router.context.internal/errors/ERR-4001",
  "title": "Tenant Validation Error",
  "status": 403,
  "detail": "Tenant 'tenant-alpha' is not authorized to route requests to region 'EU'.",
  "instance": "/v1/context/route",
  "code": "ERR-4001",
  "timestamp": "2026-08-05T16:22:18Z"
}
```

## System Error Registry

| Error Code | HTTP Status | Title | Description |
| :--- | :--- | :--- | :--- |
| `ERR-1001` | 400 | `INVALID_SCHEMA` | Payload fails JSON schema validation constraints. |
| `ERR-2001` | 401 | `UNAUTHORIZED` | Invalid signature, expired JWT token, or missing header. |
| `ERR-4001` | 403 | `TENANT_RESTRICTION` | Tenant boundary or data residency policy violation. |
| `ERR-5001` | 503 | `NO_TARGET_AVAILABLE` | All target models in provider matrix are circuit-broken. |
| `ERR-5002` | 504 | `DEPENDENCY_TIMEOUT` | Downstream dependent service (`memory-manager`) timed out. |
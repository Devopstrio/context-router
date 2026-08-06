# API Endpoint Documentation

## Endpoint 1: Evaluate & Route Context
* **URL:** `/v1/context/route`
* **Method:** `POST`
* **Auth:** JWT Bearer + Tenant Scopes

### Headers
| Header | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `Authorization` | String | Yes | `Bearer <JWT_TOKEN>` |
| `X-Correlation-ID` | String | Yes | UUID for distributed transaction tracing |
| `X-Tenant-ID` | String | Yes | Must match token `tenant_id` claim |

---

## Endpoint 2: Batch Context Route Resolution
* **URL:** `/v1/context/route/batch`
* **Method:** `POST`
* **Auth:** JWT Bearer (`batch:process` scope)

### Purpose
Processes up to 100 route evaluations in parallel for multi-agent or asynchronous pipeline workflows.

---

## Endpoint 3: Register / Update Model Capability Profile
* **URL:** `/v1/registry/models`
* **Method:** `POST`
* **Auth:** Internal System Admin JWT

### Purpose
Registers or updates model target profiles in the active scoring matrix.
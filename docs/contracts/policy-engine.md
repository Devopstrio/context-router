# Service Contract: `policy-engine`

## Protocol: gRPC In-Memory IPC / Local Shared Cache
Evaluates ABAC policies and tenant access rules prior to context routing.

### Input Parameters
* `tenant_id`: String
* `requested_provider`: String
* `data_classification`: String (`PUBLIC`, `CONFIDENTIAL`, `RESTRICTED_PHI`)

### Expected Output
* `is_allowed`: Boolean
* `restricted_regions`: Array of Strings
* `max_allowed_cost_per_token`: Float
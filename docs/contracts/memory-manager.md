# Service Contract: `memory-manager`

## 1. Interface Protocol
* **Protocol:** gRPC / Protobuf v3
* **Transport:** HTTP/2 over TLS 1.3
* **SLA Target:** P99 $< 8\text{ms}$

## 2. Protobuf Specification
```protobuf
syntax = "proto3";

package enterprise.context.memory;

service MemoryManagerService {
  rpc GetSessionStatePointer (SessionRequest) returns (SessionResponse);
}

message SessionRequest {
  string tenant_id = 1;
  string session_id = 2;
}

message SessionResponse {
  string session_id = 1;
  int32 message_count = 2;
  int64 estimated_history_tokens = 3;
  string state_pointer_uri = 4;
}
```
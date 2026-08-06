# Service Contract: `context-assembler`

## 1. Interface Protocol
* **Protocol:** REST / HTTP/2 or gRPC Event Dispatch
* **Purpose:** Directs physical prompt assembly following context routing decision.

## 2. Dispatch Spec Payload
```json
{
  "route_id": "route-8812-7712-4412",
  "tenant_id": "tenant-corp-alpha",
  "session_id": "sess-9923-bf34-9981",
  "target_model": {
    "provider": "azure_openai",
    "model_id": "gpt-4o",
    "endpoint": "https://eu-east-1.openai.azure.com/"
  },
  "assembly_instructions": {
    "inject_system_prompt_id": "sys-prompt-customer-support-v2",
    "include_memory_pointer": "redis://memory.internal/sess-9923",
    "max_output_tokens": 4096
  }
}
```
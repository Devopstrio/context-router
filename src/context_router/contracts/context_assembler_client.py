"""Contract Client for context-assembler Sibling Service."""

from typing import Any


class ContextAssemblerClient:
    """Client implementing the contract for dispatching context assembly instructions."""

    def __init__(self, host: str = "assembler.internal", port: int = 8082) -> None:
        self.host = host
        self.port = port

    def dispatch_assembly_job(
        self,
        route_id: str,
        tenant_id: str,
        session_id: str,
        provider: str,
        model_id: str,
        endpoint: str,
        max_output_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Dispatches an assembly instruction payload to context-assembler service."""
        return {
            "status": "DISPATCHED",
            "route_id": route_id,
            "tenant_id": tenant_id,
            "session_id": session_id,
            "target_model": {
                "provider": provider,
                "model_id": model_id,
                "endpoint": endpoint,
            },
            "assembly_instructions": {
                "inject_system_prompt_id": "sys-prompt-default-v1",
                "include_memory_pointer": f"redis://memory.internal/{tenant_id}:{session_id}",
                "max_output_tokens": max_output_tokens,
            },
        }

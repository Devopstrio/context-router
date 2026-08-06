"""Contract Client for memory-manager Sibling Service."""


class MemoryStatePointer:
    def __init__(
        self,
        session_id: str,
        message_count: int,
        estimated_history_tokens: int,
        state_pointer_uri: str,
    ) -> None:
        self.session_id = session_id
        self.message_count = message_count
        self.estimated_history_tokens = estimated_history_tokens
        self.state_pointer_uri = state_pointer_uri


class MemoryManagerClient:
    """Client implementing the contract for conversation history state lookups."""

    def __init__(self, host: str = "memory.internal", port: int = 50052) -> None:
        self.host = host
        self.port = port

    def get_session_state_pointer(
        self, tenant_id: str, session_id: str
    ) -> MemoryStatePointer:
        """Queries memory-manager for session history state pointer and token count."""
        # Simulated gRPC client response matching Protobuf contract
        return MemoryStatePointer(
            session_id=session_id,
            message_count=12,
            estimated_history_tokens=1450,
            state_pointer_uri=f"redis://memory.internal/{tenant_id}:{session_id}",
        )

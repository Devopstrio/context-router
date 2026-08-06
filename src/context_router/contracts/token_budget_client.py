"""Contract Client for token-budget-optimizer Sibling Service."""


class TokenBudgetClient:
    """Client implementing the contract for token estimation and payload truncation."""

    def __init__(self, host: str = "budget.internal", port: int = 8081) -> None:
        self.host = host
        self.port = port

    def estimate_payload_tokens(self, user_query: str, history_tokens: int) -> int:
        """Estimates total token mass (query + history)."""
        # Rough estimate: ~4 chars per token for query + history tokens
        query_tokens = max(1, len(user_query) // 4)
        return query_tokens + history_tokens

    def truncate_to_limit(self, user_query: str, max_allowed_tokens: int) -> str:
        """Truncates payload string to fit target max_allowed_tokens limit."""
        char_limit = max_allowed_tokens * 4
        if len(user_query) > char_limit:
            return user_query[:char_limit]
        return user_query

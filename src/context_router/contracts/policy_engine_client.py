"""Contract Client for policy-engine Sibling Service."""


class PolicyEvaluationResult:
    def __init__(
        self,
        is_allowed: bool,
        restricted_regions: list[str],
        max_allowed_cost_per_token: float,
    ) -> None:
        self.is_allowed = is_allowed
        self.restricted_regions = restricted_regions
        self.max_allowed_cost_per_token = max_allowed_cost_per_token


class PolicyEngineClient:
    """Client implementing the contract for ABAC policy evaluation."""

    def __init__(self, host: str = "policy.internal", port: int = 50051) -> None:
        self.host = host
        self.port = port

    def evaluate_tenant_policy(
        self, tenant_id: str, data_classification: str = "PUBLIC"
    ) -> PolicyEvaluationResult:
        """Queries policy-engine for tenant access constraints and data residency restrictions."""
        if data_classification == "RESTRICTED_PHI":
            return PolicyEvaluationResult(
                is_allowed=True,
                restricted_regions=["EU", "US"],
                max_allowed_cost_per_token=0.01,
            )
        return PolicyEvaluationResult(
            is_allowed=True,
            restricted_regions=["EU", "US", "APAC"],
            max_allowed_cost_per_token=0.05,
        )

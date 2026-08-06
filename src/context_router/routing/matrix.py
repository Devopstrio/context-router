"""Route Decision Matrix with Mathematical Scoring Equation."""

from context_router.config.model_registry import ModelProfile, ModelRegistry
from context_router.config.settings import ContextRouterSettings
from context_router.validation.schemas import RouteRequest


class RouteDecisionMatrix:
    """Evaluates and ranks candidate target models using deterministic multi-attribute utility scoring."""

    def __init__(
        self,
        model_registry: ModelRegistry,
        settings: ContextRouterSettings,
    ) -> None:
        self.registry = model_registry
        self.settings = settings

    def score_model(
        self,
        model: ModelProfile,
        max_cost: float,
        max_latency: float,
        circuit_health: float,
        tenant_affinity: float,
        weight_cost: float,
        weight_latency: float,
        weight_health: float,
        weight_affinity: float,
    ) -> float:
        """Calculates deterministic Target Score S_i according to mathematical formula:

        S_i = (w_c * (C_max - C_i) / C_max)
            + (w_l * (L_max - L_i) / L_max)
            + (w_h * H_i)
            + (w_a * A_i)
        """
        cost_term = (max_cost - model.cost_per_1k_input_tokens) / max_cost if max_cost > 0 else 1.0
        latency_term = (
            (max_latency - model.historical_p99_latency_ms) / max_latency if max_latency > 0 else 1.0
        )

        # Clamp terms to [0, 1]
        cost_term = max(0.0, min(1.0, cost_term))
        latency_term = max(0.0, min(1.0, latency_term))

        score = (
            (weight_cost * cost_term)
            + (weight_latency * latency_term)
            + (weight_health * circuit_health)
            + (weight_affinity * tenant_affinity)
        )
        return float(score)

    def evaluate_route(
        self,
        request: RouteRequest,
        total_tokens: int,
        circuit_statuses: dict[str, bool],
        tenant_allowed_regions: list[str] | None = None,
        override_weights: dict[str, float] | None = None,
    ) -> tuple[ModelProfile, list[ModelProfile]]:
        """Filters candidate models by capacity, region, cost, and health."""
        active_models = self.registry.get_all_active_models()

        # Step 1: Filter models
        eligible: list[ModelProfile] = []
        for m in active_models:
            # Context window check
            if m.context_window < total_tokens:
                continue

            # Region check
            if tenant_allowed_regions and not any(r in tenant_allowed_regions for r in m.supported_regions):
                continue

            # Request cost constraint check
            if request.constraints and request.constraints.max_cost_per_1k_tokens is not None:
                if m.cost_per_1k_input_tokens > request.constraints.max_cost_per_1k_tokens:
                    continue

            # Request allowed providers constraint check
            if request.constraints and request.constraints.allowed_providers:
                if m.provider not in request.constraints.allowed_providers:
                    continue

            # Circuit breaker check (if false = open/unhealthy)
            if not circuit_statuses.get(m.model_id, True):
                continue

            eligible.append(m)

        if not eligible:
            raise ValueError("No eligible models found matching context requirements and health status")

        # Determine weight parameters
        s_set = self.settings
        w_c = override_weights.get("w_c", s_set.weight_cost) if override_weights else s_set.weight_cost
        w_l = override_weights.get("w_l", s_set.weight_latency) if override_weights else s_set.weight_latency
        w_h = override_weights.get("w_h", s_set.weight_health) if override_weights else s_set.weight_health
        w_a = override_weights.get("w_a", s_set.weight_affinity) if override_weights else s_set.weight_affinity

        max_cost = max(m.cost_per_1k_input_tokens for m in eligible) or 1.0
        max_latency = max(m.historical_p99_latency_ms for m in eligible) or 1.0

        # Step 2: Score eligible models
        scored: list[tuple[float, ModelProfile]] = []
        for m in eligible:
            circuit_health = 1.0 if circuit_statuses.get(m.model_id, True) else 0.0
            has_affinity = tenant_allowed_regions and any(r in tenant_allowed_regions for r in m.supported_regions)
            affinity = 1.0 if has_affinity else 0.5
            s = self.score_model(
                m, max_cost, max_latency, circuit_health, affinity, w_c, w_l, w_h, w_a
            )
            scored.append((s, m))

        scored.sort(key=lambda x: x[0], reverse=True)

        best_model = scored[0][1]
        fallback_chain = [item[1] for item in scored[1:3]]

        return best_model, fallback_chain

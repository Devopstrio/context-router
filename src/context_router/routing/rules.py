"""Priority Rule Engine and Header Hint Overrides."""


class PriorityRuleEngine:
    """Evaluates multi-layer governance and routing rules."""

    def resolve_header_overrides(
        self,
        headers: dict[str, str],
    ) -> tuple[dict[str, float] | None, str | None]:
        """Parses operational override hints from HTTP headers."""
        preference = headers.get("x-routing-preference", "").lower()
        force_model = headers.get("x-routing-force-model")

        override_weights = None
        if preference == "ultra-low-latency":
            override_weights = {"w_l": 0.8, "w_c": 0.1, "w_h": 0.05, "w_a": 0.05}
        elif preference == "cost-optimized":
            override_weights = {"w_c": 0.8, "w_l": 0.1, "w_h": 0.05, "w_a": 0.05}
        elif preference == "high-accuracy":
            override_weights = {"w_c": 0.1, "w_l": 0.2, "w_h": 0.4, "w_a": 0.3}

        return override_weights, force_model

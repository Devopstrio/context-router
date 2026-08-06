"""Model Capability Profile Registry."""

from typing import Any
from pydantic import BaseModel


class ModelProfile(BaseModel):
    """Model target capability profile."""

    model_id: str
    provider: str
    endpoint: str
    context_window: int
    cost_per_1k_input_tokens: float
    historical_p99_latency_ms: float
    supported_regions: list[str]
    is_active: bool = True
    metadata: dict[str, Any] = {}


class ModelRegistry:
    """Registry maintaining active model capability profiles for decision routing."""

    def __init__(self) -> None:
        self._models: dict[str, ModelProfile] = {}
        self._seed_default_models()

    def _seed_default_models(self) -> None:
        defaults = [
            ModelProfile(
                model_id="gpt-4o",
                provider="azure_openai",
                endpoint="https://eu-east-1.openai.azure.com/deployments/gpt-4o",
                context_window=128000,
                cost_per_1k_input_tokens=0.005,
                historical_p99_latency_ms=8.5,
                supported_regions=["EU", "US"],
            ),
            ModelProfile(
                model_id="gpt-4o-mini",
                provider="azure_openai",
                endpoint="https://eu-east-1.openai.azure.com/deployments/gpt-4o-mini",
                context_window=128000,
                cost_per_1k_input_tokens=0.00015,
                historical_p99_latency_ms=4.2,
                supported_regions=["EU", "US", "APAC"],
            ),
            ModelProfile(
                model_id="claude-3-5-sonnet",
                provider="anthropic_bedrock",
                endpoint="https://bedrock-runtime.eu-west-1.amazonaws.com/model/claude-3-5-sonnet",
                context_window=200000,
                cost_per_1k_input_tokens=0.003,
                historical_p99_latency_ms=9.1,
                supported_regions=["EU", "US"],
            ),
            ModelProfile(
                model_id="llama-3-70b",
                provider="aws_bedrock",
                endpoint="https://bedrock-runtime.us-east-1.amazonaws.com/model/llama-3-70b",
                context_window=8192,
                cost_per_1k_input_tokens=0.0007,
                historical_p99_latency_ms=6.0,
                supported_regions=["US"],
            ),
        ]
        for m in defaults:
            self._models[m.model_id] = m

    def register_model(self, profile: ModelProfile) -> None:
        self._models[profile.model_id] = profile

    def get_model(self, model_id: str) -> ModelProfile | None:
        return self._models.get(model_id)

    def get_all_active_models(self) -> list[ModelProfile]:
        return [m for m in self._models.values() if m.is_active]

    def list_models(self) -> list[ModelProfile]:
        return list(self._models.values())

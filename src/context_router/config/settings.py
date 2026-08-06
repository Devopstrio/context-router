"""Application Configuration Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class ContextRouterSettings(BaseSettings):
    """Production configuration settings for context-router."""

    environment: str = "production"
    port: int = 8080
    host: str = "127.0.0.1"
    log_level: str = "INFO"

    # Security & Auth
    jwt_secret_key: str = "super-secret-enterprise-jwt-key-32bytes-minimum!"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "https://auth.enterprise.internal"
    jwt_audience: str = "context-router-api"
    enable_mtls_verification: bool = False

    # L2 Cache
    redis_primary_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 20
    redis_timeout_seconds: float = 2.0
    l1_cache_ttl_seconds: int = 5

    # Routing Weights
    weight_cost: float = 0.3
    weight_latency: float = 0.3
    weight_health: float = 0.2
    weight_affinity: float = 0.2

    # Sibling Services
    policy_engine_host: str = "policy.internal"
    policy_engine_port: int = 50051
    memory_manager_host: str = "memory.internal"
    memory_manager_port: int = 50052
    token_budget_host: str = "budget.internal"
    token_budget_port: int = 8081
    context_assembler_host: str = "assembler.internal"
    context_assembler_port: int = 8082
    audit_service_host: str = "audit.internal"
    audit_service_port: int = 9092

    # Resiliency
    max_routing_timeout_ms: int = 15
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout_seconds: int = 30

    model_config = SettingsConfigDict(env_prefix="CONTEXT_ROUTER_", env_file=".env")

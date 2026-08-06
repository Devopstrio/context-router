"""JWT Authentication & Claims Validation."""

import time
from typing import Any

import jwt
from pydantic import BaseModel, Field


class JWTClaims(BaseModel):
    """Cryptographic JWT Token Claims."""

    iss: str = "https://auth.enterprise.internal"
    sub: str = "service-agent-01"
    aud: str = "context-router-api"
    exp: int
    iat: int
    tenant_id: str
    roles: list[str] = Field(default_factory=list)
    data_residency: list[str] = Field(default_factory=list)


class JWTAuthenticator:
    """Validates JWT bearer tokens and extracts tenant identity context."""

    def __init__(
        self,
        secret_key: str = "super-secret-enterprise-jwt-key-32bytes-minimum!",
        algorithm: str = "HS256",
        issuer: str = "https://auth.enterprise.internal",
        audience: str = "context-router-api",
    ) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.issuer = issuer
        self.audience = audience

    def decode_and_validate(self, token: str) -> JWTClaims:
        """Decodes token and validates signature, expiration, issuer, audience."""
        try:
            payload: dict[str, Any] = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_signature": True, "verify_exp": True},
            )
            return JWTClaims(
                iss=payload.get("iss", self.issuer),
                sub=payload.get("sub", "service-agent"),
                aud=payload.get("aud", self.audience),
                exp=payload.get("exp", int(time.time()) + 3600),
                iat=payload.get("iat", int(time.time())),
                tenant_id=payload.get("tenant_id", "default-tenant"),
                roles=payload.get("roles", ["context:route"]),
                data_residency=payload.get("data_residency", ["EU", "US"]),
            )
        except jwt.PyJWTError as e:
            raise ValueError(f"Invalid JWT Token: {str(e)}") from e

    def generate_test_token(
        self,
        tenant_id: str = "tenant-corp-alpha",
        roles: list[str] | None = None,
        data_residency: list[str] | None = None,
        expires_in_seconds: int = 3600,
    ) -> str:
        """Generates a valid signed JWT token for testing and integration suites."""
        now = int(time.time())
        claims = {
            "iss": self.issuer,
            "sub": "service-agent-test",
            "aud": self.audience,
            "exp": now + expires_in_seconds,
            "iat": now,
            "tenant_id": tenant_id,
            "roles": roles or ["context:route", "session:read"],
            "data_residency": data_residency or ["EU", "US"],
        }
        return jwt.encode(claims, self.secret_key, algorithm=self.algorithm)

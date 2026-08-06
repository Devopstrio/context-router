"""Tenant Isolation Guardrail."""

from context_router.security.jwt_auth import JWTClaims


class SecurityBoundaryViolation(Exception):
    """Exception raised when a cross-tenant boundary violation is detected."""

    def __init__(self, message: str, code: str = "ERR-4001") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class TenantIsolationGuard:
    """Verifies multi-tenancy isolation boundaries and cryptographic tenant tags."""

    def verify_tenant_boundary(self, header_tenant_id: str, jwt_claims: JWTClaims) -> None:
        """Ensures X-Tenant-ID header strictly matches tenant_id in validated JWT claims."""
        if not header_tenant_id:
            raise SecurityBoundaryViolation(
                "Missing required X-Tenant-ID header", code="ERR-4001"
            )

        if header_tenant_id != jwt_claims.tenant_id:
            raise SecurityBoundaryViolation(
                f"Tenant boundary violation: Header '{header_tenant_id}' does not match authenticated token claim '{jwt_claims.tenant_id}'",
                code="ERR-4001",
            )

    def enforce_data_residency(
        self, tenant_claims: JWTClaims, target_regions: list[str]
    ) -> None:
        """Validates that target regions comply with tenant's data residency policies."""
        if not tenant_claims.data_residency:
            return  # No restriction specified

        allowed_set = set(tenant_claims.data_residency)
        for region in target_regions:
            if region not in allowed_set:
                raise SecurityBoundaryViolation(
                    f"Data residency policy violation: Target region '{region}' is not authorized for tenant '{tenant_claims.tenant_id}' (Allowed: {tenant_claims.data_residency})",
                    code="ERR-4001",
                )

"""Role-Based (RBAC) and Attribute-Based (ABAC) Access Control Engine."""

from typing import Any

from context_router.security.jwt_auth import JWTClaims
from context_router.security.tenant_guard import SecurityBoundaryViolation


class RBACABACEngine:
    """Evaluates fine-grained RBAC and ABAC access control policies."""

    REQUIRED_ROUTE_ROLE = "context:route"
    ADMIN_ROLE = "admin:models"

    def authorize_route_request(
        self,
        claims: JWTClaims,
        request_attributes: dict[str, Any] | None = None,
    ) -> None:
        """Validates that token contains necessary roles for routing."""
        if not claims.roles:
            raise SecurityBoundaryViolation(
                "Access Denied: Token lacks required roles", code="ERR-4001"
            )

        if self.REQUIRED_ROUTE_ROLE not in claims.roles and "admin" not in claims.roles:
            raise SecurityBoundaryViolation(
                f"Access Denied: Missing required role '{self.REQUIRED_ROUTE_ROLE}'",
                code="ERR-4001",
            )

        # ABAC Evaluation if request attributes provided
        if request_attributes:
            data_classification = request_attributes.get("data_classification")
            if data_classification == "RESTRICTED_PHI" and "phi:access" not in claims.roles:
                raise SecurityBoundaryViolation(
                    "ABAC Policy Violation: Accessing RESTRICTED_PHI requires 'phi:access' role",
                    code="ERR-4001",
                )

    def authorize_admin_request(self, claims: JWTClaims) -> None:
        """Validates admin role for model registry management."""
        if self.ADMIN_ROLE not in claims.roles and "admin" not in claims.roles:
            raise SecurityBoundaryViolation(
                f"Access Denied: Action requires administrative role '{self.ADMIN_ROLE}'",
                code="ERR-4001",
            )

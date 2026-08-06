"""Unit tests for Security, JWT Authentication, and Tenant Isolation Guard."""

import pytest
from context_router.security.jwt_auth import JWTAuthenticator
from context_router.security.rbac_abac import RBACABACEngine
from context_router.security.tenant_guard import SecurityBoundaryViolation, TenantIsolationGuard


def test_jwt_generation_and_validation(authenticator):
    token = authenticator.generate_test_token(tenant_id="tenant-corp-alpha")
    claims = authenticator.decode_and_validate(token)
    assert claims.tenant_id == "tenant-corp-alpha"
    assert "context:route" in claims.roles


def test_jwt_invalid_token_raises_value_error(authenticator):
    with pytest.raises(ValueError):
        authenticator.decode_and_validate("invalid.jwt.token")


def test_tenant_boundary_verification_matching(authenticator):
    guard = TenantIsolationGuard()
    claims = authenticator.decode_and_validate(authenticator.generate_test_token("tenant-alpha"))
    # Should not raise exception
    guard.verify_tenant_boundary("tenant-alpha", claims)


def test_tenant_boundary_verification_mismatch_raises_violation(authenticator):
    guard = TenantIsolationGuard()
    claims = authenticator.decode_and_validate(authenticator.generate_test_token("tenant-alpha"))
    with pytest.raises(SecurityBoundaryViolation) as exc_info:
        guard.verify_tenant_boundary("tenant-beta", claims)
    assert exc_info.value.code == "ERR-4001"


def test_rbac_abac_authorization(authenticator):
    rbac = RBACABACEngine()
    claims = authenticator.decode_and_validate(authenticator.generate_test_token())
    # Standard authorized request
    rbac.authorize_route_request(claims)

    # Missing required PHI role for RESTRICTED_PHI
    with pytest.raises(SecurityBoundaryViolation):
        rbac.authorize_route_request(claims, {"data_classification": "RESTRICTED_PHI"})

"""Security Middleware for Request Interception and Auth Enforcement."""

import uuid
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from context_router.security.jwt_auth import JWTAuthenticator
from context_router.security.tenant_guard import TenantIsolationGuard


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing Correlation ID, JWT authentication, and Tenant Isolation."""

    def __init__(
        self,
        app: Any,
        authenticator: JWTAuthenticator,
        tenant_guard: TenantIsolationGuard,
    ) -> None:
        super().__init__(app)
        self.authenticator = authenticator
        self.tenant_guard = tenant_guard

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Generate or capture correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        # Skip auth for health endpoints and docs
        path = request.url.path
        if path.startswith("/health") or path in ("/docs", "/redoc", "/openapi.json"):
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = correlation_id
            return response

        # Auth enforcement
        auth_header = request.headers.get("Authorization")
        tenant_header = request.headers.get("X-Tenant-ID")

        if not auth_header or not auth_header.startswith("Bearer "):
            # Let route handler or exception handler handle missing auth
            pass
        else:
            token = auth_header.split(" ", 1)[1]
            try:
                claims = self.authenticator.decode_and_validate(token)
                request.state.claims = claims

                if tenant_header:
                    self.tenant_guard.verify_tenant_boundary(tenant_header, claims)
            except Exception as e:
                request.state.auth_error = str(e)

        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response

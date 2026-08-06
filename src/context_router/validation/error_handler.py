"""RFC 7807 Problem Details Error Handlers."""

import datetime
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from context_router.security.tenant_guard import SecurityBoundaryViolation


class RouterBaseException(Exception):
    """Base exception for context-router diagnostic taxonomy."""

    def __init__(self, code: str, title: str, status: int, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.title = title
        self.status = status
        self.detail = detail


class NoTargetAvailableException(RouterBaseException):
    """Raised when all candidate model targets are unavailable or circuit broken."""

    def __init__(self, detail: str = "All target models in provider matrix are circuit-broken.") -> None:
        super().__init__(
            code="ERR-5001",
            title="NO_TARGET_AVAILABLE",
            status=503,
            detail=detail,
        )


class DependencyTimeoutException(RouterBaseException):
    """Raised when a downstream contract service times out."""

    def __init__(self, detail: str = "Downstream dependent service timed out.") -> None:
        super().__init__(
            code="ERR-5002",
            title="DEPENDENCY_TIMEOUT",
            status=504,
            detail=detail,
        )


def build_problem_details(
    code: str, title: str, status: int, detail: str, instance: str
) -> dict[str, Any]:
    """Constructs RFC 7807 compliant error dictionary."""
    return {
        "type": f"https://router.context.internal/errors/{code}",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": instance,
        "code": code,
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handles 400 Bad Request schema validation failures."""
    payload = build_problem_details(
        code="ERR-1001",
        title="INVALID_SCHEMA",
        status=400,
        detail=str(exc),
        instance=request.url.path,
    )
    return JSONResponse(status_code=400, content=payload)


async def security_boundary_exception_handler(
    request: Request, exc: SecurityBoundaryViolation
) -> JSONResponse:
    """Handles 403 Forbidden tenant restriction & security boundary violations."""
    payload = build_problem_details(
        code=exc.code,
        title="TENANT_RESTRICTION",
        status=403,
        detail=exc.message,
        instance=request.url.path,
    )
    return JSONResponse(status_code=403, content=payload)


async def router_base_exception_handler(
    request: Request, exc: RouterBaseException
) -> JSONResponse:
    """Handles taxonomy router exceptions (503, 504, etc.)."""
    payload = build_problem_details(
        code=exc.code,
        title=exc.title,
        status=exc.status,
        detail=exc.detail,
        instance=request.url.path,
    )
    return JSONResponse(status_code=exc.status, content=payload)

"""Ingress Validator for Request Validation."""

from context_router.validation.schemas import RouteRequest


class IngressValidator:
    """Validates structural and semantic rules of ingress context route requests."""

    def validate_payload(self, request: RouteRequest) -> None:
        """Validates payload schema and required fields."""
        if not request.tenant_id or not request.tenant_id.strip():
            raise ValueError("tenant_id must be non-empty")
        if not request.session_id or not request.session_id.strip():
            raise ValueError("session_id must be non-empty")
        if not request.request_context.user_query or not request.request_context.user_query.strip():
            raise ValueError("user_query must be non-empty")

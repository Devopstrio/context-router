"""Liveness, Readiness, and Startup Health Probes."""

import time
from typing import Any

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(tags=["Health"])

_start_time = time.time()


@router.get("/health/live", response_model=None)
def liveness_probe() -> dict[str, Any]:
    """Liveness probe: verifies process is alive."""
    return {
        "status": "UP",
        "service": "context-router",
        "timestamp": time.time(),
    }


@router.get("/health/ready", response_model=None)
def readiness_probe(request: Request) -> dict[str, Any]:
    """Readiness probe: checks Redis L2 cache connection and model registry."""
    l2_cache = request.app.state.l2_cache
    redis_ready = l2_cache.ping() if l2_cache else True

    registry = request.app.state.model_registry
    models_ready = len(registry.get_all_active_models()) > 0 if registry else False

    if not redis_ready or not models_ready:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "DOWN",
                "redis_connected": redis_ready,
                "models_available": models_ready,
            },
        )

    return {
        "status": "UP",
        "redis_connected": redis_ready,
        "models_available": models_ready,
        "timestamp": time.time(),
    }


@router.get("/health/startup", response_model=None)
def startup_probe() -> dict[str, Any]:
    """Startup probe: verifies service initialized properly."""
    uptime_seconds = time.time() - _start_time
    return {
        "status": "UP",
        "uptime_seconds": round(uptime_seconds, 2),
        "timestamp": time.time(),
    }

"""Probes (port of `controllers/health.controller.ts`)."""

from __future__ import annotations

from backend.core.http.types import ApiRequest
from backend.core.http.types import Reply
from backend.core.http.types import ok
from backend.operations.services import health as health


def get_health(req: ApiRequest) -> Reply:
    return ok(health.liveness())


def get_ready(req: ApiRequest) -> Reply:
    result = health.readiness()
    return ok(result, status=200 if result["status"] == "ready" else 503)

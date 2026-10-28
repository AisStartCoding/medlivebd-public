"""Probes (port of `controllers/health.controller.ts`)."""

from __future__ import annotations

from medlive.core.http import ApiRequest
from medlive.core.http import Reply
from medlive.core.http import ok
from medlive.modules.operations.services import health as health


def get_health(req: ApiRequest) -> Reply:
    return ok(health.liveness())


def get_ready(req: ApiRequest) -> Reply:
    result = health.readiness()
    return ok(result, status=200 if result["status"] == "ready" else 503)

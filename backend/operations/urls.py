"""Probes, at the root rather than under `/api/v1` (port of `routes/health.routes.ts`)."""

from backend.operations import views as health
from backend.core.http.router import Router

health_routes = Router()

health_routes.get("/healthz", health.get_health)
health_routes.get("/readyz", health.get_ready)

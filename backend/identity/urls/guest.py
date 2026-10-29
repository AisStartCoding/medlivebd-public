"""Tracking-link routes (port of `routes/guest.routes.ts`; FR-GST-05, FR-LAB-04)."""

from backend.identity.views import guest as guest
from backend.core.http.router import Router
from backend.core.validation.requests import validate
from backend.domain.schemas import booking as s

routes = Router()

routes.get("/guest/link/:token", validate(params=s.tracking_link_params), guest.open_tracking_link)
routes.get(
    "/guest/link/:token/reports/:reportId", validate(params=s.tracking_report_params), guest.report_url
)

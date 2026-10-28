"""Tracking-link routes (port of `routes/guest.routes.ts`; FR-GST-05, FR-LAB-04)."""

from medlive.modules.identity.views import guest as guest
from medlive.core.router import Router
from medlive.core.validation import validate
from medlive.domain.schemas import booking as s

routes = Router()

routes.get("/guest/link/:token", validate(params=s.tracking_link_params), guest.open_tracking_link)
routes.get(
    "/guest/link/:token/reports/:reportId", validate(params=s.tracking_report_params), guest.report_url
)

"""Provider callbacks (port of `routes/webhooks.routes.ts`; FR-PAY-03, FR-NOT-06)."""

from backend.payments.views import webhooks as webhooks
from backend.core.http.router import Router

routes = Router()

routes.post("/webhooks/bkash", webhooks.callback("bkash"))
routes.post("/webhooks/nagad", webhooks.callback("nagad"))
routes.post("/webhooks/sms-dlr", webhooks.sms_delivery)

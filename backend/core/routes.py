"""Route mounting (port of `routes/index.ts`).

Base path `/api/v1`. Every response is `{ ok: true, data }` or
`{ ok: false, error: { code, message, details } }`. The routers are mounted
in the order the TypeScript mounts them, because the first route that matches
answers.
"""

from __future__ import annotations

import importlib

from backend.core.http.pipeline import install_routes
from backend.core.http.router import Router

#: The TypeScript's order (`buildApiRouter`). A router is listed once its
#: module is ported; `docs/django-migration/compatibility-matrix.md` tracks it.
ROUTE_MODULES = {
    "admin": "backend.reporting.urls.admin",
    "gov": "backend.reporting.urls.gov",
    "bed": "backend.beds.urls",
    "booking": "backend.booking.urls.booking",
    "registration": "backend.booking.urls.registration",
    "standby": "backend.booking.urls.standby",
    "clinical": "backend.clinical.urls.clinical",
    "consent": "backend.clinical.urls.consent",
    "demo": "backend.demo.urls",
    "emergency": "backend.emergency.urls",
    "guest": "backend.identity.urls.guest",
    "patient_auth": "backend.identity.urls.patient_auth",
    "staff_auth": "backend.identity.urls.staff_auth",
    "health": "backend.operations.urls",
    "hospital_settings": "backend.hospital.urls",
    "imports": "backend.imports.urls",
    "lab": "backend.laboratory.urls",
    "mock_pay": "backend.payments.urls.mock_pay",
    "payment": "backend.payments.urls.payment",
    "webhooks": "backend.payments.urls.webhooks",
    "platform": "backend.platform_admin.urls",
    "queue": "backend.queues.urls.queue",
    "sync": "backend.queues.urls.sync",
    "referral": "backend.referrals.urls",
    "discovery": "backend.catalog.urls"
}

API_ROUTERS: list[str] = [
    "discovery",
    "guest",
    "demo",
    "staff_auth",
    "patient_auth",
    "booking",
    "queue",
    "registration",
    "standby",
    "clinical",
    "consent",
    "bed",
    "emergency",
    "referral",
    "lab",
    "payment",
    "admin",
    "hospital_settings",
    "imports",
    "platform",
    "gov",
    "webhooks",
    "mock_pay",
    "sync",
]

#: Mounted only where its condition holds (`buildApiRouter`).
_CONDITIONAL = {"mock_pay": lambda e: e.PAYMENT_PROVIDER == "mock"}


def build() -> tuple[Router, Router]:
    from backend.core.security.demo_phones import install_demo_phone_rule
    from backend.operations.urls import health_routes

    # FR-DEM-08: a demonstration takes a person's phone only from its own list.
    install_demo_phone_rule()

    from backend.core.env import env

    api = Router()
    for name in API_ROUTERS:
        condition = _CONDITIONAL.get(name)
        if condition is not None and not condition(env()):
            continue
        module = importlib.import_module(ROUTE_MODULES[name])
        api.use(module.routes)
    root = Router()
    root.use(health_routes)

    if env().NODE_ENV == "test":
        from backend.core.testing.seam import routes as seam

        root.use(seam)
    install_routes(api, root)
    return api, root

"""Route mounting (port of `routes/index.ts`).

Base path `/api/v1`. Every response is `{ ok: true, data }` or
`{ ok: false, error: { code, message, details } }`. The routers are mounted
in the order the TypeScript mounts them, because the first route that matches
answers.
"""

from __future__ import annotations

import importlib

from ..core.pipeline import install_routes
from ..core.router import Router

#: The TypeScript's order (`buildApiRouter`). A router is listed once its
#: module is ported; `docs/django-migration/compatibility-matrix.md` tracks it.
ROUTE_MODULES = {
    "admin": "medlive.modules.reporting.urls.admin",
    "gov": "medlive.modules.reporting.urls.gov",
    "bed": "medlive.modules.beds.urls",
    "booking": "medlive.modules.booking.urls.booking",
    "registration": "medlive.modules.booking.urls.registration",
    "standby": "medlive.modules.booking.urls.standby",
    "clinical": "medlive.modules.clinical.urls.clinical",
    "consent": "medlive.modules.clinical.urls.consent",
    "demo": "medlive.modules.demo.urls",
    "emergency": "medlive.modules.emergency.urls",
    "guest": "medlive.modules.identity.urls.guest",
    "patient_auth": "medlive.modules.identity.urls.patient_auth",
    "staff_auth": "medlive.modules.identity.urls.staff_auth",
    "health": "medlive.modules.operations.urls",
    "hospital_settings": "medlive.modules.hospital.urls",
    "imports": "medlive.modules.imports.urls",
    "lab": "medlive.modules.laboratory.urls",
    "mock_pay": "medlive.modules.payments.urls.mock_pay",
    "payment": "medlive.modules.payments.urls.payment",
    "webhooks": "medlive.modules.payments.urls.webhooks",
    "platform": "medlive.modules.platform.urls",
    "queue": "medlive.modules.queue.urls.queue",
    "sync": "medlive.modules.queue.urls.sync",
    "referral": "medlive.modules.referrals.urls",
    "discovery": "medlive.modules.catalog.urls"
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
    from ..core.demo_phones import install_demo_phone_rule
    from medlive.modules.operations.urls import health_routes

    # FR-DEM-08: a demonstration takes a person's phone only from its own list.
    install_demo_phone_rule()

    from ..core.env import env

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
        from .test_seam import routes as seam

        root.use(seam)
    install_routes(api, root)
    return api, root

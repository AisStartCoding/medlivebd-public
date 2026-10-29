"""The process: Django's HTTP application and the Socket.IO server on one port
(port of `server.ts`; BACKEND.md §3, §6, §12).

    uvicorn backend.core.asgi:application --host 0.0.0.0 --port 4000 --no-proxy-headers

`--no-proxy-headers` because the client address is decided by the pipeline
from `TRUST_PROXY_HOPS`, exactly as Express's `trust proxy` decided it.
The Socket.IO server answers `/socket.io/`; everything else is Django.
Background work (schedules, the message sender, offer and payment timers)
starts with the process and stops with it.
"""

from __future__ import annotations

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.core.settings")

import django  # noqa: E402

django.setup()

import socketio  # noqa: E402
from django.core.asgi import get_asgi_application  # noqa: E402

from backend.core.env import env
from backend.core.observability.logging import logger
from backend.realtime.server import attach_loop
from backend.realtime.server import sio
from backend.realtime.server import start_realtime_tasks
from backend.realtime.server import stop_realtime_tasks

django_application = get_asgi_application()


async def _startup() -> None:
    attach_loop()
    start_realtime_tasks()
    if env().RUN_BACKGROUND_JOBS:
        from backend.operations.services.jobs import start_background

        start_background()
    e = env()
    logger.info(
        {
            "port": e.PORT,
            "nodeEnv": e.NODE_ENV,
            "demoMode": e.DEMO_MODE,
            "smsProvider": e.SMS_PROVIDER,
            "paymentProvider": e.PAYMENT_PROVIDER,
        },
        "api listening",
    )


async def _shutdown() -> None:
    logger.info({}, "shutting down")
    from backend.operations.services.jobs import stop_background

    stop_background()
    await stop_realtime_tasks()
    logger.info({}, "shutdown complete")


application = socketio.ASGIApp(
    sio,
    other_asgi_app=django_application,
    socketio_path="socket.io",
    on_startup=_startup,
    on_shutdown=_shutdown,
)

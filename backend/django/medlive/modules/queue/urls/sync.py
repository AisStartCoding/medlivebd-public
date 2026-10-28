"""Offline sync routes (port of `routes/sync.routes.ts`; SY-01, FR-OFF-01).

The batch is idempotent by each entry's `clientEventId`; the request-level
key is optional because a console that lost its answer sends the same batch.
"""

from medlive.modules.queue.views import sync as sync
from medlive.core.auth import idempotency
from medlive.core.auth import require_auth
from medlive.core.auth import require_role
from medlive.core.router import Router
from medlive.core.validation import validate
from medlive.domain.schemas import sync as s

routes = Router()

_CONSOLE_ROLES = ("receptionist", "doctor", "hospital_admin")

routes.post(
    "/sync/events",
    require_auth,
    require_role(*_CONSOLE_ROLES),
    idempotency(),
    validate(body=s.sync_batch_body),
    sync.push_events,
)
routes.get(
    "/sync/session/:id",
    require_auth,
    require_role(*_CONSOLE_ROLES),
    validate(params=s.sync_params, query=s.sync_pull_query),
    sync.pull_session,
)

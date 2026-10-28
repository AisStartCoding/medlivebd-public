"""Counter registration routes (port of `routes/registration.routes.ts`; S-B-03, FR-REC-14)."""

from medlive.modules.booking.views import registration as registration
from medlive.core.auth import WRITE
from medlive.core.auth import require_auth
from medlive.core.auth import require_role
from medlive.core.router import Router
from medlive.core.validation import validate
from medlive.domain.schemas import registration as s

routes = Router()

_reception = (require_auth, require_role("receptionist"))

routes.get(
    "/registration/patients", *_reception, validate(query=s.registration_lookup_query), registration.lookup
)
routes.post(
    "/registration/patients", *_reception, WRITE, validate(body=s.register_patient_body), registration.register
)

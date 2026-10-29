"""Counter registration routes (port of `routes/registration.routes.ts`; S-B-03, FR-REC-14)."""

from backend.booking.views import registration as registration
from backend.core.security.auth import WRITE
from backend.core.security.auth import require_auth
from backend.core.security.auth import require_role
from backend.core.http.router import Router
from backend.core.validation.requests import validate
from backend.domain.schemas import registration as s

routes = Router()

_reception = (require_auth, require_role("receptionist"))

routes.get(
    "/registration/patients", *_reception, validate(query=s.registration_lookup_query), registration.lookup
)
routes.post(
    "/registration/patients", *_reception, WRITE, validate(body=s.register_patient_body), registration.register
)

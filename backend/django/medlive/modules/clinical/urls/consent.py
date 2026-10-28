"""Consent routes (port of `routes/consent.routes.ts`; FR-PAT-63, FR-PAT-64)."""

from medlive.modules.clinical.views import consent as consent
from medlive.core.auth import WRITE
from medlive.core.auth import require_auth
from medlive.core.router import Router
from medlive.core.validation import validate
from medlive.domain.schemas import clinical as s
from medlive.domain.schemas.booking import id_params

routes = Router()

routes.post("/patients/:id/consent-offer", require_auth, WRITE, validate(params=id_params), consent.offer_consent)
routes.post("/consents/qr", require_auth, WRITE, validate(body=s.redeem_consent_body), consent.redeem_consent)
routes.post("/consents", require_auth, WRITE, validate(body=s.create_consent_body), consent.create_consent)
routes.post("/consents/:id/revoke", require_auth, WRITE, validate(params=id_params), consent.revoke_consent)
routes.get("/patients/:id/access", require_auth, validate(params=id_params), consent.get_access)

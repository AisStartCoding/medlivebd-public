"""Patient sign-in routes (port of `routes/patientAuth.routes.ts`; FR-PAT-01, FR-PAT-04, FR-GST-03, FR-SEC-05).

Sending a code is limited per address as well as per phone (the service
counts the phone), so one address cannot spray codes at many numbers.
"""

from medlive.modules.identity.views import patient_auth as patient_auth
from medlive.core.auth import WRITE
from medlive.core.auth import require_auth
from medlive.core.ratelimit import by_ip
from medlive.core.ratelimit import rate_limit
from medlive.core.router import Router
from medlive.core.validation import validate
from medlive.domain.schemas import auth as s

routes = Router()

_send_limit = rate_limit(limit=30, window_seconds=600, key_for=by_ip, code="AUTH_OTP_RATE_LIMIT")
_verify_limit = rate_limit(limit=60, window_seconds=600, key_for=by_ip, code="AUTH_OTP_RATE_LIMIT")
_refresh_limit = rate_limit(limit=2_000, window_seconds=600, key_for=by_ip)

routes.post("/auth/otp", _send_limit, validate(body=s.otp_request_body), patient_auth.request_code)
routes.post("/auth/verify", _verify_limit, validate(body=s.otp_verify_body), patient_auth.verify)
routes.post("/auth/refresh", _refresh_limit, validate(body=s.patient_refresh_body), patient_auth.refresh)
routes.post("/auth/logout", validate(body=s.patient_refresh_body), patient_auth.logout)
routes.post("/guest/start", _send_limit, validate(body=s.guest_start_body), patient_auth.start_guest)
routes.post("/guest/verify", _verify_limit, validate(body=s.guest_verify_body), patient_auth.verify_guest)
routes.get("/me/profiles", require_auth, patient_auth.profiles)
routes.post("/guest/claim", require_auth, WRITE, validate(body=s.claim_body), patient_auth.claim)

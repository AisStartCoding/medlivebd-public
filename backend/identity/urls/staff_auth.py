"""Staff sign-in routes (port of `routes/staffAuth.routes.ts`; S-B-00, FR-SEC-06, FR-SUP-01).

The address limit is generous because a hospital's whole staff can sit
behind one address; the account lockout is what stops guessing.
"""

from backend.identity.views import staff_auth as staff_auth
from backend.core.security.auth import require_auth
from backend.core.http.ratelimit import by_ip
from backend.core.http.ratelimit import rate_limit
from backend.core.http.router import Router
from backend.core.validation.requests import validate
from backend.domain.schemas import auth as s

routes = Router()

_sign_in_limit = rate_limit(limit=300, window_seconds=600, key_for=by_ip)
_refresh_limit = rate_limit(limit=2_000, window_seconds=600, key_for=by_ip)

routes.post("/staff/login", _sign_in_limit, validate(body=s.staff_login_body), staff_auth.login)
routes.post("/staff/refresh", _refresh_limit, validate(body=s.staff_refresh_body), staff_auth.refresh)
routes.post("/staff/logout", validate(body=s.staff_refresh_body), staff_auth.logout)
routes.get("/staff/me", require_auth, staff_auth.me)
routes.post(
    "/staff/password", require_auth, _sign_in_limit, validate(body=s.staff_password_body), staff_auth.change_password
)
routes.post("/staff/2fa", _sign_in_limit, validate(body=s.staff_two_factor_body), staff_auth.second_factor)
routes.post("/staff/2fa/setup", require_auth, _sign_in_limit, staff_auth.two_factor_setup)
routes.post(
    "/staff/2fa/enable",
    require_auth,
    _sign_in_limit,
    validate(body=s.staff_two_factor_enable_body),
    staff_auth.two_factor_enable,
)
routes.get("/staff/chambers", require_auth, staff_auth.chambers)

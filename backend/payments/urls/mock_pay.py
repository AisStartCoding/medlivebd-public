"""The simulated payment page (port of `routes/mockPay.routes.ts`; mounted with PAYMENT_PROVIDER=mock only)."""

from backend.payments.views import mock_pay as mock_pay
from backend.core.http.router import Router
from backend.core.validation.schema import z
from backend.core.validation.requests import validate

routes = Router()

_params = z.object({"checkoutId": z.string().regex(r"^mock_[0-9a-f-]{36}$")})
_outcome_params = _params.extend({"outcome": z.enum(["paid", "failed", "cancelled"])})

routes.get("/mock-pay/:checkoutId", validate(params=_params), mock_pay.page)
routes.get("/mock-pay/:checkoutId/:outcome", validate(params=_outcome_params), mock_pay.settle)

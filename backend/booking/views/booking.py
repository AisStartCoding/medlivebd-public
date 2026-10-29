"""Booking controllers (port of `controllers/booking.controller.ts`; FR-PAT-20, FR-GST-01, FR-PAT-33)."""

from __future__ import annotations

from typing import Any

from backend.core.http.errors import AppError
from backend.core.http.errors import auth_required
from backend.core.http.errors import forbidden_scope
from backend.core.http.errors import validation_failed
from backend.core.http.types import ApiRequest
from backend.core.http.types import Reply
from backend.core.http.types import ok
from backend.booking.services import booking as booking
from backend.identity.services import patient_auth as patient_auth
from backend.platform_admin.services.deployment import method_available
from backend.queues.views.queue import actor_of
from backend.queues.views.queue import assert_booking_scope
from backend.queues.views.queue import queue_answer


def create_booking(req: ApiRequest) -> Reply:
    body = req.body
    if not method_available(body["method"]):
        raise AppError("PAYMENT_UNAVAILABLE", details={"method": body["method"]})
    principal = req.principal
    if (principal is None or principal.kind != "patient") and "guest" in body:
        patient_auth.assert_guest_phone_proven(principal, body["guest"]["phone"])
    result = booking.create_booking(
        session_id=body["sessionId"],
        booker=_booker_from(req, body),
        method=body["method"],
        reason=body.get("reason"),
        intake=body.get("intake"),
        arrival_window_start=body.get("arrivalWindowStart"),
        client_event_id=req.idempotency_key,
    )
    return ok(result, status=200 if result["duplicate"] else 201)


def _booker_from(req: ApiRequest, body: dict[str, Any]) -> dict[str, Any]:
    principal = req.principal
    if principal is not None and principal.kind == "patient":
        if "patientId" not in body:
            raise validation_failed({"field": "patientId", "reason": "required_when_signed_in"})
        return {"kind": "user", "userId": principal.id, "patientId": body["patientId"]}
    if "guest" not in body:
        raise validation_failed({"field": "guest", "reason": "required_without_an_account"})
    guest = body["guest"]
    return {
        "kind": "guest",
        "phone": guest["phone"],
        "name": guest["name"],
        "ageYears": guest["ageYears"],
        "sex": guest["sex"],
    }


def _account_of(req: ApiRequest) -> str:
    principal = req.principal
    if principal is None:
        raise auth_required()
    if principal.kind != "patient":
        raise forbidden_scope({"reason": "account_only"})
    return principal.id


def my_bookings(req: ApiRequest) -> Reply:
    return ok(booking.my_bookings(_account_of(req)))


def my_booking_link(req: ApiRequest) -> Reply:
    return ok(booking.link_for_my_booking(_account_of(req), req.params["id"]), status=201)


def get_booking(req: ApiRequest) -> Reply:
    assert_booking_scope(req)
    audience = "staff" if req.principal is not None and req.principal.kind == "staff" else "patient"
    return ok(booking.booking_view(req.params["id"], audience))


def cancel_booking(req: ApiRequest) -> Reply:
    body = req.body
    assert_booking_scope(req)
    result = booking.cancel_booking(
        booking_id=req.params["id"],
        actor=actor_of(req),
        reason=body.get("reason"),
        client_event_id=body.get("clientEventId"),
        client_ts=body.get("clientTs"),
    )
    return ok(queue_answer(req, result))

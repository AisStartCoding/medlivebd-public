"""Clinical controllers (port of `controllers/clinical.controller.ts`; FR-DOC-*, FR-PAT-40, FR-PAT-6x)."""

from __future__ import annotations

from typing import Any

from medlive.core.errors import auth_required
from medlive.core.http import ApiRequest
from medlive.core.http import Reply
from medlive.core.http import ok
from medlive.modules.clinical.services import clinical as clinical
from medlive.modules.queue.views.queue import actor_of


def _principal_of(req: ApiRequest) -> Any:
    principal = req.principal
    if principal is None:
        raise auth_required()
    return principal


def get_records(req: ApiRequest) -> Reply:
    principal = _principal_of(req)
    return ok(
        clinical.patient_records(
            principal=principal, patient_id=req.params["id"], booking_id=req.query.get("booking")
        )
    )


def create_visit(req: ApiRequest) -> Reply:
    principal = _principal_of(req)
    return ok(clinical.save_visit(principal=principal, actor=actor_of(req), body=req.body), status=201)


def get_consultation(req: ApiRequest) -> Reply:
    principal = _principal_of(req)
    return ok(clinical.consultation(principal, req.params["id"]))


def search_formulary(req: ApiRequest) -> Reply:
    return ok({"medicines": clinical.formulary(req.query["q"])})


def upload_document(req: ApiRequest) -> Reply:
    principal = _principal_of(req)
    return ok({"document": clinical.upload_document(principal, req.body)}, status=201)


def list_documents(req: ApiRequest) -> Reply:
    principal = _principal_of(req)
    return ok({"documents": clinical.list_own_documents(principal, req.query["patient"])})


def remove_document(req: ApiRequest) -> Reply:
    principal = _principal_of(req)
    clinical.remove_own_document(principal, req.params["id"])
    return ok({"removed": True})


def document_url(req: ApiRequest) -> Reply:
    principal = _principal_of(req)
    return ok(
        {
            "url": clinical.document_url(
                principal=principal, patient_id=req.params["id"], document_id=req.params["docId"]
            )
        }
    )

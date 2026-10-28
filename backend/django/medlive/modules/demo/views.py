"""Demonstration picker controllers (port of `controllers/demo.controller.ts`; CLAUDE.md §4.1)."""

from __future__ import annotations

from medlive.core.http import ApiRequest
from medlive.core.http import Reply
from medlive.core.http import ok
from medlive.modules.demo import services as demo


def status(req: ApiRequest) -> Reply:
    return ok(demo.status())


def list_consoles(req: ApiRequest) -> Reply:
    return ok({"consoles": demo.list_consoles(), "national": demo.list_national_consoles()})


def mint_token(req: ApiRequest) -> Reply:
    body = req.body
    if "hospitalId" in body:
        return ok(demo.mint_principal(hospital_id=body["hospitalId"], role=body["role"]))
    return ok(demo.mint_national_principal(role=body["role"]))

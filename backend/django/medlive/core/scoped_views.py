"""DRF resource views inside the existing scoped pipeline (FR-SEC-11).

This bridge is not a URL entry point. Route guards run first, then DRF dispatch
and serializer helpers, then the existing Reply/security/error renderer. SQL
dictionaries deliberately never enter ORM filtering or pagination backends.
"""

from contextvars import ContextVar
from typing import Any

from django.http import HttpResponse
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import BasePermission

from .http import ApiRequest, Reply
from .pipeline import _AlwaysPassThrough, _PassThroughRenderer

_active: ContextVar[ApiRequest | None] = ContextVar("scoped_view_request", default=None)


class PipelinePermission(BasePermission):
    def has_permission(self, request: Any, view: Any) -> bool:
        return _active.get() is not None and _active.get() is view.kwargs.get("scoped_request")


class ScopedGenericAPIView(GenericAPIView):
    # Authentication, rate limits, RLS and route policies have already run.
    # The permission below rejects mounting this view directly outside that chain.
    authentication_classes: list[Any] = []
    permission_classes = [PipelinePermission]
    throttle_classes: list[Any] = []
    renderer_classes = [_PassThroughRenderer]
    content_negotiation_class = _AlwaysPassThrough
    http_method_names = ["get", "head"]

    @property
    def default_response_headers(self) -> dict[str, str]:
        return {}

    def handle_exception(self, exc: Exception) -> HttpResponse:
        raise exc  # The single pipeline error translator preserves public codes.


def reply_response(reply: Reply) -> HttpResponse:
    response = HttpResponse(status=reply.status)
    response.pipeline_reply = reply
    return response


def scoped_handler(view_type: type[ScopedGenericAPIView]) -> Any:
    view = view_type.as_view()

    def handle(req: ApiRequest) -> Reply:
        token = _active.set(req)
        try:
            response = view(req.django, scoped_request=req)
            return response.pipeline_reply
        finally:
            _active.reset(token)

    return handle

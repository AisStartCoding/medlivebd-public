"""Public discovery (port of `controllers/discovery.controller.ts`). No account needed (GR-08)."""

from __future__ import annotations

from backend.core.env import env
from backend.core.http.errors import not_found
from backend.core.http.types import ApiRequest
from backend.core.http.types import Reply
from backend.core.http.types import ok
from backend.core.http.types import raw_reply
from backend.platform_admin.services import deployment as deployment
from backend.catalog import services as discovery
from backend.platform_admin.services import portal as portals


def get_hospital(req: ApiRequest) -> Reply:
    return ok(discovery.hospital_detail(req.params["id"]))


def get_hospital_doctors(req: ApiRequest) -> Reply:
    specialty = req.query_raw.get("specialty")
    result = discovery.doctors_at(req.params["id"], specialty if isinstance(specialty, str) else None)
    return ok({"doctors": result["items"], "asOf": result["asOf"]})


def get_doctor(req: ApiRequest) -> Reply:
    return ok(discovery.doctor_detail(req.params["id"]))


def get_availability(req: ApiRequest) -> Reply:
    return ok(discovery.availability(req.params["id"]))


def get_config(req: ApiRequest) -> Reply:
    """What this deployment offers, and whose address the app was opened at (FR-BRD-07)."""
    scope = req.query.get("scope")
    host = req.query.get("host")
    address = None if host is None else portals.address_of(host)
    at_portal = address.code if address is not None and address.kind == "portal" else None
    code = at_portal if at_portal is not None else scope
    scoped = None if code is None else discovery.scope_info(code)
    data = {**deployment.public_config(), "address": "network" if address is None else address.kind}
    if address is not None and address.kind == "nobodys":
        data["networkUrl"] = env().WEB_BASE_URL
    data["scope"] = (
        None
        if scoped is None
        else {
            "code": scoped["code"],
            "hospitalId": scoped["hospitalId"],
            "nameBn": scoped["nameBn"],
            "nameEn": scoped["nameEn"],
            "theme": scoped["theme"],
            "descriptionBn": scoped["descriptionBn"],
            "descriptionEn": scoped["descriptionEn"],
            "logoVersion": scoped["logoVersion"],
            "logoImage": scoped["logoImage"],
            "modulesOff": scoped["modulesOff"],
            "notShared": scoped["notShared"],
            "byAddress": at_portal is not None,
        }
    )
    return ok(data)


def get_logo(req: ApiRequest) -> Reply:
    file = discovery.logo(req.params["id"])
    if file is None:
        raise not_found("logo")
    version = req.query_raw.get("v")
    return raw_reply(
        file["bytes"],
        file["contentType"],
        headers={
            "Cache-Control": "public, max-age=31536000, immutable"
            if version == file["version"]
            else "public, max-age=300",
            "Cross-Origin-Resource-Policy": "cross-origin",
        },
    )


from backend.core.http.scoped_views import ScopedGenericAPIView
from backend.core.http.scoped_views import reply_response
from backend.core.http.scoped_views import scoped_handler
from backend.catalog.serializers import HospitalQuerySerializer
from backend.catalog.serializers import DoctorQuerySerializer
from backend.catalog.serializers import SearchQuerySerializer
from backend.catalog.serializers import SessionQuerySerializer


class HospitalListView(ScopedGenericAPIView):
    serializer_class = HospitalQuerySerializer

    def get(self, request, *, scoped_request):
        query = self.get_serializer(data=scoped_request.query_raw)
        query.is_valid(raise_exception=True)
        result = discovery.search_hospitals(query.validated_data)
        return reply_response(ok({"hospitals": result["items"], "asOf": result["asOf"]}))


class DoctorListView(ScopedGenericAPIView):
    serializer_class = DoctorQuerySerializer

    def get(self, request, *, scoped_request):
        query = self.get_serializer(data=scoped_request.query_raw)
        query.is_valid(raise_exception=True)
        return reply_response(ok({"doctors": discovery.search_doctors(query.validated_data)}))


class SearchView(ScopedGenericAPIView):
    serializer_class = SearchQuerySerializer

    def get(self, request, *, scoped_request):
        query = self.get_serializer(data=scoped_request.query_raw)
        query.is_valid(raise_exception=True)
        return reply_response(ok(discovery.search(query.validated_data)))


class SessionListView(ScopedGenericAPIView):
    serializer_class = SessionQuerySerializer

    def get(self, request, *, scoped_request):
        query = self.get_serializer(data=scoped_request.query_raw)
        query.is_valid(raise_exception=True)
        return reply_response(ok({"sessions": discovery.sessions_for(query.validated_data)}))


list_hospitals = scoped_handler(HospitalListView)
list_doctors = scoped_handler(DoctorListView)
search = scoped_handler(SearchView)
list_sessions = scoped_handler(SessionListView)

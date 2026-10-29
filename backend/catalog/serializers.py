"""SQL catalog query inputs with the established coercion/error contract.

Use the canonical schemas rather than defining a second subtly different set
of bounds, unknown-field rules or messages (FR-PAT-16, GR-08).
"""

from rest_framework import serializers

from backend.core.http.errors import validation_failed
from backend.domain.schemas import booking


class CatalogQuerySerializer(serializers.Serializer):
    schema = None

    def to_internal_value(self, data):
        result = self.schema.safe_parse(data)
        if not result.success:
            raise validation_failed({"issues": [
                {"path": ".".join(["query", *(str(p) for p in issue["path"])]), "message": issue["message"]}
                for issue in result.issues
            ]})
        return result.data


class HospitalQuerySerializer(CatalogQuerySerializer):
    schema = booking.hospital_query


class DoctorQuerySerializer(CatalogQuerySerializer):
    schema = booking.doctor_query


class SearchQuerySerializer(CatalogQuerySerializer):
    schema = booking.search_query


class SessionQuerySerializer(CatalogQuerySerializer):
    schema = booking.session_query

"""Catalog DRF, bounds and SQL read shape (FR-PAT-16, FR-SUP-02, NFR-01)."""

import pytest
from django.test import RequestFactory
from rest_framework.exceptions import PermissionDenied

from backend.core.database import connection as db
from backend.core.observability.performance import observe_sql
from backend.catalog import services
from backend.catalog.views import HospitalListView

from backend.tests.api.conftest import Api


def test_resource_view_cannot_be_mounted_without_the_scoped_pipeline() -> None:
    with pytest.raises(PermissionDenied):
        HospitalListView.as_view()(RequestFactory().get("/hospitals"))


@pytest.mark.parametrize("query", ["limit=101", "limit=-1", "lat=0", "limit=2&limit=3"])
def test_catalog_serializer_preserves_filter_errors(api: Api, query: str) -> None:
    response = api.call("GET", f"/hospitals?{query}")
    assert response.status == 400
    assert response.body["error"]["code"] == "VALIDATION_FAILED"
    assert response.body["error"]["details"]["issues"][0]["path"].startswith("query.")


def test_hospital_query_count_does_not_grow_per_card(api: Api) -> None:
    counts = []
    for limit in [1, 100]:
        with observe_sql() as metrics:
            # Direct service measurement excludes request/security reads, which are separately logged.
            result = services.search_hospitals({"limit": limit})
        assert len(result["items"]) <= limit
        counts.append(metrics.count)
    assert counts == [2, 2]


def test_doctor_detail_reads_one_matching_doctor() -> None:
    doctor_id = db.fetch_value("SELECT id FROM doctors WHERE deleted_at IS NULL AND bmdc_verified_at IS NOT NULL LIMIT 1")
    with observe_sql() as metrics:
        result = services.doctor_detail(doctor_id)
    assert result["doctor"]["id"] == doctor_id
    # Exactly one doctor plus that doctor's returned sessions, never the catalog.
    assert metrics.rows == 1 + len(result["sessions"])
    assert metrics.count == 2

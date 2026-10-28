"""Online queue stamps share the event log's clock (FR-REC-02, DB-P4)."""

from datetime import datetime, timezone

import pytest

from medlive.core import db
from medlive.domain.time import clock_at

from .conftest import Api, create_queue_fixture, staff_token


@pytest.mark.parametrize("offset_ms", [-60_000, 60_000])
def test_arrive_then_end_survives_application_clock_skew(api: Api, offset_ms: int) -> None:
    fixture = create_queue_fixture(1)
    token = staff_token(fixture.receptionist_id, fixture.hospital_id, ["receptionist"])
    with clock_at(datetime.now(timezone.utc).timestamp() * 1000 + offset_ms):
        arrived = api.call("POST", f"/sessions/{fixture.session_id}/arrived", token=token, body={})
        assert arrived.status == 200
        ended = api.call("POST", f"/sessions/{fixture.session_id}/end", token=token, body={"reason": None})
        assert ended.status == 200
    row = db.fetch_one("SELECT actual_start, actual_end FROM sessions WHERE id = %s", [fixture.session_id])
    assert row is not None
    assert row["actual_end"] >= row["actual_start"]

"""Operational metrics never need SQL rows, principal ids or credentials (FR-SEC-08)."""

import json
import logging
import sys

from medlive.core.logging import JsonFormatter
from medlive.core.performance import observe_sql, record_sql


def test_exception_diagnostics_exclude_driver_message_and_values() -> None:
    private_message = "synthetic-private-row-and-token"
    try:
        raise RuntimeError(private_message)
    except RuntimeError:
        record = logging.LogRecord("medlive", logging.ERROR, __file__, 1, "unhandled error", (), sys.exc_info())
    result = json.loads(JsonFormatter().format(record))
    assert result["err"]["type"] == "RuntimeError"
    assert private_message not in json.dumps(result)


def test_sql_observation_is_scoped_and_nested_observers_do_not_corrupt_parent() -> None:
    with observe_sql() as parent:
        record_sql(2.5, 1)
        with observe_sql() as child:
            record_sql(1, 3)
        record_sql(3, 2)
    assert (parent.count, parent.rows, parent.milliseconds) == (2, 3, 5.5)
    assert (child.count, child.rows) == (1, 3)

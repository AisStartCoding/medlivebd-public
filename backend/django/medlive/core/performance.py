"""Request-local SQL metrics without statements, parameters or identifiers (NFR-01)."""

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Iterator


@dataclass
class SqlMetrics:
    count: int = 0
    milliseconds: float = 0
    rows: int = 0


_metrics: ContextVar[SqlMetrics | None] = ContextVar("sql_metrics", default=None)


@contextmanager
def observe_sql() -> Iterator[SqlMetrics]:
    metrics = SqlMetrics()
    token = _metrics.set(metrics)
    try:
        yield metrics
    finally:
        _metrics.reset(token)


def record_sql(milliseconds: float, rows: int) -> None:
    metrics = _metrics.get()
    if metrics is not None:
        metrics.count += 1
        metrics.milliseconds += milliseconds
        metrics.rows += max(rows, 0)


def sql_metrics() -> dict[str, int | float]:
    metrics = _metrics.get()
    if metrics is None:
        return {}
    return {"sqlCount": metrics.count, "sqlMs": round(metrics.milliseconds, 2), "sqlRows": metrics.rows}

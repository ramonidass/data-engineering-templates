"""Pure transforms: no files, network, environment, clocks, or global state."""

from collections.abc import Iterable
from datetime import date
from decimal import Decimal

from .models import DailyTotal, Event


def deduplicate_latest(events: Iterable[Event]) -> list[Event]:
    """Retain the latest event per ID, with a deterministic value tie-breaker."""
    latest: dict[str, Event] = {}
    for event in events:
        current = latest.get(event.event_id)
        if current is None or (event.occurred_at, event.value) > (
            current.occurred_at,
            current.value,
        ):
            latest[event.event_id] = event
    return sorted(
        latest.values(),
        key=lambda event: (event.occurred_at, event.event_id),
    )


def daily_totals(events: Iterable[Event]) -> list[DailyTotal]:
    totals: dict[date, tuple[int, Decimal]] = {}
    for event in events:
        day = event.occurred_at.date()
        count, value = totals.get(day, (0, Decimal(0)))
        totals[day] = (count + 1, value + event.value)
    return [
        DailyTotal(event_date=day, event_count=count, total_value=value)
        for day, (count, value) in sorted(totals.items())
    ]

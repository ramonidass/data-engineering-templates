"""Ports keep orchestration independent from infrastructure adapters."""

from collections.abc import Iterable
from typing import Protocol

from .models import DailyTotal, Event


class EventSource(Protocol):
    def read(self) -> Iterable[Event]: ...


class DailyTotalSink(Protocol):
    def write(self, records: Iterable[DailyTotal]) -> int: ...

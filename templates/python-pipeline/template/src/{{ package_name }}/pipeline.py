"""Pipeline orchestration: compose ports and report observable run statistics."""

from dataclasses import dataclass

from .ports import DailyTotalSink, EventSource
from .transforms import daily_totals, deduplicate_latest


@dataclass(frozen=True)
class PipelineResult:
    input_count: int
    duplicate_count: int
    output_count: int


def run_pipeline(source: EventSource, sink: DailyTotalSink) -> PipelineResult:
    events = list(source.read())
    deduplicated = deduplicate_latest(events)
    output_count = sink.write(daily_totals(deduplicated))
    return PipelineResult(
        input_count=len(events),
        duplicate_count=len(events) - len(deduplicated),
        output_count=output_count,
    )

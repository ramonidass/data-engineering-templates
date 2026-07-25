"""Structured Streaming transforms, kept separate from source/sink wiring."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as sf

from .schemas import EVENT_SCHEMA


def parse_kafka_events(df: DataFrame) -> DataFrame:
    """Parse Kafka's binary ``value`` as an event JSON document."""
    parsed = df.select(
        sf.from_json(sf.col("value").cast("string"), EVENT_SCHEMA).alias("event")
    )
    events = parsed.select("event.*")
    # In permissive JSON mode a malformed payload can become a struct whose
    # fields are all null, so checking only the struct itself is insufficient.
    return events.where(
        sf.col("event_id").isNotNull() & sf.col("occurred_at").isNotNull()
    )


def streaming_daily_totals(
    events: DataFrame,
    *,
    watermark_delay: str = "10 minutes",
) -> DataFrame:
    """Deduplicate bounded state and emit final event-time daily windows."""
    deduplicated = events.withWatermark(
        "occurred_at", watermark_delay
    ).dropDuplicatesWithinWatermark(["event_id"])
    return (
        deduplicated.groupBy(sf.window("occurred_at", "1 day"))
        .agg(
            sf.count("*").alias("event_count"),
            sf.coalesce(sf.sum("value"), sf.lit(0.0)).alias("total_value"),
        )
        .select(
            sf.to_date(sf.col("window.start")).alias("event_date"),
            "event_count",
            "total_value",
        )
    )

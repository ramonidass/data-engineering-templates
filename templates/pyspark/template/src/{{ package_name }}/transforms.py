"""Pure DataFrame -> DataFrame transformations.

Rules that keep this testable:
- No I/O here — reading and writing happen only in jobs/.
- No SparkSession arguments — transforms operate on the DataFrames they get.
- Each function does one thing and is unit-tested in tests/test_transforms.py.
"""

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F


def deduplicate_events(df: DataFrame) -> DataFrame:
    """Keep the latest record per event_id."""
    return df.orderBy(F.col("occurred_at").desc()).dropDuplicates(["event_id"])


def daily_totals(df: DataFrame) -> DataFrame:
    """Aggregate event values per calendar day."""
    event_date: Column = F.to_date("occurred_at").alias("event_date")
    return (
        df.groupBy(event_date)
        .agg(
            F.count("*").alias("event_count"),
            F.sum("value").alias("total_value"),
        )
        .orderBy("event_date")
    )

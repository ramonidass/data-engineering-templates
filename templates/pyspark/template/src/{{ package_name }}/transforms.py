"""Pure DataFrame -> DataFrame transformations.

Rules that keep this testable:
- No I/O here — reading and writing happen only in jobs/.
- No SparkSession arguments — transforms operate on the DataFrames they get.
- Each function does one thing and is unit-tested in tests/test_transforms.py.
"""

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as sf
from pyspark.sql.window import Window


def require_columns(df: DataFrame, required: set[str]) -> None:
    """Fail at the boundary with a useful contract error."""
    missing = required.difference(df.columns)
    if missing:
        names = ", ".join(sorted(missing))
        raise ValueError(f"missing required columns: {names}")


def deduplicate_events(df: DataFrame) -> DataFrame:
    """Keep the latest record per event_id deterministically.

    A global ``orderBy().dropDuplicates()`` is not safe: the deduplication
    shuffle does not promise to preserve the earlier ordering. Use a window,
    with an explicit tie-breaker, whenever the retained row matters.
    """
    require_columns(df, {"event_id", "occurred_at", "value"})
    latest_first = Window.partitionBy("event_id").orderBy(
        sf.col("occurred_at").desc_nulls_last(),
        # Replace this example tie-breaker with source sequence/ingestion time
        # when the source supplies one.
        sf.col("value").desc_nulls_last(),
    )
    return (
        df.withColumn("_row_number", sf.row_number().over(latest_first))
        .where(sf.col("_row_number") == 1)
        .drop("_row_number")
    )


def daily_totals(df: DataFrame) -> DataFrame:
    """Aggregate event values per calendar day."""
    require_columns(df, {"occurred_at", "value"})
    event_date: Column = sf.to_date("occurred_at").alias("event_date")
    return (
        df.groupBy(event_date)
        .agg(
            sf.count("*").alias("event_count"),
            sf.coalesce(sf.sum("value"), sf.lit(0.0)).alias("total_value"),
        )
        .orderBy("event_date")
    )

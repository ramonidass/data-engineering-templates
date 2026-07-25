"""Explicit schemas for every dataset the jobs read or write.

Never rely on schema inference in production reads: it is slow and silently
drifts. Pair each Spark schema with a pydantic model when rows cross a
non-Spark boundary (APIs, config, fixtures).
"""

from datetime import datetime

from pydantic import BaseModel
from pyspark.sql import types as st

EVENT_SCHEMA = st.StructType(
    [
        st.StructField("event_id", st.StringType(), nullable=False),
        st.StructField("occurred_at", st.TimestampType(), nullable=False),
        st.StructField("value", st.DoubleType(), nullable=True),
    ]
)


class Event(BaseModel):
    """One input event; mirrors EVENT_SCHEMA for use outside Spark."""

    event_id: str
    occurred_at: datetime
    value: float | None = None

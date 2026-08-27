"""
Patterns worth keeping:
- `frozen=True` for value objects; mutation happens by constructing new
  instances, which keeps models safe to share across threads and caches.
- Constrain at the field level (`Field(ge=..., pattern=...)`) so invalid data
  cannot be constructed at all.
"""

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class RecordStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class ExampleRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1, max_length=200)
    status: RecordStatus = RecordStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def archived(self) -> "ExampleRecord":
        """Return a copy of this record in the archived state."""
        return self.model_copy(update={"status": RecordStatus.ARCHIVED})

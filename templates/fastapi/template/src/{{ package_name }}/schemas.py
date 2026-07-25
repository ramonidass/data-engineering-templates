"""API request/response models.

Conventions:
- One `*Create` / `*Update` model per writable resource, one read model with
  server-generated fields (id, timestamps).
- Validate at the edge: constraints live here, not scattered through handlers.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ItemCreate(BaseModel):
    """Payload to create an Item. Replace with your first real resource."""

    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    quantity: int = Field(default=0, ge=0)


class Item(ItemCreate):
    """An Item as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class HealthStatus(BaseModel):
    status: str
    version: str

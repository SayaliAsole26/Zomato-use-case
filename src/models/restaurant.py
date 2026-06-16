from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CostTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RestaurantRecord(BaseModel):
    """Canonical restaurant record after preprocessing."""

    id: str
    name: str
    location: str
    cuisines: list[str] = Field(default_factory=list)
    rating: float | None = None
    cost_for_two: int | None = None
    cost_tier: CostTier | None = None
    address: str | None = None
    votes: int | None = None
    raw: dict[str, Any] | None = None

    model_config = {"frozen": True}

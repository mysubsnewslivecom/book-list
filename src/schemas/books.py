from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# -------------------------
# Base schema (shared fields)
# -------------------------
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    status: str = Field(default="available", min_length=1, max_length=50)

    model_config = ConfigDict(extra="forbid")  # prevents additionalProp1 etc.


# -------------------------
# Create schema (POST)
# -------------------------
class BookCreate(BookBase):
    pass


# -------------------------
# Update schema (PUT/PATCH)
# -------------------------
class BookUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    author: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    status: str | None = Field(None, min_length=1, max_length=50)

    model_config = ConfigDict(extra="forbid")


# -------------------------
# Response schema (API output)
# -------------------------
class BookOut(BookBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

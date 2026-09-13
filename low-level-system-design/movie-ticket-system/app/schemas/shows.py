from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import field_validator, model_validator
from sqlmodel import SQLModel

from app.models.entities import ShowSeatStatus, ShowStatus


class ShowCreate(SQLModel):
    movie_id: UUID
    auditorium_id: UUID
    starts_at: datetime
    ends_at: datetime
    base_price: Decimal

    @model_validator(mode="after")
    def validate_times(self) -> "ShowCreate":
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")

        if self.base_price < 0:
            raise ValueError("base_price cannot be negative")

        return self


class ShowRead(SQLModel):
    id: UUID
    movie_id: UUID
    auditorium_id: UUID
    starts_at: datetime
    ends_at: datetime
    base_price: Decimal
    status: ShowStatus


class ShowSeatRead(SQLModel):
    id: UUID
    seat_id: UUID
    row_label: str
    seat_number: int
    price: Decimal
    status: ShowSeatStatus
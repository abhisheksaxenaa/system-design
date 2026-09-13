from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import field_validator
from sqlmodel import SQLModel

from app.models.entities import BookingStatus


class BookingCreate(SQLModel):
    show_id: UUID
    seat_ids: list[UUID]

    @field_validator("seat_ids")
    @classmethod
    def validate_seat_ids(
        cls,
        value: list[UUID],
    ) -> list[UUID]:
        if not value:
            raise ValueError("At least one seat is required")

        if len(value) > 10:
            raise ValueError(
                "At most 10 seats can be booked at once"
            )

        if len(set(value)) != len(value):
            raise ValueError("Duplicate seat IDs are not allowed")

        return value


class BookingConfirm(SQLModel):
    payment_reference: str

    @field_validator("payment_reference")
    @classmethod
    def validate_payment_reference(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError("payment_reference is required")

        if len(value) > 200:
            raise ValueError("payment_reference is too long")

        return value


class BookingSeatRead(SQLModel):
    show_seat_id: UUID
    seat_id: UUID
    price: Decimal


class BookingRead(SQLModel):
    id: UUID
    show_id: UUID
    status: BookingStatus
    total_amount: Decimal
    expires_at: datetime
    payment_reference: str | None
    seats: list[BookingSeatRead]
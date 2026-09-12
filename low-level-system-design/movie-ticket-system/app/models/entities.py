from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Index,
    Numeric,
    UniqueConstraint,
)
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SeatCategory(StrEnum):
    REGULAR = "REGULAR"
    PREMIUM = "PREMIUM"
    RECLINER = "RECLINER"


class ShowStatus(StrEnum):
    SCHEDULED = "SCHEDULED"
    CANCELLED = "CANCELLED"


class ShowSeatStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    HELD = "HELD"
    BOOKED = "BOOKED"


class BookingStatus(StrEnum):
    HELD = "HELD"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class Movie(SQLModel, table=True):
    __tablename__ = "movie"
    __table_args__ = (
        CheckConstraint(
            "duration_minutes > 0",
            name="ck_movie_duration_positive",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=200, index=True)
    duration_minutes: int
    language: str = Field(max_length=50)

    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class Theater(SQLModel, table=True):
    __tablename__ = "theater"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=150)
    city: str = Field(max_length=100, index=True)

    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class Auditorium(SQLModel, table=True):
    __tablename__ = "auditorium"
    __table_args__ = (
        UniqueConstraint(
            "theater_id",
            "name",
            name="uq_auditorium_theater_name",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    theater_id: UUID = Field(
        foreign_key="theater.id",
        index=True,
        nullable=False,
    )

    name: str = Field(max_length=100)

    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class Seat(SQLModel, table=True):
    __tablename__ = "seat"
    __table_args__ = (
        UniqueConstraint(
            "auditorium_id",
            "row_label",
            "seat_number",
            name="uq_seat_location",
        ),
        CheckConstraint(
            "seat_number > 0",
            name="ck_seat_number_positive",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    auditorium_id: UUID = Field(
        foreign_key="auditorium.id",
        index=True,
        nullable=False,
    )

    row_label: str = Field(max_length=10)
    seat_number: int

    category: SeatCategory = Field(default=SeatCategory.REGULAR)

    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class Show(SQLModel, table=True):
    __tablename__ = "show"
    __table_args__ = (
        CheckConstraint(
            "ends_at > starts_at",
            name="ck_show_end_after_start",
        ),
        CheckConstraint(
            "base_price >= 0",
            name="ck_show_price_nonnegative",
        ),
        Index(
            "ix_show_movie_starts",
            "movie_id",
            "starts_at",
        ),
        Index(
            "ix_show_auditorium_starts",
            "auditorium_id",
            "starts_at",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    movie_id: UUID = Field(
        foreign_key="movie.id",
        nullable=False,
    )

    auditorium_id: UUID = Field(
        foreign_key="auditorium.id",
        nullable=False,
    )

    starts_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    ends_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    base_price: Decimal = Field(
        sa_column=Column(Numeric(10, 2), nullable=False),
    )

    status: ShowStatus = Field(default=ShowStatus.SCHEDULED)

    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class Booking(SQLModel, table=True):
    __tablename__ = "booking"
    __table_args__ = (
        UniqueConstraint(
            "idempotency_key",
            name="uq_booking_idempotency_key",
        ),
        UniqueConstraint(
            "payment_reference",
            name="uq_booking_payment_reference",
        ),
        CheckConstraint(
            "total_amount >= 0",
            name="ck_booking_amount_nonnegative",
        ),
        Index("ix_booking_show", "show_id"),
        Index("ix_booking_status", "status"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    show_id: UUID = Field(
        foreign_key="show.id",
        nullable=False,
    )

    status: BookingStatus = Field(default=BookingStatus.HELD)

    total_amount: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(10, 2), nullable=False),
    )

    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    payment_reference: str | None = Field(
        default=None,
        max_length=200,
    )

    idempotency_key: str = Field(
        max_length=200,
        nullable=False,
    )

    request_fingerprint: str = Field(
        max_length=64,
        nullable=False,
    )

    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    def confirm(
        self,
        payment_reference: str,
        now: datetime,
    ) -> None:
        if self.status == BookingStatus.CONFIRMED:
            if self.payment_reference != payment_reference:
                raise ValueError(
                    "Booking is already confirmed with another payment"
                )
            return

        if self.status != BookingStatus.HELD:
            raise ValueError(
                f"Cannot confirm booking in {self.status} state"
            )

        if now >= self.expires_at:
            raise ValueError("Booking hold has expired")

        self.status = BookingStatus.CONFIRMED
        self.payment_reference = payment_reference
        self.updated_at = now

    def cancel(self, now: datetime) -> None:
        if self.status == BookingStatus.CANCELLED:
            return

        if self.status != BookingStatus.HELD:
            raise ValueError(
                f"Cannot cancel booking in {self.status} state"
            )

        self.status = BookingStatus.CANCELLED
        self.updated_at = now

    def expire(self, now: datetime) -> None:
        if self.status != BookingStatus.HELD:
            return

        self.status = BookingStatus.EXPIRED
        self.updated_at = now


class ShowSeat(SQLModel, table=True):
    __tablename__ = "show_seat"
    __table_args__ = (
        UniqueConstraint(
            "show_id",
            "seat_id",
            name="uq_show_seat",
        ),
        CheckConstraint(
            "price >= 0",
            name="ck_show_seat_price_nonnegative",
        ),
        Index(
            "ix_show_seat_show_status",
            "show_id",
            "status",
        ),
        Index(
            "ix_show_seat_hold_expires",
            "hold_expires_at",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    show_id: UUID = Field(
        foreign_key="show.id",
        nullable=False,
    )

    seat_id: UUID = Field(
        foreign_key="seat.id",
        nullable=False,
    )

    price: Decimal = Field(
        sa_column=Column(Numeric(10, 2), nullable=False),
    )

    status: ShowSeatStatus = Field(
        default=ShowSeatStatus.AVAILABLE
    )

    hold_booking_id: UUID | None = Field(
        default=None,
        foreign_key="booking.id",
    )

    hold_expires_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    def is_available(self, now: datetime) -> bool:
        if self.status == ShowSeatStatus.AVAILABLE:
            return True

        if (
            self.status == ShowSeatStatus.HELD
            and self.hold_expires_at is not None
            and self.hold_expires_at <= now
        ):
            return True

        return False

    def hold(
        self,
        booking_id: UUID,
        expires_at: datetime,
        now: datetime,
    ) -> None:
        if not self.is_available(now):
            raise ValueError("Seat is not available")

        self.status = ShowSeatStatus.HELD
        self.hold_booking_id = booking_id
        self.hold_expires_at = expires_at

    def release(self) -> None:
        if self.status == ShowSeatStatus.BOOKED:
            raise ValueError("Booked seat cannot be released")

        self.status = ShowSeatStatus.AVAILABLE
        self.hold_booking_id = None
        self.hold_expires_at = None

    def mark_booked(self, booking_id: UUID) -> None:
        if (
            self.status != ShowSeatStatus.HELD
            or self.hold_booking_id != booking_id
        ):
            raise ValueError("Seat is not held by this booking")

        self.status = ShowSeatStatus.BOOKED
        self.hold_expires_at = None


class BookingSeat(SQLModel, table=True):
    __tablename__ = "booking_seat"

    booking_id: UUID = Field(
        foreign_key="booking.id",
        primary_key=True,
    )

    show_seat_id: UUID = Field(
        foreign_key="show_seat.id",
        primary_key=True,
    )

    price: Decimal = Field(
        sa_column=Column(Numeric(10, 2), nullable=False),
    )
from datetime import (
    datetime,
    timedelta,
    timezone,
)
from decimal import Decimal
from uuid import uuid4

import pytest

from app.models.entities import (
    Booking,
    BookingStatus,
    ShowSeat,
    ShowSeatStatus,
)


def now():
    return datetime.now(timezone.utc)


def test_available_show_seat_can_be_held():
    current = now()

    seat = ShowSeat(
        show_id=uuid4(),
        seat_id=uuid4(),
        price=Decimal("250.00"),
    )

    booking_id = uuid4()

    seat.hold(
        booking_id=booking_id,
        expires_at=current + timedelta(minutes=5),
        now=current,
    )

    assert seat.status == ShowSeatStatus.HELD
    assert seat.hold_booking_id == booking_id


def test_held_seat_cannot_be_held_again():
    current = now()

    seat = ShowSeat(
        show_id=uuid4(),
        seat_id=uuid4(),
        price=Decimal("250.00"),
    )

    seat.hold(
        booking_id=uuid4(),
        expires_at=current + timedelta(minutes=5),
        now=current,
    )

    with pytest.raises(ValueError):
        seat.hold(
            booking_id=uuid4(),
            expires_at=current + timedelta(minutes=5),
            now=current,
        )


def test_expired_hold_is_available():
    current = now()

    seat = ShowSeat(
        show_id=uuid4(),
        seat_id=uuid4(),
        price=Decimal("250.00"),
        status=ShowSeatStatus.HELD,
        hold_booking_id=uuid4(),
        hold_expires_at=(
            current - timedelta(seconds=1)
        ),
    )

    assert seat.is_available(current)


def test_booking_can_be_confirmed():
    current = now()

    booking = Booking(
        show_id=uuid4(),
        total_amount=Decimal("500.00"),
        expires_at=(
            current + timedelta(minutes=5)
        ),
        idempotency_key="abc",
        request_fingerprint="a" * 64,
    )

    booking.confirm(
        payment_reference="pay-1",
        now=current,
    )

    assert booking.status == BookingStatus.CONFIRMED
    assert booking.payment_reference == "pay-1"


def test_expired_booking_cannot_be_confirmed():
    current = now()

    booking = Booking(
        show_id=uuid4(),
        total_amount=Decimal("500.00"),
        expires_at=(
            current - timedelta(seconds=1)
        ),
        idempotency_key="abc",
        request_fingerprint="a" * 64,
    )

    with pytest.raises(ValueError):
        booking.confirm(
            payment_reference="pay-1",
            now=current,
        )
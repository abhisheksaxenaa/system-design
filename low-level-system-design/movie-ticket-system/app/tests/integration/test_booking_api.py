from decimal import Decimal
from uuid import uuid4

from app.domain.pricing import (
    CategoryMultiplierPricing,
)
from app.models.entities import Seat, SeatCategory


def test_premium_pricing():
    seat = Seat(
        auditorium_id=uuid4(),
        row_label="A",
        seat_number=1,
        category=SeatCategory.PREMIUM,
    )

    strategy = CategoryMultiplierPricing()

    assert strategy.price(
        Decimal("200.00"),
        seat,
    ) == Decimal("250.00")


def test_recliner_pricing():
    seat = Seat(
        auditorium_id=uuid4(),
        row_label="A",
        seat_number=1,
        category=SeatCategory.RECLINER,
    )

    strategy = CategoryMultiplierPricing()

    assert strategy.price(
        Decimal("200.00"),
        seat,
    ) == Decimal("300.00")
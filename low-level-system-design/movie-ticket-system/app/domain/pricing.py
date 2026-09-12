from decimal import Decimal
from typing import Protocol

from app.models.entities import Seat, SeatCategory


class SeatPricingStrategy(Protocol):
    def price(
        self,
        base_price: Decimal,
        seat: Seat,
    ) -> Decimal: ...


class CategoryMultiplierPricing:
    _multipliers = {
        SeatCategory.REGULAR: Decimal("1.00"),
        SeatCategory.PREMIUM: Decimal("1.25"),
        SeatCategory.RECLINER: Decimal("1.50"),
    }

    def price(
        self,
        base_price: Decimal,
        seat: Seat,
    ) -> Decimal:
        multiplier = self._multipliers[seat.category]

        return (
            base_price * multiplier
        ).quantize(Decimal("0.01"))
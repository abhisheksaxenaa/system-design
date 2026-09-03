from abc import ABC, abstractmethod

from app.models.movie import Showtime, Seat, SeatTier

class PricingStrategy(ABC):
    @abstractmethod
    def calculate_price(self, showtime: Showtime, seat: Seat) -> float:
        pass

class BaseTierPricingStrategy(PricingStrategy):
    """Calculates price based on seat tier multipliers."""
    TIER_MULTIPLIERS = {
        SeatTier.STANDARD: 1.0,
        SeatTier.PREMIUM: 1.3,
        SeatTier.VIP: 1.8
    }

    def calculate_price(self, showtime: Showtime, seat: Seat) -> float:
        multiplier = self.TIER_MULTIPLIERS.get(seat.tier, 1.0)
        return showtime.base_price * multiplier

class MatineeDiscountStrategy(BaseTierPricingStrategy):
    """Applies a 20% discount for shows starting before 4 PM."""
    def calculate_price(self, showtime: Showtime, seat: Seat) -> float:
        base_calculated = super().calculate_price(showtime, seat)
        if showtime.start_time.hour < 16:
            return base_calculated * 0.8
        return base_calculated

class DemandPopularityStrategy(BaseTierPricingStrategy):
    """Scales price according to the movie's popularity dynamic multiplier."""
    def calculate_price(self, showtime: Showtime, seat: Seat) -> float:
        base_calculated = super().calculate_price(showtime, seat)
        return base_calculated * showtime.popularity_factor

# Context Class
class PricingContext:
    def __init__(self, strategy: PricingStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: PricingStrategy):
        self._strategy = strategy

    def compute(self, showtime: Showtime, seat: Seat) -> float:
        return self._strategy.calculate_price(showtime, seat)

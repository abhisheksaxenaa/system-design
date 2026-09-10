from datetime import datetime
import math

class PricingService:
    """Compute parking fees using a tiered per-hour model.

    Example tiers (from ReadMe):
      - $4 for the first hour
      - $3.5 for the second and third hour
      - $2.5 for every hour after that
    """

    FIRST_HOUR = 4.0
    SECOND_THIRD = 3.5
    REMAINING = 2.5

    def compute_fee(self, entry_time: datetime, exit_time: datetime) -> float:
        if exit_time <= entry_time:
            return 0.0
        delta = exit_time - entry_time
        hours = math.ceil(delta.total_seconds() / 60)
        fee = 0.0
        if hours >= 1:
            fee += self.FIRST_HOUR
        if hours >= 2:
            # second and third
            fee += self.SECOND_THIRD * min(hours - 1, 2)
        if hours > 3:
            fee += self.REMAINING * (hours - 3)
        return round(fee, 2)

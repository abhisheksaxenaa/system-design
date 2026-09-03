import enum


class SeatTier(enum.Enum):
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"
    VIP = "VIP"

class SeatStatus(enum.Enum):
    AVAILABLE = "AVAILABLE"
    LOCKED = "LOCKED"
    BOOKED = "BOOKED"

class BookingStatus(enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

from typing import List, Optional
from sqlmodel import Session, select

from app.models.movie import ShowtimeSeat
from app.models.constants import SeatStatus, BookingStatus
from app.models.movie import Showtime, Seat, Booking
from app.repos.pricing import PricingStrategy, PricingContext

class BookingService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def lock_seats(self, showtime_id: int, seat_ids: List[int]) -> bool:
        """Locks seats for reservation."""
        seats_to_lock = self.db.exec(
            select(ShowtimeSeat).where(
                ShowtimeSeat.showtime_id == showtime_id,
                ShowtimeSeat.seat_id.in_(seat_ids),
                ShowtimeSeat.status == SeatStatus.AVAILABLE,
            )
        ).all()

        if len(seats_to_lock) != len(seat_ids):
            return False  # One or more seats unavailable

        for s in seats_to_lock:
            s.status = SeatStatus.LOCKED
        self.db.commit()
        return True

    def create_booking(
        self, 
        user_id: int, 
        showtime_id: int, 
        seat_ids: List[int], 
        pricing_strategy: PricingStrategy
    ) -> Optional[Booking]:
        
        showtime = self.db.get(Showtime, showtime_id)
        seats = self.db.exec(select(Seat).where(Seat.id.in_(seat_ids))).all()
        
        if not showtime or len(seats) != len(seat_ids):
            return None

        # Price calculation via Strategy Context
        pricing_context = PricingContext(pricing_strategy)
        total_price = sum(pricing_context.compute(showtime, seat) for seat in seats)

        # Create Booking Entity
        booking = Booking(
            user_id=user_id,
            showtime_id=showtime_id,
            total_amount=total_price,
            status=BookingStatus.CONFIRMED
        )
        self.db.add(booking)

        # Update Seat States to BOOKED
        showtime_seats = self.db.exec(
            select(ShowtimeSeat).where(
                ShowtimeSeat.showtime_id == showtime_id,
                ShowtimeSeat.seat_id.in_(seat_ids),
            )
        ).all()

        for st_seat in showtime_seats:
            st_seat.status = SeatStatus.BOOKED

        self.db.commit()
        return booking

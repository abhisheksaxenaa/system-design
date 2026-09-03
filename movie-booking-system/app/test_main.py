import datetime
from sqlmodel import Session, SQLModel, create_engine

from app.models.user import User
from app.models.constants import SeatTier
from app.models.movie import Movie, Screen, Seat, Showtime, ShowtimeSeat
from app.services.booking_service import BookingService
from app.repos.pricing import MatineeDiscountStrategy

if __name__ == "__main__":
    # Setup Engine (Replace with Postgres URL for production: "postgresql://user:pass@localhost/dbname")
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    session = Session(engine)

    # Seed Data
    user = User(name="Alice", email="alice@example.com")
    movie = Movie(title="Inception", duration_minutes=148)
    screen = Screen(name="IMAX Screen 1")
    session.add_all([user, movie, screen])
    session.commit()

    seat_std = Seat(screen_id=screen.id, seat_number="A1", tier=SeatTier.STANDARD)
    seat_vip = Seat(screen_id=screen.id, seat_number="VIP1", tier=SeatTier.VIP)
    session.add_all([seat_std, seat_vip])
    session.commit()

    # Matinee Showtime (1:00 PM) with 1.5x popularity
    matinee_show = Showtime(
        movie_id=movie.id, 
        screen_id=screen.id, 
        start_time=datetime.datetime(2026, 9, 10, 13, 0),
        base_price=10.0,
        popularity_factor=1.5
    )
    session.add(matinee_show)
    session.commit()

    # Initialize seats for showtime
    st_seat1 = ShowtimeSeat(showtime_id=matinee_show.id, seat_id=seat_std.id)
    st_seat2 = ShowtimeSeat(showtime_id=matinee_show.id, seat_id=seat_vip.id)
    session.add_all([st_seat1, st_seat2])
    session.commit()

    # Test Booking with Matinee Discount Strategy
    service = BookingService(session)
    seat_ids = [seat_std.id, seat_vip.id]

    if service.lock_seats(matinee_show.id, seat_ids):
        booking = service.create_booking(
            user_id=user.id,
            showtime_id=matinee_show.id,
            seat_ids=seat_ids,
            pricing_strategy=MatineeDiscountStrategy()
        )
        print(f"Booking Success! Total Calculated Amount: ${booking.total_amount:.2f}")
        # Standard ($10 * 1.0 * 0.8) + VIP ($10 * 1.8 * 0.8) = $8.00 + $14.40 = $22.40
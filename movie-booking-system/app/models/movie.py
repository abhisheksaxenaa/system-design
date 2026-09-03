import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.constants import SeatTier, SeatStatus, BookingStatus


class Movie(SQLModel, table=True):
    __tablename__ = "movies"

    id: int | None = Field(default=None, primary_key=True)
    title: str
    duration_minutes: int


class Seat(SQLModel, table=True):
    __tablename__ = "seats"

    id: int | None = Field(default=None, primary_key=True)
    screen_id: int = Field(foreign_key="screens.id")
    seat_number: str
    tier: SeatTier = Field(default=SeatTier.STANDARD)
    screen: Optional["Screen"] = Relationship(back_populates="seats")


class Screen(SQLModel, table=True):
    __tablename__ = "screens"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    seats: list[Seat] = Relationship(back_populates="screen")


class Showtime(SQLModel, table=True):
    __tablename__ = "showtimes"

    id: int | None = Field(default=None, primary_key=True)
    movie_id: int = Field(foreign_key="movies.id")
    screen_id: int = Field(foreign_key="screens.id")
    start_time: datetime.datetime
    base_price: float
    popularity_factor: float = 1.0
    movie: Optional["Movie"] = Relationship()
    screen: Optional["Screen"] = Relationship()


class ShowtimeSeat(SQLModel, table=True):
    """Tracks seat availability and lock state for a specific showtime."""

    __tablename__ = "showtime_seats"

    id: int | None = Field(default=None, primary_key=True)
    showtime_id: int = Field(foreign_key="showtimes.id")
    seat_id: int = Field(foreign_key="seats.id")
    status: SeatStatus = Field(default=SeatStatus.AVAILABLE)
    seat: Optional["Seat"] = Relationship()
    showtime: Optional["Showtime"] = Relationship()


class Booking(SQLModel, table=True):
    __tablename__ = "bookings"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    showtime_id: int = Field(foreign_key="showtimes.id")
    total_amount: float
    status: BookingStatus = Field(default=BookingStatus.PENDING)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

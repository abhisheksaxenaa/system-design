from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlmodel import Session, select

from app.models.entities import (
    Auditorium,
    Booking,
    BookingSeat,
    Movie,
    Seat,
    Show,
    ShowSeat,
    Theater,
)


class SQLModelCatalogRepository:
    def __init__(self, session: Session):
        self._session = session

    def add_movie(self, movie: Movie) -> None:
        self._session.add(movie)

    def get_movie(self, movie_id: UUID) -> Movie | None:
        return self._session.get(Movie, movie_id)

    def add_theater(self, theater: Theater) -> None:
        self._session.add(theater)

    def get_theater(
        self,
        theater_id: UUID,
    ) -> Theater | None:
        return self._session.get(Theater, theater_id)

    def add_auditorium(
        self,
        auditorium: Auditorium,
    ) -> None:
        self._session.add(auditorium)

    def get_auditorium(
        self,
        auditorium_id: UUID,
    ) -> Auditorium | None:
        return self._session.get(Auditorium, auditorium_id)

    def add_seat(self, seat: Seat) -> None:
        self._session.add(seat)

    def get_seats_for_auditorium(
        self,
        auditorium_id: UUID,
    ) -> list[Seat]:
        statement = (
            select(Seat)
            .where(Seat.auditorium_id == auditorium_id)
            .order_by(
                Seat.row_label,
                Seat.seat_number,
            )
        )

        return list(self._session.exec(statement).all())


class SQLModelShowRepository:
    def __init__(self, session: Session):
        self._session = session

    def add(self, show: Show) -> None:
        self._session.add(show)

    def get(self, show_id: UUID) -> Show | None:
        return self._session.get(Show, show_id)

    def list(
        self,
        movie_id: UUID | None = None,
        starts_from: datetime | None = None,
        starts_until: datetime | None = None,
    ) -> list[Show]:
        statement = select(Show)

        if movie_id is not None:
            statement = statement.where(
                Show.movie_id == movie_id
            )

        if starts_from is not None:
            statement = statement.where(
                Show.starts_at >= starts_from
            )

        if starts_until is not None:
            statement = statement.where(
                Show.starts_at < starts_until
            )

        statement = statement.order_by(Show.starts_at)

        return list(self._session.exec(statement).all())

    def add_show_seats(
        self,
        show_seats: list[ShowSeat],
    ) -> None:
        self._session.add_all(show_seats)

    def get_show_seats(
        self,
        show_id: UUID,
    ) -> list[ShowSeat]:
        statement = (
            select(ShowSeat)
            .where(ShowSeat.show_id == show_id)
            .order_by(ShowSeat.seat_id)
        )

        return list(self._session.exec(statement).all())

    def lock_requested_seats(
        self,
        show_id: UUID,
        seat_ids: list[UUID],
    ) -> list[ShowSeat]:
        statement = (
            select(ShowSeat)
            .where(
                ShowSeat.show_id == show_id,
                ShowSeat.seat_id.in_(seat_ids),
            )
            .with_for_update()
            .order_by(ShowSeat.id)
        )

        return list(self._session.exec(statement).all())


class SQLModelBookingRepository:
    def __init__(self, session: Session):
        self._session = session

    def add(self, booking: Booking) -> None:
        self._session.add(booking)

    def add_booking_seats(
        self,
        items: list[BookingSeat],
    ) -> None:
        self._session.add_all(items)

    def get(
        self,
        booking_id: UUID,
    ) -> Booking | None:
        return self._session.get(Booking, booking_id)

    def get_for_update(
        self,
        booking_id: UUID,
    ) -> Booking | None:
        statement = (
            select(Booking)
            .where(Booking.id == booking_id)
            .with_for_update()
        )

        return self._session.exec(statement).one_or_none()

    def find_by_idempotency_key(
        self,
        key: str,
    ) -> Booking | None:
        statement = select(Booking).where(
            Booking.idempotency_key == key
        )

        return self._session.exec(statement).one_or_none()

    def get_booking_seats(
        self,
        booking_id: UUID,
    ) -> list[BookingSeat]:
        statement = select(BookingSeat).where(
            BookingSeat.booking_id == booking_id
        )

        return list(self._session.exec(statement).all())

    def lock_held_show_seats(
        self,
        booking_id: UUID,
    ) -> list[ShowSeat]:
        statement = (
            select(ShowSeat)
            .where(
                ShowSeat.hold_booking_id == booking_id
            )
            .with_for_update()
            .order_by(ShowSeat.id)
        )

        return list(self._session.exec(statement).all())
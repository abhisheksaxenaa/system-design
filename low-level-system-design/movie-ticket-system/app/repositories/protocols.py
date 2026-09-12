from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

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


class CatalogRepository(Protocol):
    def add_movie(self, movie: Movie) -> None: ...

    def get_movie(self, movie_id: UUID) -> Movie | None: ...

    def add_theater(self, theater: Theater) -> None: ...

    def get_theater(
        self,
        theater_id: UUID,
    ) -> Theater | None: ...

    def add_auditorium(
        self,
        auditorium: Auditorium,
    ) -> None: ...

    def get_auditorium(
        self,
        auditorium_id: UUID,
    ) -> Auditorium | None: ...

    def add_seat(self, seat: Seat) -> None: ...

    def get_seats_for_auditorium(
        self,
        auditorium_id: UUID,
    ) -> list[Seat]: ...


class ShowRepository(Protocol):
    def add(self, show: Show) -> None: ...

    def get(self, show_id: UUID) -> Show | None: ...

    def list(
        self,
        movie_id: UUID | None = None,
        starts_from: datetime | None = None,
        starts_until: datetime | None = None,
    ) -> list[Show]: ...

    def add_show_seats(
        self,
        show_seats: list[ShowSeat],
    ) -> None: ...

    def get_show_seats(
        self,
        show_id: UUID,
    ) -> list[ShowSeat]: ...

    def lock_requested_seats(
        self,
        show_id: UUID,
        seat_ids: list[UUID],
    ) -> list[ShowSeat]: ...


class BookingRepository(Protocol):
    def add(self, booking: Booking) -> None: ...

    def add_booking_seats(
        self,
        items: list[BookingSeat],
    ) -> None: ...

    def get(
        self,
        booking_id: UUID,
    ) -> Booking | None: ...

    def get_for_update(
        self,
        booking_id: UUID,
    ) -> Booking | None: ...

    def find_by_idempotency_key(
        self,
        key: str,
    ) -> Booking | None: ...

    def get_booking_seats(
        self,
        booking_id: UUID,
    ) -> list[BookingSeat]: ...

    def lock_held_show_seats(
        self,
        booking_id: UUID,
    ) -> list[ShowSeat]: ...
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.exceptions.errors import (
    ConflictError,
    EntityNotFound,
    IdempotencyConflict,
    InvalidOperation,
)
from app.models.entities import (
    Booking,
    BookingSeat,
    BookingStatus,
    Seat,
    ShowSeat,
    ShowSeatStatus,
)
from app.repositories.protocols import (
    BookingRepository,
    ShowRepository,
)
from app.schemas.bookings import (
    BookingCreate,
    BookingRead,
    BookingSeatRead,
)


class BookingService:
    def __init__(
        self,
        session: Session,
        booking_repository: BookingRepository,
        show_repository: ShowRepository,
        hold_minutes: int,
    ):
        self._session = session
        self._booking_repository = booking_repository
        self._show_repository = show_repository
        self._hold_minutes = hold_minutes

    def create_hold(
        self,
        data: BookingCreate,
        idempotency_key: str,
    ) -> BookingRead:
        fingerprint = self._fingerprint(data)

        existing = (
            self._booking_repository
            .find_by_idempotency_key(
                idempotency_key
            )
        )

        if existing is not None:
            if (
                existing.request_fingerprint
                != fingerprint
            ):
                raise IdempotencyConflict(
                    "Idempotency key was already used "
                    "with a different request"
                )

            return self._build_read(existing)

        show = self._show_repository.get(data.show_id)

        if show is None:
            raise EntityNotFound("Show not found")

        now = datetime.now(timezone.utc)

        if show.starts_at <= now:
            raise InvalidOperation(
                "Cannot book a show that has started"
            )

        locked_seats = (
            self._show_repository.lock_requested_seats(
                show_id=data.show_id,
                seat_ids=data.seat_ids,
            )
        )

        if len(locked_seats) != len(data.seat_ids):
            raise EntityNotFound(
                "One or more seats do not exist "
                "for this show"
            )

        unavailable: list[UUID] = []

        for show_seat in locked_seats:
            if not show_seat.is_available(now):
                unavailable.append(show_seat.seat_id)

        if unavailable:
            raise ConflictError(
                "One or more requested seats "
                "are unavailable"
            )

        expires_at = now + timedelta(
            minutes=self._hold_minutes
        )

        total = sum(
            (seat.price for seat in locked_seats),
            start=Decimal("0.00"),
        )

        booking = Booking(
            show_id=data.show_id,
            total_amount=total,
            expires_at=expires_at,
            idempotency_key=idempotency_key,
            request_fingerprint=fingerprint,
        )

        try:
            self._booking_repository.add(booking)
            self._session.flush()

            booking_seats: list[BookingSeat] = []

            for show_seat in locked_seats:
                show_seat.hold(
                    booking_id=booking.id,
                    expires_at=expires_at,
                    now=now,
                )

                booking_seats.append(
                    BookingSeat(
                        booking_id=booking.id,
                        show_seat_id=show_seat.id,
                        price=show_seat.price,
                    )
                )

            self._booking_repository.add_booking_seats(
                booking_seats
            )

            self._session.commit()

        except IntegrityError as exc:
            self._session.rollback()

            # Most likely concurrent duplicate
            # idempotency-key request.
            existing = (
                self._booking_repository
                .find_by_idempotency_key(
                    idempotency_key
                )
            )

            if (
                existing is not None
                and existing.request_fingerprint
                == fingerprint
            ):
                return self._build_read(existing)

            raise ConflictError(
                "Booking could not be created"
            ) from exc

        self._session.refresh(booking)

        return self._build_read(booking)

    def confirm(
        self,
        booking_id: UUID,
        payment_reference: str,
    ) -> BookingRead:
        now = datetime.now(timezone.utc)

        booking = (
            self._booking_repository.get_for_update(
                booking_id
            )
        )

        if booking is None:
            raise EntityNotFound("Booking not found")

        show_seats = (
            self._booking_repository
            .lock_held_show_seats(
                booking_id
            )
        )

        if booking.status == BookingStatus.CONFIRMED:
            if (
                booking.payment_reference
                != payment_reference
            ):
                raise ConflictError(
                    "Booking is already confirmed "
                    "with another payment"
                )

            self._session.rollback()
            return self._build_read(booking)

        if booking.status != BookingStatus.HELD:
            raise InvalidOperation(
                f"Booking cannot be confirmed "
                f"from {booking.status}"
            )

        if now >= booking.expires_at:
            booking.expire(now)

            for seat in show_seats:
                if (
                    seat.status == ShowSeatStatus.HELD
                    and seat.hold_booking_id
                    == booking.id
                ):
                    seat.release()

            self._session.commit()

            raise ConflictError(
                "Booking hold has expired"
            )

        if not show_seats:
            raise ConflictError(
                "Booking no longer owns its seats"
            )

        try:
            booking.confirm(
                payment_reference=payment_reference,
                now=now,
            )

            for seat in show_seats:
                seat.mark_booked(booking.id)

            self._session.commit()

        except IntegrityError as exc:
            self._session.rollback()

            raise ConflictError(
                "Payment reference has already been used"
            ) from exc

        self._session.refresh(booking)

        return self._build_read(booking)

    def cancel(
        self,
        booking_id: UUID,
    ) -> BookingRead:
        now = datetime.now(timezone.utc)

        booking = (
            self._booking_repository.get_for_update(
                booking_id
            )
        )

        if booking is None:
            raise EntityNotFound("Booking not found")

        show_seats = (
            self._booking_repository
            .lock_held_show_seats(
                booking_id
            )
        )

        if booking.status == BookingStatus.CANCELLED:
            self._session.rollback()
            return self._build_read(booking)

        try:
            booking.cancel(now)

            for seat in show_seats:
                if (
                    seat.status == ShowSeatStatus.HELD
                    and seat.hold_booking_id
                    == booking.id
                ):
                    seat.release()

            self._session.commit()

        except ValueError as exc:
            self._session.rollback()
            raise InvalidOperation(str(exc)) from exc

        self._session.refresh(booking)

        return self._build_read(booking)

    def get(
        self,
        booking_id: UUID,
    ) -> BookingRead:
        booking = self._booking_repository.get(
            booking_id
        )

        if booking is None:
            raise EntityNotFound("Booking not found")

        return self._build_read(booking)

    def _build_read(
        self,
        booking: Booking,
    ) -> BookingRead:
        booking_seats = (
            self._booking_repository
            .get_booking_seats(booking.id)
        )

        show_seat_ids = [
            item.show_seat_id
            for item in booking_seats
        ]

        if not show_seat_ids:
            seat_reads: list[BookingSeatRead] = []
        else:
            statement = (
                select(ShowSeat, Seat)
                .join(
                    Seat,
                    Seat.id == ShowSeat.seat_id,
                )
                .where(
                    ShowSeat.id.in_(show_seat_ids)
                )
            )

            rows = self._session.exec(statement).all()

            show_seat_by_id = {
                show_seat.id: (
                    show_seat,
                    seat,
                )
                for show_seat, seat in rows
            }

            seat_reads = []

            for booking_seat in booking_seats:
                show_seat, seat = (
                    show_seat_by_id[
                        booking_seat.show_seat_id
                    ]
                )

                seat_reads.append(
                    BookingSeatRead(
                        show_seat_id=show_seat.id,
                        seat_id=seat.id,
                        price=booking_seat.price,
                    )
                )

        return BookingRead(
            id=booking.id,
            show_id=booking.show_id,
            status=booking.status,
            total_amount=booking.total_amount,
            expires_at=booking.expires_at,
            payment_reference=(
                booking.payment_reference
            ),
            seats=seat_reads,
        )

    @staticmethod
    def _fingerprint(
        data: BookingCreate,
    ) -> str:
        payload = {
            "show_id": str(data.show_id),
            "seat_ids": sorted(
                str(value)
                for value in data.seat_ids
            ),
        }

        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()

        return hashlib.sha256(encoded).hexdigest()
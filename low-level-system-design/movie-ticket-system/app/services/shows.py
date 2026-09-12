from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.domain.pricing import SeatPricingStrategy
from app.exceptions.errors import (
    ConflictError,
    DuplicateEntity,
    EntityNotFound,
    InvalidOperation,
)
from app.models.entities import Show, ShowSeat, ShowStatus
from app.repositories.protocols import (
    CatalogRepository,
    ShowRepository,
)
from app.schemas.shows import ShowCreate


class ShowService:
    def __init__(
        self,
        session: Session,
        catalog_repository: CatalogRepository,
        show_repository: ShowRepository,
        pricing_strategy: SeatPricingStrategy,
    ):
        self._session = session
        self._catalog_repository = catalog_repository
        self._show_repository = show_repository
        self._pricing_strategy = pricing_strategy

    def create_show(
        self,
        data: ShowCreate,
    ) -> Show:
        movie = self._catalog_repository.get_movie(
            data.movie_id
        )

        if movie is None:
            raise EntityNotFound("Movie not found")

        auditorium = (
            self._catalog_repository.get_auditorium(
                data.auditorium_id
            )
        )

        if auditorium is None:
            raise EntityNotFound("Auditorium not found")

        seats = (
            self._catalog_repository
            .get_seats_for_auditorium(
                data.auditorium_id
            )
        )

        if not seats:
            raise InvalidOperation(
                "Cannot create a show in an auditorium "
                "without seats"
            )

        if data.starts_at <= datetime.now(timezone.utc):
            raise InvalidOperation(
                "Cannot schedule a show in the past"
            )

        conflicting = [
            existing
            for existing in self._show_repository.list()
            if (
                existing.auditorium_id
                == data.auditorium_id
                and existing.status
                == ShowStatus.SCHEDULED
                and existing.starts_at < data.ends_at
                and existing.ends_at > data.starts_at
            )
        ]

        if conflicting:
            raise ConflictError(
                "Auditorium already has an overlapping show"
            )

        show = Show(**data.model_dump())

        try:
            self._show_repository.add(show)
            self._session.flush()

            show_seats = [
                ShowSeat(
                    show_id=show.id,
                    seat_id=seat.id,
                    price=self._pricing_strategy.price(
                        data.base_price,
                        seat,
                    ),
                )
                for seat in seats
            ]

            self._show_repository.add_show_seats(
                show_seats
            )

            self._session.commit()

        except IntegrityError as exc:
            self._session.rollback()
            raise DuplicateEntity(
                "Unable to create show"
            ) from exc

        self._session.refresh(show)

        return show

    def list_shows(
        self,
        movie_id: UUID | None,
        starts_from: datetime | None,
        starts_until: datetime | None,
    ) -> list[Show]:
        return self._show_repository.list(
            movie_id=movie_id,
            starts_from=starts_from,
            starts_until=starts_until,
        )
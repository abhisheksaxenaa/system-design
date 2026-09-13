from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.exceptions.errors import (
    DuplicateEntity,
    EntityNotFound,
)
from app.models.entities import (
    Auditorium,
    Movie,
    Seat,
    Theater,
)
from app.repositories.protocols import CatalogRepository
from app.schemas.catalog import (
    AuditoriumCreate,
    MovieCreate,
    SeatCreate,
    TheaterCreate,
)


class CatalogService:
    def __init__(
        self,
        session: Session,
        repository: CatalogRepository,
    ):
        self._session = session
        self._repository = repository

    def create_movie(
        self,
        data: MovieCreate,
    ) -> Movie:
        movie = Movie(**data.model_dump())

        self._repository.add_movie(movie)
        self._commit(movie)

        return movie

    def create_theater(
        self,
        data: TheaterCreate,
    ) -> Theater:
        theater = Theater(**data.model_dump())

        self._repository.add_theater(theater)
        self._commit(theater)

        return theater

    def create_auditorium(
        self,
        theater_id: UUID,
        data: AuditoriumCreate,
    ) -> Auditorium:
        if self._repository.get_theater(theater_id) is None:
            raise EntityNotFound("Theater not found")

        auditorium = Auditorium(
            theater_id=theater_id,
            **data.model_dump(),
        )

        self._repository.add_auditorium(auditorium)
        self._commit(auditorium)

        return auditorium

    def create_seat(
        self,
        auditorium_id: UUID,
        data: SeatCreate,
    ) -> Seat:
        if (
            self._repository.get_auditorium(auditorium_id)
            is None
        ):
            raise EntityNotFound("Auditorium not found")

        seat = Seat(
            auditorium_id=auditorium_id,
            **data.model_dump(),
        )

        self._repository.add_seat(seat)
        self._commit(seat)

        return seat

    def _commit(self, entity: object) -> None:
        try:
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise DuplicateEntity(
                "Entity violates a uniqueness constraint"
            ) from exc

        self._session.refresh(entity)
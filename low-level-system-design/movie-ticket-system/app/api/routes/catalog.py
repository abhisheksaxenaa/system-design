from uuid import UUID

from fastapi import APIRouter, status

from app.api.dependencies import CatalogServiceDep
from app.schemas.catalog import (
    AuditoriumCreate,
    AuditoriumRead,
    MovieCreate,
    MovieRead,
    SeatCreate,
    SeatRead,
    TheaterCreate,
    TheaterRead,
)


router = APIRouter(tags=["catalog"])


@router.post(
    "/movies",
    response_model=MovieRead,
    status_code=status.HTTP_201_CREATED,
)
def create_movie(
    body: MovieCreate,
    service: CatalogServiceDep,
) -> MovieRead:
    return MovieRead.model_validate(
        service.create_movie(body)
    )


@router.post(
    "/theaters",
    response_model=TheaterRead,
    status_code=status.HTTP_201_CREATED,
)
def create_theater(
    body: TheaterCreate,
    service: CatalogServiceDep,
) -> TheaterRead:
    return TheaterRead.model_validate(
        service.create_theater(body)
    )


@router.post(
    "/theaters/{theater_id}/auditoriums",
    response_model=AuditoriumRead,
    status_code=status.HTTP_201_CREATED,
)
def create_auditorium(
    theater_id: UUID,
    body: AuditoriumCreate,
    service: CatalogServiceDep,
) -> AuditoriumRead:
    return AuditoriumRead.model_validate(
        service.create_auditorium(
            theater_id,
            body,
        )
    )


@router.post(
    "/auditoriums/{auditorium_id}/seats",
    response_model=SeatRead,
    status_code=status.HTTP_201_CREATED,
)
def create_seat(
    auditorium_id: UUID,
    body: SeatCreate,
    service: CatalogServiceDep,
) -> SeatRead:
    return SeatRead.model_validate(
        service.create_seat(
            auditorium_id,
            body,
        )
    )
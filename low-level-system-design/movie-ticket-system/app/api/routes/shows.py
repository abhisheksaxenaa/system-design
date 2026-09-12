from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, status
from sqlmodel import Session, select

from app.api.dependencies import (
    SessionDep,
    ShowServiceDep,
)
from app.models.entities import Seat, ShowSeat
from app.schemas.shows import (
    ShowCreate,
    ShowRead,
    ShowSeatRead,
)


router = APIRouter(
    prefix="/shows",
    tags=["shows"],
)


@router.post(
    "",
    response_model=ShowRead,
    status_code=status.HTTP_201_CREATED,
)
def create_show(
    body: ShowCreate,
    service: ShowServiceDep,
) -> ShowRead:
    return ShowRead.model_validate(
        service.create_show(body)
    )


@router.get(
    "",
    response_model=list[ShowRead],
)
def list_shows(
    service: ShowServiceDep,
    movie_id: UUID | None = None,
    starts_from: datetime | None = None,
    starts_until: datetime | None = None,
) -> list[ShowRead]:
    shows = service.list_shows(
        movie_id,
        starts_from,
        starts_until,
    )

    return [
        ShowRead.model_validate(show)
        for show in shows
    ]


@router.get(
    "/{show_id}/seats",
    response_model=list[ShowSeatRead],
)
def get_show_seats(
    show_id: UUID,
    session: SessionDep,
) -> list[ShowSeatRead]:
    statement = (
        select(ShowSeat, Seat)
        .join(
            Seat,
            Seat.id == ShowSeat.seat_id,
        )
        .where(ShowSeat.show_id == show_id)
        .order_by(
            Seat.row_label,
            Seat.seat_number,
        )
    )

    rows = session.exec(statement).all()

    return [
        ShowSeatRead(
            id=show_seat.id,
            seat_id=seat.id,
            row_label=seat.row_label,
            seat_number=seat.seat_number,
            price=show_seat.price,
            status=show_seat.status,
        )
        for show_seat, seat in rows
    ]
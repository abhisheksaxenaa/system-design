from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Header,
    status,
)

from app.api.dependencies import BookingServiceDep
from app.schemas.bookings import (
    BookingConfirm,
    BookingCreate,
    BookingRead,
)


router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)


@router.post(
    "",
    response_model=BookingRead,
    status_code=status.HTTP_201_CREATED,
)
def create_booking(
    body: BookingCreate,
    service: BookingServiceDep,
    idempotency_key: Annotated[
        str,
        Header(alias="Idempotency-Key"),
    ],
) -> BookingRead:
    return service.create_hold(
        data=body,
        idempotency_key=idempotency_key,
    )


@router.get(
    "/{booking_id}",
    response_model=BookingRead,
)
def get_booking(
    booking_id: UUID,
    service: BookingServiceDep,
) -> BookingRead:
    return service.get(booking_id)


@router.post(
    "/{booking_id}/confirm",
    response_model=BookingRead,
)
def confirm_booking(
    booking_id: UUID,
    body: BookingConfirm,
    service: BookingServiceDep,
) -> BookingRead:
    return service.confirm(
        booking_id,
        body.payment_reference,
    )


@router.post(
    "/{booking_id}/cancel",
    response_model=BookingRead,
)
def cancel_booking(
    booking_id: UUID,
    service: BookingServiceDep,
) -> BookingRead:
    return service.cancel(booking_id)
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.config import get_settings
from app.db.session import get_session
from app.domain.pricing import CategoryMultiplierPricing
from app.repositories.sqlmodel import (
    SQLModelBookingRepository,
    SQLModelCatalogRepository,
    SQLModelShowRepository,
)
from app.services.bookings import BookingService
from app.services.catalog import CatalogService
from app.services.shows import ShowService


SessionDep = Annotated[
    Session,
    Depends(get_session),
]


def get_catalog_service(
    session: SessionDep,
) -> CatalogService:
    return CatalogService(
        session=session,
        repository=SQLModelCatalogRepository(session),
    )


def get_show_service(
    session: SessionDep,
) -> ShowService:
    return ShowService(
        session=session,
        catalog_repository=(
            SQLModelCatalogRepository(session)
        ),
        show_repository=(
            SQLModelShowRepository(session)
        ),
        pricing_strategy=CategoryMultiplierPricing(),
    )


def get_booking_service(
    session: SessionDep,
) -> BookingService:
    settings = get_settings()

    return BookingService(
        session=session,
        booking_repository=(
            SQLModelBookingRepository(session)
        ),
        show_repository=(
            SQLModelShowRepository(session)
        ),
        hold_minutes=settings.booking_hold_minutes,
    )


CatalogServiceDep = Annotated[
    CatalogService,
    Depends(get_catalog_service),
]

ShowServiceDep = Annotated[
    ShowService,
    Depends(get_show_service),
]

BookingServiceDep = Annotated[
    BookingService,
    Depends(get_booking_service),
]
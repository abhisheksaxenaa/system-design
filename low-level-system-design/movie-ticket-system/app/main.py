from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes.bookings import (
    router as bookings_router,
)
from app.api.routes.catalog import (
    router as catalog_router,
)
from app.api.routes.shows import (
    router as shows_router,
)
from app.exceptions.errors import (
    ConflictError,
    DuplicateEntity,
    EntityNotFound,
    InvalidOperation,
)


app = FastAPI(
    title="Movie Ticket Booking",
    version="1.0.0",
)


@app.exception_handler(EntityNotFound)
async def handle_not_found(
    request: Request,
    exc: EntityNotFound,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "error": "not_found",
            "message": str(exc),
        },
    )


@app.exception_handler(DuplicateEntity)
async def handle_duplicate(
    request: Request,
    exc: DuplicateEntity,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            "error": "duplicate",
            "message": str(exc),
        },
    )


@app.exception_handler(ConflictError)
async def handle_conflict(
    request: Request,
    exc: ConflictError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            "error": "conflict",
            "message": str(exc),
        },
    )


@app.exception_handler(InvalidOperation)
async def handle_invalid_operation(
    request: Request,
    exc: InvalidOperation,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "error": "invalid_operation",
            "message": str(exc),
        },
    )


app.include_router(catalog_router)
app.include_router(shows_router)
app.include_router(bookings_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
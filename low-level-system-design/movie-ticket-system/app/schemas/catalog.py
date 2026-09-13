from uuid import UUID

from sqlmodel import SQLModel

from app.models.entities import SeatCategory


class MovieCreate(SQLModel):
    title: str
    duration_minutes: int
    language: str


class MovieRead(MovieCreate):
    id: UUID


class TheaterCreate(SQLModel):
    name: str
    city: str


class TheaterRead(TheaterCreate):
    id: UUID


class AuditoriumCreate(SQLModel):
    name: str


class AuditoriumRead(AuditoriumCreate):
    id: UUID
    theater_id: UUID


class SeatCreate(SQLModel):
    row_label: str
    seat_number: int
    category: SeatCategory = SeatCategory.REGULAR


class SeatRead(SeatCreate):
    id: UUID
    auditorium_id: UUID
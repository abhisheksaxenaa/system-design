from typing import Optional, List
import enum
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String
from sqlalchemy import Enum as SAEnum


class VehicleType(str, enum.Enum):
    CAR = "car"
    TRUCK = "truck"
    MOTORCYCLE = "motorcycle"


class SpotType(str, enum.Enum):
    COMPACT = "compact"
    LARGE = "large"
    HANDICAPPED = "handicapped"
    MOTORCYCLE = "motorcycle"
    EV = "ev"


class Spot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    floor: int
    spot_type: SpotType = Field(sa_column=Column(SAEnum(SpotType), nullable=False))
    is_free: bool = Field(default=True)
    ticket: Optional["Ticket"] = Relationship(back_populates="spot")


class Vehicle(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    license_plate: str = Field(sa_column=Column(String, unique=True, index=True))
    vehicle_type: VehicleType = Field(sa_column=Column(SAEnum(VehicleType), nullable=False))
    tickets: List["Ticket"] = Relationship(back_populates="vehicle")


class Ticket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    vehicle_id: Optional[int] = Field(default=None, foreign_key="vehicle.id")
    spot_id: Optional[int] = Field(default=None, foreign_key="spot.id")
    entry_time: datetime = Field(default_factory=datetime.utcnow)
    exit_time: Optional[datetime] = None
    paid_amount: Optional[float] = None
    is_paid: bool = Field(default=False)
    vehicle: Optional[Vehicle] = Relationship(back_populates="tickets")
    spot: Optional[Spot] = Relationship(back_populates="ticket")

from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from app.models.models import Spot, Vehicle, Ticket, SpotType


class SpotRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_free_spot(self, spot_types: List[SpotType]) -> Optional[Spot]:
        stmt = select(Spot).where(Spot.is_free == True, Spot.spot_type.in_(spot_types)).order_by(Spot.id)
        if self.session.get_bind().dialect.name == "postgresql":
            stmt = stmt.with_for_update(skip_locked=True)
        result = self.session.exec(stmt).first()
        return result

    def save(self, obj):
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get_by_id(self, spot_id: int) -> Optional[Spot]:
        stmt = select(Spot).where(Spot.id == spot_id)
        return self.session.exec(stmt).one_or_none()

    def free_spot(self, spot_id: int) -> Optional[Spot]:
        spot = self.get_by_id(spot_id)
        if not spot:
            return None
        spot.is_free = True
        self.session.add(spot)
        self.session.commit()
        self.session.refresh(spot)
        return spot


class VehicleRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_or_create(self, license_plate: str, vehicle_type) -> Vehicle:
        stmt = select(Vehicle).where(Vehicle.license_plate == license_plate)
        found = self.session.exec(stmt).first()
        if found:
            return found
        v = Vehicle(license_plate=license_plate, vehicle_type=vehicle_type)
        self.session.add(v)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            return self.session.exec(stmt).one()
        self.session.refresh(v)
        return v


class TicketRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, ticket: Ticket) -> Ticket:
        self.session.add(ticket)
        self.session.commit()
        self.session.refresh(ticket)
        return ticket

    def get(self, ticket_id: int) -> Optional[Ticket]:
        stmt = select(Ticket).where(Ticket.id == ticket_id)
        return self.session.exec(stmt).one_or_none()

    def update(self, ticket: Ticket) -> Ticket:
        self.session.add(ticket)
        self.session.commit()
        self.session.refresh(ticket)
        return ticket


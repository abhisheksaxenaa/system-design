from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update
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

    def claim_free_spot(self, spot_types: List[SpotType]) -> Optional[Spot]:
        """Atomically claim a free spot and return it.

        For Postgres use an UPDATE ... RETURNING to atomically flip is_free -> False.
        For other DBs fall back to a safe check-and-set update.
        """
        # Try Postgres-style atomic update with RETURNING
        try:
            if self.session.get_bind().dialect.name == "postgresql":
                subq = select(Spot.id).where(
                    Spot.is_free == True, Spot.spot_type.in_(spot_types)
                ).order_by(Spot.id).limit(1).scalar_subquery()
                upd = update(Spot).where(Spot.id == subq, Spot.is_free == True).values(is_free=False).returning(Spot.id)
                res = self.session.exec(upd).one_or_none()
                if not res:
                    return None
                spot_id = res[0]
                return self.get_by_id(spot_id)
        except Exception:
            # fallthrough to generic path
            pass

        # Generic fallback: select a candidate and attempt to update by id
        stmt = select(Spot).where(Spot.is_free == True, Spot.spot_type.in_(spot_types)).order_by(Spot.id).limit(1)
        candidate = self.session.exec(stmt).first()
        if not candidate:
            return None

        try:
            upd2 = update(Spot).where(Spot.id == candidate.id, Spot.is_free == True).values(is_free=False)
            res2 = self.session.exec(upd2)
            # SQLAlchemy Result has rowcount for DML
            if getattr(res2, "rowcount", 0) == 0:
                return None
            # refresh and return the claimed spot
            return self.get_by_id(candidate.id)
        except Exception:
            return None

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
        if not spot or spot.is_free:
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


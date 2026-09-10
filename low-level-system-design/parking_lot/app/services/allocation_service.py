from typing import List
from app.repos.repo import SpotRepository, VehicleRepository, TicketRepository
from app.models.models import VehicleType, SpotType, Ticket


class AllocationService:
    def __init__(self, session):
        self.session = session
        self.spot_repo = SpotRepository(session)
        self.vehicle_repo = VehicleRepository(session)
        self.ticket_repo = TicketRepository(session)

    def _eligible_spot_types(self, vehicle_type: VehicleType) -> List[SpotType]:
        if vehicle_type == VehicleType.CAR:
            return [SpotType.COMPACT, SpotType.LARGE, SpotType.EV]
        if vehicle_type == VehicleType.TRUCK:
            return [SpotType.LARGE]
        if vehicle_type == VehicleType.MOTORCYCLE:
            return [SpotType.MOTORCYCLE, SpotType.COMPACT]
        # TODO: Raise exception if vehicle type is not supported?
        return [SpotType.COMPACT]

    def allocate_spot(self, license_plate: str, vehicle_type: VehicleType):
        eligible = self._eligible_spot_types(vehicle_type)
        # create or fetch vehicle first (handles unique constraint)
        vehicle = self.vehicle_repo.get_or_create(license_plate, vehicle_type)

        # atomically claim a free spot
        spot = self.spot_repo.claim_free_spot(eligible)
        if not spot:
            return None

        # create ticket; if ticket creation fails, free the spot again
        ticket = Ticket(vehicle_id=vehicle.id, spot_id=spot.id)
        try:
            created = self.ticket_repo.create(ticket)
            return created
        except Exception:
            # attempt to free the spot if ticket creation fails
            try:
                self.spot_repo.free_spot(spot.id)
            except Exception:
                pass
            raise

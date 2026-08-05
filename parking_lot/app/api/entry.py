from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session
from app.db import get_session
from app.services.allocation_service import AllocationService
from app.models.models import VehicleType

router = APIRouter()


class EntryRequest(BaseModel):
    license_plate: str
    vehicle_type: VehicleType


@router.post("/entry/ticket")
def take_ticket(request: EntryRequest, session: Session = Depends(get_session)):
    service = AllocationService(session)
    ticket = service.allocate_spot(request.license_plate, request.vehicle_type)
    if ticket is None:
        # TODO: Can raise custom exception related to NoTicketAvailableException?
        raise HTTPException(status_code=409, detail="Parking Full or no suitable spot")
    return {"ticket_id": ticket.id, "spot_id": ticket.spot_id, "entry_time": ticket.entry_time}

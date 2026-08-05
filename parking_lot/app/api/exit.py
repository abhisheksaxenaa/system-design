from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from datetime import datetime
from pydantic import BaseModel

from app.db import get_session
from app.repos.repo import TicketRepository, SpotRepository
from app.services.pricing_service import PricingService
from app.services.payment_service import PaymentService

router = APIRouter()

class PaymentRequest(BaseModel):
    method: str
    details: dict = {}


@router.get("/ticket/{ticket_id}")
def scan_ticket(ticket_id: int, session: Session = Depends(get_session)):
    ticket_repo = TicketRepository(session)
    ticket = ticket_repo.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    now = datetime.utcnow()
    pricing = PricingService()
    fee = pricing.compute_fee(ticket.entry_time, now)
    return {"ticket_id": ticket.id, "entry_time": ticket.entry_time, "now": now, "estimated_fee": fee}


@router.post("/ticket/{ticket_id}/pay")
def pay_ticket(ticket_id: int, req: PaymentRequest, session: Session = Depends(get_session)):
    ticket_repo = TicketRepository(session)
    ticket = ticket_repo.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    now = datetime.utcnow()
    pricing = PricingService()
    amount = pricing.compute_fee(ticket.entry_time, now)
    payment = PaymentService()
    ok = payment.pay(req.method, amount, req.details)
    if not ok:
        raise HTTPException(status_code=402, detail="Payment failed")
    ticket.is_paid = True
    ticket.paid_amount = amount
    ticket.exit_time = now
    ticket_repo.update(ticket)
    return {"ticket_id": ticket.id, "paid": True, "amount": amount}


@router.post("/exit/{ticket_id}")
def exit_parking(ticket_id: int, session: Session = Depends(get_session)):
    ticket_repo = TicketRepository(session)
    spot_repo = SpotRepository(session)
    ticket = ticket_repo.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if not ticket.is_paid:
        raise HTTPException(status_code=403, detail="Ticket not paid")
    # free the spot
    spot = spot_repo.free_spot(ticket.spot_id)
    ticket_repo.update(ticket)
    return {"ticket_id": ticket.id, "exited": True, "spot_freed": spot.id if spot else None}

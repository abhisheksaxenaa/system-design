from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session
from app.db import get_session
from app.models.models import SpotType, Spot
from app.auth import get_current_user, require_role

router = APIRouter()


class SpotCreate(BaseModel):
    floor: int
    spot_type: SpotType


@router.post("/spots")
def create_spot(payload: SpotCreate, session: Session = Depends(get_session), user=Depends(require_role("admin"))):
    spot = Spot(floor=payload.floor, spot_type=payload.spot_type)
    session.add(spot)
    session.commit()
    session.refresh(spot)
    return {"spot_id": spot.id, "floor": spot.floor, "spot_type": spot.spot_type}

@router.get("/spots/occupied")
def get_occupied_spots(session: Session = Depends(get_session), user=Depends(require_role("admin"))):
    spots = session.query(Spot).filter(Spot.is_free == False).all()
    return [{"spot_id": spot.id, "floor": spot.floor, "spot_type": spot.spot_type} for spot in spots]

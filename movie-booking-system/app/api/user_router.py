from pydantic import BaseModel
from sqlmodel import Session
from fastapi import APIRouter, Depends, HTTPException

from app.boundary.db import get_session
from app.models.user import User

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    email: str

@router.post("/user")
def create_user(payload: UserCreate, session: Session = Depends(get_session)):
    try:
        user = User(name=payload.name, email=payload.email)
        session.add(user)
        session.commit()
        session.refresh(user)
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@router.get("/user/{user_id}")
def get_user(user_id: int, session: Session = Depends(get_session)):
    try:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session
from app.boundary.db import get_session
from app.models.models import Symbol
from app.repos.winning_strategy import Standard3x3WinningStrategy
from app.services.game_service import GameService

router = APIRouter()


class GameCreate(BaseModel):
    player_1: str
    player_2: str

class MoveCreate(BaseModel):
    player: str
    row: int
    col: int

@router.post("/game")
def create_game(payload: GameCreate, session: Session = Depends(get_session)):
    service = GameService(session=session, winning_strategy=Standard3x3WinningStrategy())
    service.create_player(payload.player_1, Symbol.X)
    service.create_player(payload.player_2, Symbol.O)
    game = service.start_game()
    return {"game_id": game.id, "start_player": payload.player_1, "status": game.status.value}

@router.post("/game/{game_id}/move")
def make_move(game_id: str, payload: MoveCreate, session: Session = Depends(get_session)):
    service = GameService(session=session, winning_strategy=Standard3x3WinningStrategy())
    game = service.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    move = service.play_turn(game_id, payload.player, payload.row, payload.col)
    return {"move_id": move.id, "game_id": game.id, "status": game.status.value, "winner": move.winner.name if move.winner else None}

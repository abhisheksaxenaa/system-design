from fastapi import APIRouter
from app.api.game_router import router as game_router

router = APIRouter()
router.include_router(game_router)

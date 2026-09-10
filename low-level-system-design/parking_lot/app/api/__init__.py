from fastapi import APIRouter
from .entry import router as entry_router
from .admin import router as admin_router
from .exit import router as exit_router

router = APIRouter()
router.include_router(entry_router)
router.include_router(admin_router, prefix="/admin")
router.include_router(exit_router)

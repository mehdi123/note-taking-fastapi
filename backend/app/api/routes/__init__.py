from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.note import router as note_router
from app.api.routes.admin import router as admin_router


router = APIRouter()


router.include_router(auth_router, tags=["authentication"])
router.include_router(note_router, tags=["note"])
router.include_router(admin_router, tags=["admin"])

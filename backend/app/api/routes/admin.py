from typing import List
from fastapi import APIRouter, HTTPException, Depends
from fastapi_pagination import Page

from app.core.users import get_current_user
from app.schemas.user import UserInDB
from app.schemas.note import Note
from app.db.note import NotesTableHandler
from app.core.config import API_ADMIN_PREFIX

router = APIRouter(prefix=API_ADMIN_PREFIX)

@router.get("/search", response_model=Page[Note])
async def search_notes(tags: List[str], user: UserInDB = Depends(get_current_user)):
    """
        Search notes based on keyword
    """

    if not user.is_superuser:
        raise HTTPException(status_code=401, detail="User not authorized to do this operation")

    return await NotesTableHandler.search_tags(tags)
from fastapi import APIRouter, Query, Path, HTTPException, Depends
from fastapi_pagination import Page

from app.core.users import get_current_user
from app.schemas.note import Note, NoteCreate, NoteUpdate, BaseResponse
from app.schemas.user import UserInDB
from app.db.note import NotesTableHandler
from app.core.config import API_NOTE_PREFIX

router = APIRouter(prefix=API_NOTE_PREFIX)

@router.post("/", response_model=BaseResponse)
async def create_note(note: NoteCreate, user: UserInDB = Depends(get_current_user)):
    """
        Creates a note record for the current user
    """

    await NotesTableHandler.add(note, user.id)
    return {"success": True, "message": "note has been created successfully"}

@router.put("/", response_model=BaseResponse)
async def update_note(note: NoteUpdate, user: UserInDB = Depends(get_current_user)):
    """
        Updates a note
    """
    await NotesTableHandler.update(note, user.id)
    return {"success": True, "message": "note has been created successfully"}

@router.get("/", response_model=Page[Note])
async def get_note(user: UserInDB = Depends(get_current_user)):
    """
        Get the current users notes paginated
    """
    return await NotesTableHandler.get(user.id)

@router.delete("/", response_model=BaseResponse)
async def delete_note(note_id: int, user: UserInDB = Depends(get_current_user)):
    """
        Removes the note
    """
    await NotesTableHandler.delete(note_id, user.id)

@router.get("/search", response_model=Page[Note])
async def search_notes(keyword: str, user: UserInDB = Depends(get_current_user)):
    """
        Search notes based on keyword
    """
    return await NotesTableHandler.search(keyword, user.id)

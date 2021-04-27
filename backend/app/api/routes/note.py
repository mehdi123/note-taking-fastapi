from typing import Any, Union
from fastapi import APIRouter, Query, Path, HTTPException, Depends
from fastapi_pagination import Page

from app.core.users import get_current_user
from app.schemas.note import Note, NoteCreate, NoteUpdate, NoteInDB, BaseResponse
from app.schemas.user import UserInDB
from app.db.note import NotesTableHandler
from app.core.config import API_NOTE_PREFIX

router = APIRouter(prefix=API_NOTE_PREFIX)

@router.post("/", response_model=Union[NoteInDB, BaseResponse])
async def create_note(note: NoteCreate, user: UserInDB = Depends(get_current_user)):
    """
        Creates a note record for the current user and returns the new record
    """

    note_id = await NotesTableHandler.add(note, user.id)
    if note_id:
        return {**note.dict(), "id": note_id, "user_id": user.id}
    else:
        return {"success": False, "message": "Note not created"}

@router.put("/", response_model=Union[NoteInDB, BaseResponse])
async def update_note(note: NoteUpdate, user: UserInDB = Depends(get_current_user)):
    """
        Updates a note
    """
    result = await NotesTableHandler.update(note, user.id)
    if result:
        note_in_db = NoteInDB(title=result.get('title'),
                            body=result.get('body'),
                            tags=result.get('tags'),
                            id=result.get('id'),
                            user_id=result.get('user_id'))
        return note_in_db
    else:
        return {"success": False, "message": "No such note with the provided id"}

@router.get("/", response_model=Page[Any])
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
    result = await NotesTableHandler.delete(note_id, user.id)
    if result:
        return {"success": True, "message": "The note has been removed successfully"}
    else:
        return {"success": False, "message": "No such note with the provided id"}

@router.get("/search", response_model=Page[Any])
async def search_notes(keyword: str, user: UserInDB = Depends(get_current_user)):
    """
        Search notes based on keyword
    """
    return await NotesTableHandler.search(keyword, user.id)
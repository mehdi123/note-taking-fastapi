from pydantic import Field, EmailStr
from typing import List, Optional

from .core import IDModelMixin, CoreModel, BaseResponse

class Note(CoreModel):
    title: Optional[str]
    body: Optional[str]
    tags: Optional[List[str]]

class NoteCreate(CoreModel):
    title: str = Field(...)
    body: str = Field(...)
    tags: List[str] = Field(...)

class NoteUpdate(CoreModel, IDModelMixin):
    data: Note
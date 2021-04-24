from typing import List
from fastapi_pagination.ext.databases import paginate
from sqlalchemy import or_
from sqlalchemy.sql.expression import select

from . import database
from app.models.note import notes
from app.schemas.note import NoteCreate, NoteUpdate

class NotesTableHandler:
    '''
        Notes sqlalchemy table handler
    '''
    @staticmethod
    async def add(note: NoteCreate, user_id: int):
        query = notes.insert().values(title=note.title,
                                        body=note.body,
                                        tags=', '.join(note.tags),
                                        user_id=user_id)
        note_id = await database.execute(query)
        if note_id:
            query = notes.select().where(notes.c.user_id == user_id)\
                                .where(notes.c.id == note_id)
            result = await database.fetch_one(query)
            return result
    
    @staticmethod
    async def update(note: NoteUpdate, user_id: int):
        query = notes.select().where(notes.c.id == note.id)\
                            .where(notes.c.user_id == user_id)
        existing = await database.fetch_one(query)
        if existing:
            note_data = {k:v for k, v in note.data.dict().items() if v is not None}
            if note_data.get('tags'): # converting list of tags to string
                note_data['tags'] = ','.join(note_data['tags'])
            query = notes.update().values(**note_data).where(notes.c.id == note.id)\
                                    .where(notes.c.user_id == user_id)
            await database.execute(query)
            query = notes.select().where(notes.c.id == note.id).where(notes.c.user_id == user_id)
            result = await database.fetch_one(query)
            return result
        else:
            return None
    
    @staticmethod
    async def get(user_id: int):
        return await paginate(database, select([
            notes.c.title,
            notes.c.body,
            notes.c.tags            
        ]).where(notes.c.user_id==user_id))
    
    @staticmethod
    async def delete(note_id: int, user_id: int):
        query = notes.select().where(notes.c.id == note_id)\
                            .where(notes.c.user_id == user_id)
        note = await database.fetch_one(query)
        if note:
            query = notes.delete().where(notes.c.id == note_id).where(notes.c.user_id == user_id)
            await database.execute(query)
            return True
        else:
            return False

    @staticmethod
    async def search(keyword: str, user_id: int):
        query = notes.select().where(notes.c.user_id == user_id).where(
                                or_(
                                    notes.c.title.ilike(f"%{keyword}%"),
                                    notes.c.body.ilike(f"%{keyword}%"),
                                    notes.c.tags.ilike(f"%{keyword}%")
                                )
                            )
        return await paginate(database, query)
    
    @staticmethod
    async def search_tags(tags: List[str]):
        """
            Super user method
        """
        query = notes.select()
        for tag in tags:
            query = query.where(notes.c.tags.like(f"%,{tag} %"))
        return await paginate(database, query)

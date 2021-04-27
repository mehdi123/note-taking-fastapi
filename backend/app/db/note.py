from typing import List
from fastapi_pagination import paginate
import itertools

from sqlalchemy import or_, func
from sqlalchemy.sql.expression import select
import logging
import asyncio
from functools import wraps


from . import database as db
from app.models.note import notes, tags, note_tag
from app.schemas.note import NoteCreate, NoteUpdate, NoteInDB, NotesStats

def exc_handler(errors=(Exception, ), ret_val=None, logger=logging.getLogger(__name__)):
    """
        Exception handler decorator
    """
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def new_func(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except errors as err:
                    raise err
                    logger.warn(str(err))
                    return ret_val
            return new_func
        else:
            @wraps(func)
            def new_func(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except errors as err:
                    logger.warn(str(err))
                    return ret_val
            return new_func

    return decorator

class NotesTableHandler:
    '''
        Notes sqlalchemy table handler
    '''
    @staticmethod
    @exc_handler()
    async def add(note: NoteCreate, user_id: int):
        note_id = await db.execute(
            notes.insert().values(title=note.title, body=note.body, user_id=user_id)
        )
        if note_id:
            for tag in note.tags:
                tag_record = await TagsTableHandler.add_or_get_tag(tag)
                if tag_record:
                    await db.execute(
                        note_tag.insert().values(note_id=note_id, tag_id=tag_record.get('id'))
                    )
                else: # there is an exception
                    return None
            return note_id
    
    @staticmethod
    @exc_handler()
    async def update(note: NoteUpdate, user_id: int):
        existing = await db.fetch_one(
                    notes.select().where(notes.c.id == note.id).where(notes.c.user_id == user_id)
                    )
        if existing:
            note_data = {k:v for k, v in note.data.dict().items() if v is not None and k != 'tags'}
            await db.execute(
                notes.update().values(**note_data).where(notes.c.id == note.id).where(notes.c.user_id == user_id)
            )
            if note.data.tags is not None and len(note.data.tags) > 0:
                await NoteTagTableHandler.clean_up_tags(note.id)
                for tag in note.data.tags:
                    tag_record = await TagsTableHandler.add_or_get_tag(tag)
                    await NoteTagTableHandler.add_tag_for_note(note.id, tag_record.get('id'))
            note_in_db = await db.fetch_one(
                notes.select().where(notes.c.id == note.id).where(notes.c.user_id == user_id)
            )
            tags = await NoteTagTableHandler.get_note_tags(note.id)
            return {**note_in_db, "tags": tags}
        else:
            return None
    
    @staticmethod
    async def get(user_id: int) -> List[NoteInDB]:
        #TODO the pagination should be tested. We need to investigate the nested queries
        note_items = []
        notes_in_db = await db.fetch_all(
            notes.select().where(notes.c.user_id==user_id)
        )
        for note_in_db in notes_in_db:
            note_items.append({**note_in_db, 
                    "tags": await NoteTagTableHandler.get_note_tags(note_in_db.get('id'))
                })
        return paginate(note_items)
   
    @staticmethod
    @exc_handler(ret_val=False)
    async def delete(note_id: int, user_id: int):
        #TODO how to retrieve the rows affected?
        await db.execute(
            notes.delete().where(notes.c.id == note_id).where(notes.c.user_id == user_id)
        )
        return True

    @staticmethod
    @exc_handler()
    async def search(keyword: str, user_id: int):
        note_items = []
        notes_in_db = await db.fetch_all(
                        notes.select().where(notes.c.user_id == user_id).where(
                            or_(
                                notes.c.title.ilike(f"%{keyword}%"),
                                notes.c.body.ilike(f"%{keyword}%")
                            )
                        )
                    )
        if notes_in_db:
            for note_in_db in notes_in_db:
                note_items.append({**note_in_db, 
                        "tags": await NoteTagTableHandler.get_note_tags(note_in_db.get('id'))
                    })
        like_tags = await TagsTableHandler.search(keyword)
        if len(like_tags) > 0:
            for tag in like_tags:
                user_notes = await NoteTagTableHandler.get_user_notes_by_tag(user_id, tag)
                for user_note in user_notes:
                    note_items.append({**user_note, 
                                    "tags": await NoteTagTableHandler.get_note_tags(user_note.get('id')) 
                                    })
        return paginate(note_items)
    
    @staticmethod
    @exc_handler()
    async def search_tags(tags: List[str]):
        """
            Super user method
        """
        note_records = list(itertools.chain(*[await NoteTagTableHandler.get_notes_by_tag(tag) for tag in tags]))
        return paginate(
            [
                {**note_record, "tags": await NoteTagTableHandler.get_note_tags(note_record.get('id'))} for note_record in note_records
            ]
        )

    @staticmethod
    @exc_handler()
    async def get_note_by_id(note_id: int) -> NoteInDB:
        return await db.fetch_one(
                        notes.select().where(notes.c.id == note_id)
                    )

    @staticmethod
    @exc_handler()
    async def get_stats() -> NotesStats:
        notes_count = await db.fetch_one(
            select([func.count()], notes)
        )
        tags_count = await TagsTableHandler.get_tags_count()
        return NotesStats(notes=notes_count.get('count_1'), tags=tags_count.get('count_1'))

class TagsTableHandler:
    """
        Tags sqlalchemy table handler
    """

    @staticmethod
    @exc_handler(ret_val={})
    async def add_or_get_tag(tag) -> dict:
        existing_tag = await db.fetch_one(
                            tags.select().where(tags.c.name == tag)
                        )
        if existing_tag:
            return existing_tag
        tag_id = await db.execute(
                    tags.insert().values(name=tag)
                )
        if tag_id:
            return {"name": tag, "id": tag_id}
        return {}
    
    @staticmethod
    @exc_handler(ret_val={})
    async def get_tag_by_id(tag_id: int) -> dict:
        return await db.fetch_one(
            tags.select().where(tags.c.id == tag_id)
        )
    
    @staticmethod
    @exc_handler()
    async def get_tag_by_name(tag: str) -> dict:
        return await db.fetch_one(
            tags.select().where(tags.c.name == tag)
        )
    
    @staticmethod
    @exc_handler()
    async def search(like_tag: str) -> List[dict]:
        return [{'id': tag.get('id'), 'name': tag.get('name')} for tag in await db.fetch_all(
                    tags.select().where(tags.c.name.ilike(f"%{like_tag}%"))
                )]

    @staticmethod
    @exc_handler()
    async def get_tags_count() -> int:
        return await db.fetch_one(
            select([func.count()], tags)
        )

class NoteTagTableHandler:
    """
        note_tag sqlalchemy table handler
    """

    @staticmethod
    @exc_handler()
    async def clean_up_tags(note_id: int) -> None:
        await db.execute(
            note_tag.delete().where(note_tag.c.note_id == note_id)
        )
    
    @staticmethod
    @exc_handler()
    async def add_tag_for_note(note_id: int, tag_id: int) -> None:
        await db.execute(
            note_tag.insert().values(note_id=note_id, tag_id=tag_id)
        )
    
    @staticmethod
    @exc_handler()
    async def get_note_tags(note_id: int) -> List[str]:
        note_tag_ids = await db.fetch_all(
            note_tag.select().where(note_tag.c.note_id==note_id)
        )
        tags = []
        if note_tag_ids:
            for note_tag_id in note_tag_ids:
                tag = await TagsTableHandler.get_tag_by_id(note_tag_id.get('tag_id'))
                if tag:
                    tags.append(tag.get('name'))
        return tags
    
    @staticmethod
    @exc_handler()
    async def get_notes_by_tag(tag: str) -> List[NoteInDB]:
        tag_record = await TagsTableHandler.get_tag_by_name(tag)
        if tag_record:
            note_ids = await db.fetch_all(
                note_tag.select().where(note_tag.c.tag_id == tag_record.get('id'))
            )
            return [
                await NotesTableHandler.get_note_by_id(note_id.get('note_id')) for note_id in note_ids
            ]
        return []

    @staticmethod
    @exc_handler()
    async def get_user_notes_by_tag(user_id: int, tag: dict) -> List[NoteInDB]:
        note_rows = await db.fetch_all(
            notes.select().where(notes.c.user_id == user_id)
        )
        note_ids = [note_row.get('id') for note_row in note_rows]
        tagged_note_ids = await db.fetch_all(
            note_tag.select().where(note_tag.c.tag_id == tag.get('id')).where(note_tag.c.note_id.in_(note_ids))
        )
        return [
            await NotesTableHandler.get_note_by_id(note_id.get('note_id')) for note_id in tagged_note_ids
        ]

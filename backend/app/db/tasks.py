from fastapi import FastAPI
import logging
import sqlalchemy

from . import database, metadata
from app.core.config import DATABASE_URL
from app.utils.hash import create_hash
from app.models.user import users

logger = logging.getLogger(__name__)

async def add_admin_user(database) -> None:
    try:
        query = users.select().where(users.c.is_superuser == True)\
                            .where(users.c.fullname=='admin')
        existing_user = await database.fetch_one(query)
        if not existing_user:
            query = users.insert().values(fullname="admin",
                                email="admin",
                                password=create_hash("admin"),
                                is_verified=True,
                                is_superuser=True)
            await database.execute(query)
    except Exception as e:
        logger.warn(e)

async def connect_to_db(app: FastAPI) -> None:

    try:
        await database.connect()
        app.state._db = database

        engine = sqlalchemy.create_engine(str(DATABASE_URL))
        metadata.create_all(engine)
        
        await add_admin_user(database)

    except Exception as e:
        logger.warn("--- DB CONNECTION ERROR ---")
        logger.warn(e)
        logger.warn("--- DB CONNECTION ERROR ---")


async def close_db_connection(app: FastAPI) -> None:
    try:
        await app.state._db.disconnect()
    except Exception as e:
        logger.warn("--- DB DISCONNECT ERROR ---")
        logger.warn(e)
        logger.warn("--- DB DISCONNECT ERROR ---")
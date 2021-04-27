from fastapi import FastAPI
import logging
import sqlalchemy
from databases import Database

from . import database, metadata
from app.core.config import DATABASE_URL, DEFAULT_ADMIN_NAME, DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD

from app.models.user import users
from app.utils.hash import create_hash

logger = logging.getLogger(__name__)

async def connect_to_db(app: FastAPI) -> None:

    try:
        await database.connect()
        app.state._db = database

        engine = sqlalchemy.create_engine(str(DATABASE_URL))
        metadata.create_all(engine)

        await create_admin_user(database)
        
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

async def create_admin_user(db: Database) -> None:
    """
        Creating default admin if not already in db.
    """
    #TODO this function is temporatily here.
    try:
        admin_user = await db.fetch_one(
            users.select().where(users.c.fullname == DEFAULT_ADMIN_NAME).where(users.c.is_superuser == True)
        )
        print(admin_user)
        if not admin_user:
            await db.execute(
                users.insert().values(fullname=DEFAULT_ADMIN_NAME,
                                        email=DEFAULT_ADMIN_EMAIL,
                                        password=create_hash(DEFAULT_ADMIN_PASSWORD),
                                        is_superuser=True,
                                        is_verified=True)

            )
    except Exception as e:
        logger.warn(e)
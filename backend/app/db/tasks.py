from fastapi import FastAPI
import logging
import sqlalchemy

from . import database, metadata
from app.core.config import DATABASE_URL

logger = logging.getLogger(__name__)

async def connect_to_db(app: FastAPI) -> None:

    try:
        await database.connect()
        app.state._db = database

        engine = sqlalchemy.create_engine(str(DATABASE_URL))
        metadata.create_all(engine)

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
import sqlalchemy
from databases import Database
from app.core.config import DATABASE_URL

database = Database(DATABASE_URL, min_size=2, max_size=10)  # specifying min and max connections

metadata = sqlalchemy.MetaData()
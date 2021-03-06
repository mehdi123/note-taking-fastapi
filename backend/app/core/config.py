from databases import DatabaseURL
from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

PROJECT_NAME = "note-taking"
VERSION = "1.0.0"
API_PREFIX = "/api/v1"
API_AUTH_PREFIX="/auth"
API_NOTE_PREFIX="/note"
API_ADMIN_PREFIX="/admin"

SECRET_KEY = config("SECRET_KEY", cast=Secret, default="CHANGEIT")

POSTGRES_USER = config("POSTGRES_USER", cast=str)
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", cast=Secret)
POSTGRES_SERVER = config("POSTGRES_SERVER", cast=str, default="db")
POSTGRES_PORT = config("POSTGRES_PORT", cast=str, default="5432")
POSTGRES_DB = config("POSTGRES_DB", cast=str)

DATABASE_URL = config(
  "DATABASE_URL",
  cast=DatabaseURL,
  default=f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

MAIL_USERNAME = config("MAIL_USERNAME")
MAIL_PASSWORD = config("MAIL_PASSWORD")
MAIL_FROM = config("MAIL_FROM")
MAIL_SERVER = config("MAIL_SERVER")

JWT_SECRET = str(config("JWT_SECRET_KEY"))
JWT_ALGORITHM = str(config("JWT_ALGORITHM"))
ACCESS_TOKEN_EXPIRE_SECONDS = 30*60

DEFAULT_ADMIN_NAME='admin'
DEFAULT_ADMIN_EMAIL='admin@example.com'
DEFAULT_ADMIN_PASSWORD='admin'
import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.db import metadata


users = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, auto_increment=True),
    sa.Column("fullname", sa.String),
    sa.Column("email", sa.String),
    sa.Column("password", sa.String),
    sa.Column("is_superuser", sa.Boolean, default=False),
    sa.Column("is_verified", sa.Boolean, default=False)
)

verifications = sa.Table(
    "verifications",
    metadata,
    sa.Column("user_id", sa.ForeignKey("users.id", ondelete='CASCADE')),
    sa.Column("code", sa.String) # hash of fullname:email
)
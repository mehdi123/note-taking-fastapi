import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.db import metadata


notes = sa.Table(
    "notes",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, auto_increment=True),
    sa.Column("title", sa.String),
    sa.Column("body", sa.String),
    sa.Column("tags", sa.String), # comma separated tags: "tag1, tag2, ..."
    sa.Column("user_id", sa.ForeignKey("users.id", ondelete='CASCADE')),
)

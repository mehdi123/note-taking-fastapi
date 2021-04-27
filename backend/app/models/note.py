import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.db import metadata


notes = sa.Table(
    "notes",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, auto_increment=True),
    sa.Column("title", sa.String),
    sa.Column("body", sa.String),
    sa.Column("user_id", sa.ForeignKey("users.id", ondelete='CASCADE')),
)

tags = sa.Table(
    "tags",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, auto_increment=True),
    sa.Column("name", sa.String)
)

note_tag = sa.Table(
    "note_tag",
    metadata,
    sa.Column("note_id", sa.ForeignKey("notes.id", ondelete="CASCADE")),
    sa.Column("tag_id", sa.ForeignKey("tags.id", ondelete="CASCADE"))
)
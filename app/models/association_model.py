from sqlalchemy import Column, ForeignKey, Integer, Table

from app.models.base_model import Base

question_tags = Table( 
    "question_tag",
    Base.metadata,
    Column("question_id", Integer, ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),)
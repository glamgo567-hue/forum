from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.association_model import question_tags
from app.models.base_model import Base


class Question(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    title:  Mapped[str] = mapped_column(String(100))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author = relationship("User", back_populates="questions")
    tags = relationship("Tag", secondary=question_tags, back_populates="questions")
    answers = relationship("Answer", passive_deletes=True, back_populates="question")
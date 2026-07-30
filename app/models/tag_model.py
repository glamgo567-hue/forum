from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.association_model import question_tags
from app.models.base_model import Base


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    questions = relationship("Question", secondary=question_tags, back_populates="tags")
from sqlalchemy import CheckConstraint, ForeignKey, Index, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import Base


class Vote(Base):
    __tablename__ = "votes"
    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[int]

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    question_id: Mapped[int | None] = mapped_column(ForeignKey("questions.id"))
    answer_id: Mapped[int | None] = mapped_column(ForeignKey("answers.id"))

    __table_args__ = (Index("ix_vote_user_question_unique",
                            "user_id", "question_id",
                            unique=True,
                            postgresql_where=text("question_id IS NOT NULL")),
                      Index("ix_vote_user_answer_unique",
                            "user_id", "answer_id",
                            unique=True,
                            postgresql_where=text("answer_id IS NOT NULL")),
                      CheckConstraint(
                        "(question_id IS NOT NULL AND answer_id IS NULL) OR"
                        "(question_id IS NULL AND answer_id IS NOT NULL)",
                        name="ck_vote_exactly_one_target"))
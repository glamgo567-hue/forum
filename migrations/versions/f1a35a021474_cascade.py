"""cascade

Revision ID: f1a35a021474
Revises: 2a51bf8fc57f
Create Date: 2026-08-01 17:53:08.223408

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f1a35a021474'
down_revision: str | Sequence[str] | None = '2a51bf8fc57f'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(op.f('answers_question_id_fkey'), 'answers', type_='foreignkey')
    op.create_foreign_key('fk_answers_question_id', 'answers', 'questions', ['question_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint(op.f('question_tag_question_id_fkey'), 'question_tag', type_='foreignkey')
    op.create_foreign_key('fk_question_tag_question_id', 'question_tag', 'questions', ['question_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint(op.f('votes_answer_id_fkey'), 'votes', type_='foreignkey')
    op.create_foreign_key('fk_votes_answer_id', 'votes', 'answers', ['answer_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint(op.f('votes_question_id_fkey'), 'votes', type_='foreignkey')
    op.create_foreign_key('fk_votes_question_id', 'votes', 'questions', ['question_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_votes_question_id', 'votes', type_='foreignkey')
    op.create_foreign_key(op.f('votes_question_id_fkey'), 'votes', 'questions', ['question_id'], ['id'])

    op.drop_constraint('fk_votes_answer_id', 'votes', type_='foreignkey')
    op.create_foreign_key(op.f('votes_answer_id_fkey'), 'votes', 'answers', ['answer_id'], ['id'])

    op.drop_constraint('fk_question_tag_question_id', 'question_tag', type_='foreignkey')
    op.create_foreign_key(op.f('question_tag_question_id_fkey'), 'question_tag', 'questions', ['question_id'], ['id'])

    op.drop_constraint('fk_answers_question_id', 'answers', type_='foreignkey')
    op.create_foreign_key(op.f('answers_question_id_fkey'), 'answers', 'questions', ['question_id'], ['id'])
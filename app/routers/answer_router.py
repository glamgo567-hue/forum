from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user, get_current_user_optional
from app.dependencies.db import get_db
from app.models.answer_model import Answer
from app.models.question_model import Question
from app.models.user_model import User
from app.models.vote_model import Vote
from app.schemas.answer_schemas import AnswerCreate, AnswerRead, AnswerUpdate
from app.services.reputation_helpers import apply_reputation_change
from app.services.vote_helpers import get_my_vote, get_score

answer_router = APIRouter(tags=["answers"])

@answer_router.post("/questions/{question_id}/answers", response_model=AnswerRead, status_code=status.HTTP_201_CREATED)
async def create_answer(answer_data: AnswerCreate,
                        question_id: int,
                        current_user: User = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    question = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    new_answer = Answer(body=answer_data.body,
                        question_id=question_id,
                        author_id=current_user.id)
    db.add(new_answer)
    await db.commit()
    await db.refresh(new_answer)
    return AnswerRead(id=new_answer.id,
                      body=new_answer.body,
                      is_accepted=new_answer.is_accepted,
                      created_at=new_answer.created_at,
                      author_id=new_answer.author_id,
                      question_id=new_answer.question_id,
                      score=0,
                      my_vote=None)

@answer_router.get("/questions/{question_id}/answers", response_model=list[AnswerRead])
async def show_answers(question_id: int,
                       skip: int = 0,
                       limit: int = 10,
                       current_user: User | None = Depends(get_current_user_optional),
                       db: AsyncSession = Depends(get_db)):
    question = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    answers = (await db.execute(select(Answer).where(Answer.question_id == question_id).offset(skip).limit(limit))).scalars().all()
    answer_ids = [a.id for a in answers]

    scores_dict = {answer_id: score for answer_id, score in (await db.execute(select(Vote.answer_id, func.coalesce(func.sum(Vote.value), 0)).where(Vote.answer_id.in_(answer_ids)).group_by(Vote.answer_id))).all()}

    if current_user is None:
        my_votes_dict = {}
    else:
        my_votes_dict = {answer_id: value for answer_id, value in (await db.execute(select(Vote.answer_id, Vote.value).where(Vote.answer_id.in_(answer_ids), Vote.user_id == current_user.id))).all()}

    result = []
    for answer in answers:
        result.append(AnswerRead(id=answer.id,
                                 body=answer.body,
                                 is_accepted=answer.is_accepted,
                                 created_at=answer.created_at,
                                 author_id=answer.author_id,
                                 question_id=answer.question_id,
                                 score=scores_dict.get(answer.id, 0),
                                 my_vote=my_votes_dict.get(answer.id, None)))
    return result

@answer_router.patch("/answers/{answer_id}", response_model=AnswerRead)
async def patch_answer(answer_id: int,
                       answer_data: AnswerUpdate,
                       current_user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    answer = (await db.execute(select(Answer).where(Answer.id == answer_id))).scalar_one_or_none()
    if answer is None:
        raise HTTPException(status_code=404, detail="Answer not found")
    if answer.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    update_answer_data = answer_data.model_dump(exclude_unset=True)
    for key, value in update_answer_data.items():
        setattr(answer, key, value)
    score = await get_score(db, answer_id=answer_id)
    my_vote = await get_my_vote(db, current_user.id, answer_id=answer_id)
    await db.commit()
    await db.refresh(answer)
    return AnswerRead(id=answer.id,
                      body=answer.body,
                      is_accepted=answer.is_accepted,
                      created_at=answer.created_at,
                      author_id=answer.author_id,
                      question_id=answer.question_id,
                      score=score,
                      my_vote=my_vote)

@answer_router.delete("/answers/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def del_answer(answer_id: int,
                     current_user: User = Depends(get_current_user),
                     db: AsyncSession = Depends(get_db)):
    answer = (await db.execute(select(Answer).where(Answer.id == answer_id))).scalar_one_or_none()
    if answer is None:
        raise HTTPException(status_code=404, detail="Answer not found")
    if answer.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await db.delete(answer)
    await db.commit()

@answer_router.patch("/answers/{answer_id}/accept", response_model=AnswerRead)
async def right_answer(answer_id: int,
                       current_user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    answer = (await db.execute(select(Answer).where(Answer.id == answer_id))).scalar_one_or_none()
    if answer is None:
        raise HTTPException(status_code=404, detail="Answer not found")
    related_question = (await db.execute(select(Question).where(Question.id == answer.question_id))).scalar_one_or_none()
    if current_user.id != related_question.author_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    accepted_answer = (await db.execute(select(Answer).where(Answer.question_id == answer.question_id, Answer.is_accepted == True))).scalar_one_or_none()
    if accepted_answer is not None and accepted_answer.id != answer.id:
        accepted_answer.is_accepted = False
    if accepted_answer is None or accepted_answer.id != answer.id:
        await apply_reputation_change(db, answer.author_id, 20)
    answer.is_accepted = True
    score = await get_score(db, answer_id=answer_id)
    my_vote = await get_my_vote(db, current_user.id, answer_id=answer_id)
    await db.commit()
    await db.refresh(answer)
    return AnswerRead(id=answer.id,
                      body=answer.body,
                      is_accepted=answer.is_accepted,
                      created_at=answer.created_at,
                      author_id=answer.author_id,
                      question_id=answer.question_id,
                      score=score,
                      my_vote=my_vote)
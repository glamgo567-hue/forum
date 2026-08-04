from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies.auth import get_current_user, get_current_user_optional
from app.dependencies.db import get_db
from app.models.question_model import Question
from app.models.tag_model import Tag
from app.models.user_model import User
from app.models.vote_model import Vote
from app.schemas.question_schemas import QuestionCreate, QuestionRead, QuestionUpdate
from app.services.vote_helpers import get_my_vote, get_score

question_router = APIRouter(prefix="/questions", tags=["questions"])

@question_router.post("/", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
async def create_question(quest_data: QuestionCreate,
                          current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    new_question = Question(title=quest_data.title,
                            body=quest_data.body,
                            author_id=current_user.id,)
    tag_names = set(quest_data.tags)
    existing_tags = (await db.execute(select(Tag).where(Tag.name.in_(tag_names)))).scalars().all()

    existing_names = {tag.name for tag in existing_tags}
    new_names = tag_names - existing_names

    new_tags = [Tag(name=name) for name in new_names]
    db.add_all(new_tags)

    new_question.tags = existing_tags + new_tags

    db.add(new_question)
    await db.commit()
    await db.refresh(new_question, attribute_names=["id", "title", "body", "created_at", "author_id"])
    return QuestionRead(id=new_question.id,
                        title=new_question.title,
                        body=new_question.body,
                        author_id=new_question.author_id,
                        created_at=new_question.created_at,
                        tags=new_question.tags,
                        score=0,
                        my_vote=None)

@question_router.get("/", response_model=list[QuestionRead])
async def show_questions(skip: int = 0,
                         limit: int = 10,
                         tag: str | None = None,
                         current_user: User | None = Depends(get_current_user_optional),
                         db: AsyncSession = Depends(get_db)):
    query = select(Question).options(selectinload(Question.tags))
    if tag is not None:
        query = query.join(Question.tags).where(Tag.name == tag)
    query = query.offset(skip).limit(limit)

    questions = (await db.execute(query)).scalars().all()
    question_ids = [q.id for q in questions]

    scores_dict = {question_id: score for question_id, score in (await db.execute(select(Vote.question_id, func.coalesce(func.sum(Vote.value), 0)).where(Vote.question_id.in_(question_ids)).group_by(Vote.question_id))).all()}

    if current_user is None:
        my_votes_dict = {}
    else:
        my_votes_dict = {question_id: value for question_id, value in (await db.execute(select(Vote.question_id, Vote.value).where(Vote.question_id.in_(question_ids), Vote.user_id == current_user.id))).all()}

    result = []
    for question in questions:
        result.append(QuestionRead(id=question.id,
                                   title=question.title,
                                   body=question.body,
                                   author_id=question.author_id,
                                   created_at=question.created_at,
                                   tags=question.tags,
                                   score=scores_dict.get(question.id, 0),
                                   my_vote=my_votes_dict.get(question.id, None)))
    return result

@question_router.get("/{question_id}", response_model=QuestionRead)
async def show_question(question_id: int,
                        current_user: User | None = Depends(get_current_user_optional), 
                        db: AsyncSession = Depends(get_db)):
    question = (await db.execute(select(Question).options(selectinload(Question.tags)).where(Question.id == question_id))).scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    score = await get_score(db, question_id=question_id)

    my_vote = await get_my_vote(db, current_user.id if current_user else None, question_id=question_id)

    return QuestionRead(id=question.id,
                        title=question.title,
                        body=question.body,
                        author_id=question.author_id,
                        created_at=question.created_at,
                        tags=question.tags,
                        score=score,
                        my_vote=my_vote)

@question_router.patch("/{question_id}", response_model=QuestionRead)
async def patch_question(question_id: int,
                         quest_data: QuestionUpdate,
                         current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    question = (await db.execute(select(Question).options(selectinload(Question.tags)).where(Question.id == question_id))).scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    if question.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    update_quest_data = quest_data.model_dump(exclude_unset=True)
    for key, value in update_quest_data.items():
        setattr(question, key, value)
    score = await get_score(db, question_id=question_id)
    
    my_vote = await get_my_vote(db, current_user.id, question_id=question_id)
    
    await db.commit()
    await db.refresh(question)
    return QuestionRead(id=question.id,
                        title=question.title,
                        body=question.body,
                        author_id=question.author_id,
                        created_at=question.created_at,
                        tags=question.tags,
                        score=score,
                        my_vote=my_vote)

@question_router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def del_question(question_id: int,
                         current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    question = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    if question.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await db.delete(question)
    await db.commit()
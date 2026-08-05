import os

from dotenv import load_dotenv

load_dotenv(".env.test", override=True)

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.dependencies.db import get_db
from app.main import app
from app.models.base_model import Base

engine = create_async_engine(os.environ["DATABASE_URL"])
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,)

async def override_get_db():
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
async def db_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(db_schema):
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_headers(client):
    payload_auth = {"username": "glamgo2",
                    "email": "glamgo@gmail.com",
                    "password": "111111111",
                    "confirm_password": "111111111"}
    await client.post("/auth/register", json=payload_auth)

    payload_log = {"username":"glamgo2",
                    "password":"111111111"}
    response_log = await client.post("/auth/login", data=payload_log)

    token_data = response_log.json()
    token = token_data.get("access_token")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def dop_auth_headers(client):
    payload_auth = {"username": "glamgo3",
                    "email": "glamgo3@gmail.com",
                    "password": "111111111",
                    "confirm_password": "111111111"}
    await client.post("/auth/register", json=payload_auth)

    payload_log = {"username":"glamgo3",
                    "password":"111111111"}
    response_log = await client.post("/auth/login", data=payload_log)

    token_data = response_log.json()
    token = token_data.get("access_token")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def question(client, auth_headers):
    payload_question = {"title": "Steak doneness?",
                        "body": "How do I check medium-rare?",
                        "tags": ["cooking"]}
    response = await client.post("/questions", json=payload_question, headers=auth_headers)
    return response.json()

@pytest.fixture
async def answer(client, auth_headers, question):
    payload = {"body": "Rest it 5 minutes, internal temp ~135°F.", 
               "question_id": question["id"]}
    response = await client.post(f"/questions/{question['id']}/answers", json=payload, headers=auth_headers)
    return response.json()
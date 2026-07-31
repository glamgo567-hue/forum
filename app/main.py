from fastapi import FastAPI, status

from app.routers.auth_router import auth_router

app = FastAPI()

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy"}

app.include_router(auth_router)
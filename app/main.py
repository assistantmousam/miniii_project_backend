
from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.core.config import settings


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)


@app.get("/")
def root():
    return {
        "message": "DSA Arcade API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


app.include_router(auth_router)
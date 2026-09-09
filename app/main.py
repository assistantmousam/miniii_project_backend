from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.core.config import settings
from app.api.game import router as game_router


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


# Include API routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(game_router)

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.game import router as game_router
from app.api.qotd import router as qotd_router
from app.api.leaderboard import router as leaderboard_router
from app.api.notifications import router as notifications_router
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


# Include API routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(game_router)
app.include_router(qotd_router)
app.include_router(leaderboard_router)
app.include_router(notifications_router)


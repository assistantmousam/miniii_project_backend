from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.game import router as game_router
from app.api.qotd import router as qotd_router
from app.api.leaderboard import router as leaderboard_router
from app.api.notifications import router as notifications_router
from app.api.admin_users import router as admin_users_router
from app.api.admin_audit import router as admin_audit_router
from app.api.admin_game import router as admin_game_router
from app.api.admin_analytics import router as admin_analytics_router

from app.core.config import settings
from app.core.security_middleware import SecurityHeadersMiddleware


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


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],
)


app.add_middleware(
    SecurityHeadersMiddleware,
)


# Include API routers

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(game_router)
app.include_router(qotd_router)
app.include_router(leaderboard_router)
app.include_router(notifications_router)
app.include_router(admin_users_router)
app.include_router(admin_audit_router)
app.include_router(admin_game_router)
app.include_router(admin_analytics_router)
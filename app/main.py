# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy import text

# from app.core.config import settings
# from app.core.security_middleware import SecurityHeadersMiddleware
# from app.db.database import SessionLocal

# from app.api.auth import router as auth_router
# from app.api.users import router as users_router
# from app.api.game import router as game_router
# from app.api.qotd import router as qotd_router
# from app.api.leaderboard import router as leaderboard_router
# from app.api.notifications import router as notifications_router
# from app.api.admin_users import router as admin_users_router
# from app.api.admin_audit import router as admin_audit_router
# from app.api.admin_game import router as admin_game_router
# from app.api.admin_analytics import router as admin_analytics_router


# app = FastAPI(
#     title=settings.APP_NAME,
#     version=settings.APP_VERSION,
# )


# @app.get("/")
# def root():
#     return {
#         "message": "DSA Arcade API is running"
#     }


# @app.get("/health")
# def health():
#     return {
#         "status": "healthy"
#     }


# @app.get("/health/database")
# def database_health():
#     db = SessionLocal()

#     try:
#         db.execute(text("SELECT 1"))

#         return {
#             "status": "ok",
#             "database": "connected",
#         }

#     except Exception as exc:
#         raise HTTPException(
#             status_code=503,
#             detail={
#                 "status": "error",
#                 "database": "disconnected",
#                 "message": str(exc),
#             },
#         ) from exc

#     finally:
#         db.close()


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.cors_origins_list,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.add_middleware(
#     SecurityHeadersMiddleware
# )


# app.include_router(auth_router)
# app.include_router(users_router)
# app.include_router(game_router)
# app.include_router(qotd_router)
# app.include_router(leaderboard_router)
# app.include_router(notifications_router)
# app.include_router(admin_users_router)
# app.include_router(admin_audit_router)
# app.include_router(admin_game_router)
# app.include_router(admin_analytics_router)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.security_middleware import SecurityHeadersMiddleware
from app.db.database import SessionLocal

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


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# SECURITY HEADERS
# ============================================================

app.add_middleware(
    SecurityHeadersMiddleware
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "DSA Arcade API is running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# DATABASE HEALTH CHECK
# ============================================================

@app.get("/health/database")
def database_health():
    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "connected",
        }

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "database": "disconnected",
                "message": str(exc),
            },
        ) from exc

    finally:
        db.close()


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(game_router)
app.include_router(qotd_router)
app.include_router(leaderboard_router)
app.include_router(notifications_router)

# Admin APIs
app.include_router(admin_users_router)
app.include_router(admin_audit_router)
app.include_router(admin_game_router)
app.include_router(admin_analytics_router)
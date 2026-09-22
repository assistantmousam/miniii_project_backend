from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services.auth_service import (
    login_user,
    register_user,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"],
)


@router.get("/check-username")
def check_username(
    username: str,
    db: Session = Depends(get_db),
):
    existing = db.scalar(
        select(User).where(User.username == username)
    )

    if existing:
        return {
            "available": False,
            "message": "Username already taken",
        }

    return {
        "available": True,
        "message": "Username available",
    }


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        user = register_user(
            db=db,
            data=data,
        )

        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except Exception as e:
        db.rollback()

        print("=" * 70)
        print("REGISTER ERROR")
        print("=" * 70)
        print(type(e).__name__)
        print(str(e))
        print("=" * 70)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {type(e).__name__}: {str(e)}",
        )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        return login_user(
            db=db,
            data=data,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    except Exception as e:
        db.rollback()

        print("=" * 70)
        print("LOGIN ERROR")
        print("=" * 70)
        print(type(e).__name__)
        print(str(e))
        print("=" * 70)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {type(e).__name__}: {str(e)}",
        )
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    refresh_access_token,
    verify_password,
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"],
)


# ============================================================
# CHECK USERNAME
# ============================================================

@router.get("/check-username")
def check_username(
    username: str = Query(..., min_length=3, max_length=20),
    db: Session = Depends(get_db),
):
    username = username.strip()

    user = db.scalar(
        select(User).where(User.username == username)
    )

    if user:
        return {
            "available": False,
            "message": "Username is already taken",
        }

    return {
        "available": True,
        "message": "Username available",
    }


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    username = data.username.strip()
    email = str(data.email).lower().strip()

    existing_username = db.scalar(
        select(User).where(User.username == username)
    )

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already taken",
        )

    existing_email = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(data.password),
        display_name=data.display_name,
        role="learner",
        is_active=True,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    email = str(data.email).lower().strip()

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(
        data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }


# ============================================================
# REFRESH
# ============================================================

@router.post("/refresh")
def refresh(
    data: RefreshTokenRequest,
):
    return refresh_access_token(data.refresh_token)


# ============================================================
# ME
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def me(
    current_user: User = Depends(get_current_user),
):
    return current_user


# ============================================================
# LOGOUT
# ============================================================

@router.post("/logout")
def logout():
    return {
        "message": "Logged out successfully"
    }
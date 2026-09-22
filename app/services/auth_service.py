from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest


def register_user(
    db: Session,
    data: RegisterRequest,
) -> User:
    username = data.username.strip()
    email = str(data.email).lower().strip()

    existing_user = db.scalar(
        select(User).where(
            or_(
                User.email == email,
                User.username == username,
            )
        )
    )

    if existing_user:
        if existing_user.email == email:
            raise ValueError("Email already registered")

        if existing_user.username == username:
            raise ValueError("Username already taken")

    user = User(
        email=email,
        username=username,
        password_hash=hash_password(data.password),
        display_name=data.display_name,
        role="player",
        is_verified=False,
        is_active=True,
        auth_provider="local",
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User:
    email = email.strip().lower()

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if user is None:
        raise ValueError("Incorrect email or password")

    if not user.password_hash:
        raise ValueError(
            "This account does not use password authentication"
        )

    if not verify_password(
        password,
        user.password_hash,
    ):
        raise ValueError("Incorrect email or password")

    if not user.is_active:
        raise ValueError("User account is inactive")

    return user


def login_user(
    db: Session,
    data: LoginRequest,
) -> dict:
    user = authenticate_user(
        db=db,
        email=str(data.email),
        password=data.password,
    )

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }
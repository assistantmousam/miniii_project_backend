from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest


def register_user(
    db: Session,
    data: RegisterRequest,
) -> User:
    existing_user = db.scalar(
        select(User).where(
            or_(
                User.email == data.email,
                User.username == data.username,
            )
        )
    )

    if existing_user:
        if existing_user.email == data.email:
            raise ValueError("Email already registered")

        if existing_user.username == data.username:
            raise ValueError("Username already taken")

    user = User(
        email=data.email,
        username=data.username,
        password_hash=hash_password(data.password),
        display_name=data.display_name,
        role="player",
        is_verified=False,
        is_active=True,
        auth_provider="local",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User:
    user = db.scalar(
        select(User).where(User.email == email)
    )

    if user is None:
        raise ValueError("Incorrect email or password")

    if not user.password_hash:
        raise ValueError(
            "This account does not use password authentication"
        )

    if not verify_password(password, user.password_hash):
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
        email=data.email,
        password=data.password,
    )

    access_token = create_access_token(
        str(user.id)
    )

    refresh_token = create_refresh_token(
        str(user.id)
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.auth import RegisterRequest


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
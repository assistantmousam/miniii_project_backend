from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.admin_security import get_current_admin
from app.db.database import get_db
from app.models.user import User
from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/api/v1/admin/users",
    tags=["Admin - Users"],
)


@router.get("")
def list_users(
    search: str | None = Query(default=None),
    role: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    query = select(User)

    if search:
        query = query.where(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.display_name.ilike(f"%{search}%"),
            )
        )

    if role:
        query = query.where(User.role == role)

    if is_active is not None:
        query = query.where(User.is_active == is_active)

    query = (
        query
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    users = db.scalars(query).all()

    return [
        {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "display_name": user.display_name,
            "role": user.role,
            "is_verified": user.is_verified,
            "is_active": user.is_active,
            "created_at": user.created_at,
        }
        for user in users
    ]


@router.get("/{user_id}")
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = db.scalar(
        select(User).where(User.id == user_id)
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "display_name": user.display_name,
        "role": user.role,
        "is_verified": user.is_verified,
        "is_active": user.is_active,
        "auth_provider": user.auth_provider,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


@router.patch("/{user_id}/suspend")
def suspend_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = db.scalar(
        select(User).where(User.id == user_id)
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if user.id == current_admin.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot suspend yourself",
        )

    user.is_active = False

    create_audit_log(
        db=db,
        admin_id=current_admin.id,
        action="SUSPEND_USER",
        entity_type="USER",
        entity_id=str(user.id),
        details={
            "username": user.username,
        },
    )

    db.commit()

    return {
        "message": "User suspended successfully",
        "user_id": str(user.id),
    }


@router.patch("/{user_id}/activate")
def activate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = db.scalar(
        select(User).where(User.id == user_id)
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    user.is_active = True

    create_audit_log(
        db=db,
        admin_id=current_admin.id,
        action="ACTIVATE_USER",
        entity_type="USER",
        entity_id=str(user.id),
        details={
            "username": user.username,
        },
    )

    db.commit()

    return {
        "message": "User activated successfully",
        "user_id": str(user.id),
    }
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.admin_security import get_current_admin
from app.db.database import get_db
from app.models.game_level import GameLevel
from app.models.user import User
from app.schemas.admin_game import (
    AdminLevelResponse,
    LevelCreateRequest,
    LevelUpdateRequest,
)
from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/api/v1/admin/game",
    tags=["Admin - Game"],
)


def level_to_response(level: GameLevel) -> AdminLevelResponse:
    return AdminLevelResponse(
        id=str(level.id),
        level_number=level.level_number,
        title=level.title,
        description=level.description,
        topic=level.topic,
        difficulty=level.difficulty,
        unlock_requires=level.unlock_requires,
        icon_url=level.icon_url,
        order_index=level.order_index,
        is_active=level.is_active,
    )


@router.post(
    "/levels",
    response_model=AdminLevelResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_level(
    data: LevelCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    existing = db.scalar(
        select(GameLevel).where(
            GameLevel.level_number == data.level_number
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Level number already exists",
        )

    level = GameLevel(
        level_number=data.level_number,
        title=data.title,
        description=data.description,
        topic=data.topic,
        difficulty=data.difficulty,
        unlock_requires=data.unlock_requires,
        icon_url=data.icon_url,
        order_index=data.order_index,
        is_active=data.is_active,
    )

    db.add(level)
    db.flush()

    create_audit_log(
        db=db,
        admin_id=admin.id,
        action="CREATE",
        entity_type="GAME_LEVEL",
        entity_id=str(level.id),
        details={
            "level_number": level.level_number,
            "title": level.title,
        },
    )

    db.commit()
    db.refresh(level)

    return level_to_response(level)


@router.get(
    "/levels",
    response_model=list[AdminLevelResponse],
)
def list_levels(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    levels = db.scalars(
        select(GameLevel).order_by(GameLevel.order_index)
    ).all()

    return [
        level_to_response(level)
        for level in levels
    ]


@router.get(
    "/levels/{level_id}",
    response_model=AdminLevelResponse,
)
def get_level(
    level_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    level = db.scalar(
        select(GameLevel).where(
            GameLevel.id == level_id
        )
    )

    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Level not found",
        )

    return level_to_response(level)


@router.patch(
    "/levels/{level_id}",
    response_model=AdminLevelResponse,
)
def update_level(
    level_id: uuid.UUID,
    data: LevelUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    level = db.scalar(
        select(GameLevel).where(
            GameLevel.id == level_id
        )
    )

    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Level not found",
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    if "level_number" in update_data:
        existing = db.scalar(
            select(GameLevel).where(
                GameLevel.level_number == update_data["level_number"],
                GameLevel.id != level.id,
            )
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Level number already exists",
            )

    for field, value in update_data.items():
        setattr(level, field, value)

    create_audit_log(
        db=db,
        admin_id=admin.id,
        action="UPDATE",
        entity_type="GAME_LEVEL",
        entity_id=str(level.id),
        details=update_data,
    )

    db.commit()
    db.refresh(level)

    return level_to_response(level)


@router.delete(
    "/levels/{level_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_level(
    level_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    level = db.scalar(
        select(GameLevel).where(
            GameLevel.id == level_id
        )
    )

    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Level not found",
        )

    create_audit_log(
        db=db,
        admin_id=admin.id,
        action="DELETE",
        entity_type="GAME_LEVEL",
        entity_id=str(level.id),
        details={
            "level_number": level.level_number,
            "title": level.title,
        },
    )

    db.delete(level)
    db.commit()

    return None
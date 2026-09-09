
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User

from app.schemas.game import (
    HintResponse,
    LevelResponse,
    SolutionResponse,
    StageResponse,
    StartStageResponse,
)

from app.schemas.scoring import (
    StageScoreResponse,
    StageSubmissionRequest,
)

from app.services.game_service import (
    get_all_levels,
    get_level_by_id,
    get_stage_by_id,
    get_user_stage_progress,
    is_level_unlocked,
    is_stage_unlocked,
    start_stage,
)

from app.services.scoring_service import process_stage_score


router = APIRouter(
    prefix="/api/v1",
    tags=["Game"],
)


@router.get(
    "/levels",
    response_model=list[LevelResponse],
)
def get_levels(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    levels = get_all_levels(db)

    return [
        LevelResponse(
            id=str(level.id),
            level_number=level.level_number,
            title=level.title,
            description=level.description,
            topic=level.topic,
            difficulty=level.difficulty,
            icon_url=level.icon_url,
            order_index=level.order_index,
            is_active=level.is_active,
            is_locked=not is_level_unlocked(
                db,
                current_user.id,
                level,
            ),
        )
        for level in levels
    ]


@router.get("/levels/{level_id}")
def get_level(
    level_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    level = get_level_by_id(db, level_id)

    if level is None:
        raise HTTPException(
            status_code=404,
            detail="Level not found",
        )

    if not is_level_unlocked(
        db,
        current_user.id,
        level,
    ):
        raise HTTPException(
            status_code=403,
            detail="Level is locked",
        )

    stages = sorted(
        level.stages,
        key=lambda stage: stage.order_index,
    )

    return {
        "id": str(level.id),
        "level_number": level.level_number,
        "title": level.title,
        "description": level.description,
        "topic": level.topic,
        "difficulty": level.difficulty,
        "icon_url": level.icon_url,
        "stages": [
            {
                "id": str(stage.id),
                "stage_number": stage.stage_number,
                "title": stage.title,
                "difficulty": stage.difficulty,
                "challenge_type": stage.challenge_type,
                "time_limit": stage.time_limit,
                "passing_score": stage.passing_score,
                "max_hints": stage.max_hints,
                "is_locked": not is_stage_unlocked(
                    db,
                    current_user.id,
                    stage,
                ),
            }
            for stage in stages
        ],
    }


@router.get(
    "/stages/{stage_id}",
    response_model=StageResponse,
)
def get_stage(
    stage_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stage = get_stage_by_id(db, stage_id)

    if stage is None:
        raise HTTPException(
            status_code=404,
            detail="Stage not found",
        )

    if not is_stage_unlocked(
        db,
        current_user.id,
        stage,
    ):
        raise HTTPException(
            status_code=403,
            detail="Stage is locked",
        )

    return StageResponse(
        id=str(stage.id),
        level_id=str(stage.level_id),
        stage_number=stage.stage_number,
        title=stage.title,
        difficulty=stage.difficulty,
        challenge_type=stage.challenge_type,
        challenge_data=stage.challenge_data,
        time_limit=stage.time_limit,
        passing_score=stage.passing_score,
        max_hints=stage.max_hints,
        order_index=stage.order_index,
        is_locked=False,
    )


@router.post(
    "/stages/{stage_id}/start",
    response_model=StartStageResponse,
)
def start_game_stage(
    stage_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stage = get_stage_by_id(db, stage_id)

    if stage is None:
        raise HTTPException(
            status_code=404,
            detail="Stage not found",
        )

    if not is_stage_unlocked(
        db,
        current_user.id,
        stage,
    ):
        raise HTTPException(
            status_code=403,
            detail="Stage is locked",
        )

    progress = start_stage(
        db,
        current_user.id,
        stage,
    )

    return StartStageResponse(
        stage_id=str(stage.id),
        status=progress.status,
        message="Stage started successfully",
    )


@router.post(
    "/stages/{stage_id}/hint",
    response_model=HintResponse,
)
def get_hint(
    stage_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stage = get_stage_by_id(db, stage_id)

    if stage is None:
        raise HTTPException(
            status_code=404,
            detail="Stage not found",
        )

    if not is_stage_unlocked(
        db,
        current_user.id,
        stage,
    ):
        raise HTTPException(
            status_code=403,
            detail="Stage is locked",
        )

    progress = get_user_stage_progress(
        db,
        current_user.id,
        stage.id,
    )

    if progress is None:
        raise HTTPException(
            status_code=400,
            detail="Start the stage first",
        )

    if progress.hints_used >= stage.max_hints:
        raise HTTPException(
            status_code=400,
            detail="Maximum hints reached",
        )

    challenge_data = stage.challenge_data or {}
    hints = challenge_data.get("hints", [])

    hint_number = progress.hints_used + 1

    if hint_number > len(hints):
        raise HTTPException(
            status_code=400,
            detail="No more hints available",
        )

    progress.hints_used += 1

    db.commit()

    return HintResponse(
        stage_id=str(stage.id),
        hint_number=hint_number,
        hint=hints[hint_number - 1],
        penalty=10,
    )


@router.get(
    "/stages/{stage_id}/solution",
    response_model=SolutionResponse,
)
def get_solution(
    stage_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stage = get_stage_by_id(db, stage_id)

    if stage is None:
        raise HTTPException(
            status_code=404,
            detail="Stage not found",
        )

    progress = get_user_stage_progress(
        db,
        current_user.id,
        stage.id,
    )

    if progress is None or progress.status != "completed":
        raise HTTPException(
            status_code=403,
            detail="Solution is available after completing the stage",
        )

    return SolutionResponse(
        stage_id=str(stage.id),
        solution_data=stage.solution_data or {},
    )


@router.post(
    "/stages/{stage_id}/submit",
    response_model=StageScoreResponse,
)
def submit_game_stage(
    stage_id: UUID,
    data: StageSubmissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stage = get_stage_by_id(db, stage_id)

    if stage is None:
        raise HTTPException(
            status_code=404,
            detail="Stage not found",
        )

    if not is_stage_unlocked(
        db,
        current_user.id,
        stage,
    ):
        raise HTTPException(
            status_code=403,
            detail="Stage is locked",
        )

    progress = get_user_stage_progress(
        db,
        current_user.id,
        stage.id,
    )

    if progress is None:
        raise HTTPException(
            status_code=400,
            detail="Start the stage before submitting",
        )

    if progress.status == "completed":
        raise HTTPException(
            status_code=409,
            detail="Stage already completed",
        )

    challenge_data = stage.challenge_data or {}

    expected_answer = challenge_data.get(
        "correct_answer"
    )

    is_correct = (
        data.answer == expected_answer
    )

    progress.attempts += 1

    (
        breakdown,
        xp_earned,
        user_score,
    ) = process_stage_score(
        db=db,
        user_id=current_user.id,
        progress=progress,
        stage=stage,
        is_correct=is_correct,
        time_taken=data.time_taken,
        operations_used=data.operations_used,
    )

    return StageScoreResponse(
        stage_id=str(stage.id),
        status=progress.status,
        passed=progress.status == "completed",
        score=breakdown["total_score"],
        score_breakdown=breakdown,
        xp_earned=xp_earned,
        total_xp=user_score.xp,
        player_level=user_score.player_level,
        message=(
            "Stage completed successfully"
            if progress.status == "completed"
            else "Stage failed. You can retry."
        ),
    )


from pydantic import BaseModel, Field


class StageSubmissionRequest(BaseModel):
    answer: dict

    time_taken: int = Field(
        default=0,
        ge=0,
    )

    operations_used: int = Field(
        default=0,
        ge=0,
    )


class ScoreBreakdown(BaseModel):
    correctness: float
    time_bonus: float
    efficiency: float
    no_hint: float
    total_score: int


class StageScoreResponse(BaseModel):
    stage_id: str
    status: str
    passed: bool
    score: int
    score_breakdown: ScoreBreakdown
    xp_earned: int
    total_xp: int
    player_level: int
    message: str
from pydantic import BaseModel


class LevelResponse(BaseModel):
    id: str
    level_number: int
    title: str
    description: str | None
    topic: str
    difficulty: str
    icon_url: str | None
    order_index: int
    is_active: bool
    is_locked: bool


class StageResponse(BaseModel):
    id: str
    level_id: str
    stage_number: int
    title: str
    difficulty: str
    challenge_type: str
    challenge_data: dict
    time_limit: int | None
    passing_score: int
    max_hints: int
    order_index: int
    is_locked: bool


class StartStageResponse(BaseModel):
    stage_id: str
    status: str
    message: str


class SubmitStageResponse(BaseModel):
    stage_id: str
    status: str
    score: int
    passed: bool
    message: str


class HintResponse(BaseModel):
    stage_id: str
    hint_number: int
    hint: str
    penalty: int


class SolutionResponse(BaseModel):
    stage_id: str
    solution_data: dict
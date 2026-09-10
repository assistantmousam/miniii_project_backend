from pydantic import BaseModel


class AdminOverviewResponse(BaseModel):
    total_users: int
    active_users: int
    verified_users: int
    total_levels: int
    active_levels: int
    total_stages: int
    total_questions: int


class UserActivityResponse(BaseModel):
    dau: int
    mau: int


class LevelCompletionResponse(BaseModel):
    level_id: str
    level_number: int
    title: str
    total_completions: int
    average_score: float


class PopularLevelResponse(BaseModel):
    level_id: str
    level_number: int
    title: str
    attempts: int


class AdminAnalyticsResponse(BaseModel):
    overview: AdminOverviewResponse
    activity: UserActivityResponse
    level_completion: list[LevelCompletionResponse]
    popular_levels: list[PopularLevelResponse]
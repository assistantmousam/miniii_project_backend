from pydantic import BaseModel


class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    score: int
    badge: str | None
    is_current_user: bool


class LeaderboardResponse(BaseModel):
    period: str
    page: int
    page_size: int
    total_users: int
    total_pages: int
    entries: list[LeaderboardEntry]
    current_user_rank: int | None
    current_user_score: int
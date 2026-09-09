from pydantic import BaseModel, EmailStr, Field


class UserProfileResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    display_name: str | None
    avatar_url: str | None
    bio: str | None
    role: str
    is_verified: bool
    is_active: bool


class UserProfileUpdate(BaseModel):
    display_name: str | None = Field(
        default=None,
        max_length=100,
    )

    avatar_url: str | None = Field(
        default=None,
        max_length=500,
    )

    bio: str | None = Field(
        default=None,
        max_length=1000,
    )


class PublicUserProfile(BaseModel):
    username: str
    display_name: str | None
    avatar_url: str | None
    bio: str | None


class UserProgressResponse(BaseModel):
    stage_id: str
    level_id: str
    status: str
    score: int
    highest_score: int
    attempts: int
    hints_used: int
    time_taken: int


class UserStatsResponse(BaseModel):
    total_score: int
    daily_score: int
    weekly_score: int
    monthly_score: int
    xp: int
    player_level: int
    completed_stages: int
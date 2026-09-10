from pydantic import BaseModel, Field


class LevelCreateRequest(BaseModel):
    level_number: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=100)
    description: str | None = None
    topic: str = Field(min_length=1, max_length=100)
    difficulty: str = Field(min_length=1, max_length=20)
    unlock_requires: int | None = Field(default=None, ge=1)
    icon_url: str | None = None
    order_index: int = Field(default=0, ge=0)
    is_active: bool = True


class LevelUpdateRequest(BaseModel):
    level_number: int | None = Field(default=None, ge=1)
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    topic: str | None = Field(default=None, min_length=1, max_length=100)
    difficulty: str | None = Field(default=None, min_length=1, max_length=20)
    unlock_requires: int | None = Field(default=None, ge=1)
    icon_url: str | None = None
    order_index: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class AdminLevelResponse(BaseModel):
    id: str
    level_number: int
    title: str
    description: str | None
    topic: str
    difficulty: str
    unlock_requires: int | None
    icon_url: str | None
    order_index: int
    is_active: bool
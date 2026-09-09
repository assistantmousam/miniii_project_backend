from datetime import datetime

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    unread_count: int


class NotificationPreferencesResponse(BaseModel):
    badge_notifications: bool
    leaderboard_notifications: bool
    email_notifications: bool


class NotificationPreferencesUpdate(BaseModel):
    badge_notifications: bool | None = None
    leaderboard_notifications: bool | None = None
    email_notifications: bool | None = None
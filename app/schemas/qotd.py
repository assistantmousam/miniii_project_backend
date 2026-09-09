from datetime import date, datetime

from pydantic import BaseModel


class QotDResponse(BaseModel):
    question_id: str
    date: date
    type: str
    difficulty: str
    content: dict
    points: int
    streak: int
    multiplier: float


class QotDSubmitRequest(BaseModel):
    answer: dict


class QotDSubmitResponse(BaseModel):
    question_id: str
    is_correct: bool
    base_points: int
    multiplier: float
    points_earned: int
    current_streak: int
    longest_streak: int
    explanation: str | None
    correct_answer: dict | None
    submitted_at: datetime
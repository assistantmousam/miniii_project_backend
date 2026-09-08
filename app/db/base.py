from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.user import User
from app.models.game_level import GameLevel
from app.models.game_stage import GameStage
from app.models.user_progress import UserProgress
from app.models.user_score import UserScore
from app.models.question import Question
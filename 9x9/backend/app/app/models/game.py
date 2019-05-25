from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.moves import Move
from app.models.user import User


class GameBase(BaseModel):
    is_active: bool = True
    is_end: bool = False
    active_users: int = 0
    moves: List[Optional[Move]]
    players: List[Optional[User]]


class GameInDB(GameBase):
    game_id: int
    last_action: Optional[datetime]


class Game(GameInDB):
    pass


class GameCreate(GameBase):
    pass

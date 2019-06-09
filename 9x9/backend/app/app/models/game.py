from enum import Enum
from typing import Optional, List, Set

from pydantic import BaseModel

from app.models.move import Move
from app.models.user import User


class GameStatus(str, Enum):
    PLAYING = 'playing'
    ENDED = 'ended'
    CREATED = 'created'
    WAITING = 'waiting'


class GameBase(BaseModel):
    status: GameStatus = GameStatus.CREATED
    players: List[Optional[User]] = []


class Game(GameBase):
    active_players: Set[int] = set()
    moves: List[Optional[Move]] = []


class GameInDB(GameBase):
    id: int

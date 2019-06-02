from enum import IntEnum
from typing import List, Dict

from pydantic import BaseModel, validator


class GameFieldState(IntEnum):
    empty = 0
    X = 1
    O = -1


class GameModel(IntEnum):
    X = 1
    O = -1


class BorderWinner(IntEnum):
    empty = 0
    X = 1
    O = -1


class Board(BaseModel):
    game_fields: List[List[GameFieldState]]
    border_winner: BorderWinner = BorderWinner.empty

    @validator('game_fields', whole=True)
    def validate_game_board_size(cls, game_fields):
        assert len(game_fields) == 3
        for field in game_fields:
            assert len(field) == 3
        return game_fields


class InnerBoard(Board):
    pass


class OuterBoard(Board):
    game_fields: List[List[InnerBoard]]


class GameModels(BaseModel):
    game_model: Dict[int, GameModel]

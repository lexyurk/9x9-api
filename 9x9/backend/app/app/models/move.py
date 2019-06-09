from typing import List

from pydantic import BaseModel, Schema


class Coordinate(BaseModel):
    x: int = Schema(..., ge=0, le=2, description="Coordinate must be in range 0..2")
    y: int = Schema(..., ge=0, le=2, description="Coordinate must be in range 0..2")


class MoveBase(BaseModel):
    inner_field: Coordinate
    outer_field: Coordinate


class Move(MoveBase):
    player_id: int


class MoveInDB(Move):
    id: int


class GameMove(Move):
    pass


class ResponseGameMove(BaseModel):
    status: str
    last_move: Move
    next_player: int
    outer_field: List[int] = Schema(..., min_length=2, max_length=2, ge=0, le=2)

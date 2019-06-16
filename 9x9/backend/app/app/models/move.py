from typing import List

from pydantic import BaseModel, Schema, validator


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


class MoveRequestSchema(BaseModel):
    inner_field: List[int]
    outer_field: List[int]

    @validator('inner_field', 'outer_field', whole=True)
    def validate_fields(cls, field):
        assert len(field) == 2
        for field_value in field:
            assert 0 <= field_value <= 2
        return field


class MoveResponseSchema(MoveRequestSchema):
    player_id: int


class ResponseGameMove(BaseModel):
    status: str
    last_move: MoveResponseSchema
    next_player: int
    outer_field: List[int] = Schema(..., min_length=2, max_length=2, ge=0, le=2)

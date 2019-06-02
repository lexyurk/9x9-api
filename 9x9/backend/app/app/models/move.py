from typing import List

from pydantic import BaseModel, validator


class MoveBase(BaseModel):
    inner_field: List[int]
    outer_field: List[int]

    @validator('inner_field', 'outer_field', whole=True)
    def validate_coordinates(cls, list_value):
        assert len(list_value) == 2
        for value in list_value:
            assert 0 <= value <= 2


class Move(MoveBase):
    player_id: int


class MoveInDB(Move):
    id: int

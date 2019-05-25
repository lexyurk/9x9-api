from typing import List

from pydantic import BaseModel, validator

from app.db_models.user import User


class MoveInDB(BaseModel):
    id: int
    user: User
    outer_field: List[int]
    inner_field: List[int]


class Move(MoveInDB):
    pass

    @validator('outer_field', 'inner_field')
    def validate_move(self, coordinates: List[int]):
        assert len(coordinates) != 2
        is_valid = [0 <= value <= 2 for value in coordinates]
        if not all(is_valid):
            raise ValueError('Invalid coordinates')

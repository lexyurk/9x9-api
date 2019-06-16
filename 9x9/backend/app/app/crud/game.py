from typing import List

from app.core.game.game import game_manager
from app.db.session import Session
from app.db_models.game import Game
from app.db_models.user import User as DBUser
from app.models.game import GameStatus
from app.models.move import MoveRequestSchema, Coordinate, Move, MoveResponseSchema


def create(db_session: Session, *, creator: DBUser) -> Game:
    game = Game(players=[creator], status=GameStatus.CREATED)
    game_manager.create_game(game.id)
    db_session.add(game)
    db_session.commit()
    db_session.refresh(game)
    return game


def convert_to_move_model(request_move: MoveRequestSchema, user_id: int):
    return Move(
        player_id=user_id,
        inner_field=_convert_to_coordinate(request_move.inner_field),
        outer_field=_convert_to_coordinate(request_move.outer_field)
    )


def convert_to_response_model(move: Move) -> MoveResponseSchema:
    return MoveResponseSchema(
        player_id=move.player_id,
        inner_field=_convert_coordinate_to_list(move.inner_field),
        outer_field=_convert_coordinate_to_list(move.outer_field)
    )


def _convert_to_coordinate(move_coordinate: List[int]) -> Coordinate:
    return Coordinate(x=move_coordinate[0], y=move_coordinate[1])


def _convert_coordinate_to_list(move_coordinate: Coordinate) -> List[int]:
    return [move_coordinate.x, move_coordinate.y]

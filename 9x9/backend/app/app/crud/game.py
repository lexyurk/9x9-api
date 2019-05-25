from fastapi.encoders import jsonable_encoder

from app.db.session import Session
from app.db_models.game import Game
from app.models.game import GameCreate


def create(db_session: Session) -> Game:
    new_game = GameCreate()
    game_in_data = jsonable_encoder(new_game)
    game = Game(**game_in_data)
    db_session.add(game)
    db_session.commit()
    db_session.refresh(game)
    return game

from app.db.session import Session
from app.db_models.game import Game
from app.db_models.user import User as DBUser
from app.models.game import GameStatus


def create(db_session: Session, *, creator: DBUser) -> Game:
    game = Game(players=creator, status=GameStatus.CREATED)
    db_session.add(game)
    db_session.commit()
    db_session.refresh(game)
    return game

from fastapi import HTTPException

from app.core.game.exceptions import GameNotFoundError
from app.core.game.game import game_manager
from app.core.game.game_lobby import GameLobby


def get_game(
        game_id: int,
        game_manager=game_manager
) -> GameLobby:
    game = game_manager.get_game(game_id=game_id)
    return game

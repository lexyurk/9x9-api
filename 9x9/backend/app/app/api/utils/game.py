from fastapi import HTTPException

from app.core.game.exceptions import GameNotFoundError
from app.core.game.game import game_manager
from app.core.game.game_lobby import GameLobby


def get_game(
        game_id: int,
        game_manager=game_manager
) -> GameLobby:
    try:
        game = game_manager.get_game(game_id=game_id)
    except GameNotFoundError:
        raise HTTPException(status_code=404, detail=GameNotFoundError.args[0])
    return game

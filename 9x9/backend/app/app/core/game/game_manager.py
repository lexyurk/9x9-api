from typing import Dict

from app.core.game.exceptions import GameNotFoundError
from app.core.game.game_lobby import GameLobby


class GamesManager:
    active_games: int = 0
    games: Dict[int, GameLobby]

    def __init__(self):
        self.games = {}

    def create_game(self, game_id: int):
        self.games[game_id] = GameLobby()
        self.active_games += 1

    def get_game(self, game_id: int):
        if game_id not in self.games.keys():
            raise GameNotFoundError("Game not found")
        return self.games[game_id]

    def remove_game(self, game_id: int):
        if game_id not in self.games:
            raise GameNotFoundError("Game not found")

        del self.games[game_id]
        self.active_games -= 1


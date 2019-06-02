from typing import Dict

from app.core.game.game_lobby import GameLobby


class GamesManager:
    active_games: int = 0
    games: Dict[int, GameLobby]

    def __init__(self):
        self.games = {}

    def add_game(self, game_id: int):
        self.games[game_id] = GameLobby()

    def get_game(self, game_id: int):
        return self.games[game_id]

    def remove_game(self, game_id: int):
        if game_id in self.games:
            del self.games[game_id]
        else:
            raise ValueError("Game not found")

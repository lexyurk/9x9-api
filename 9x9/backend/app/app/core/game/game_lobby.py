from app.core.game.exceptions import LobbyIsFullError, UserNotFoundException
from app.models.field import OuterBoard, InnerBoard, GameFieldState, GameModels, BorderWinner
from app.models.game import Game, GameStatus
from app.models.move import GameMove
from app.models.user import User


class GameLobby:
    game: Game
    board: OuterBoard
    game_figures: GameModels
    last_move: GameMove

    def __init__(self):
        self.game = Game()

        game_board = self.initialize_game_board()
        self.board = OuterBoard(**game_board)

    def initialize_game_board(self):
        inner_game_board = dict(
            game_fields=[[GameFieldState.empty for _ in range(3)] for _ in range(3)]
        )
        game_board = dict(
            game_fields=[[InnerBoard(**inner_game_board) for _ in range(3)] for _ in range(3)]
        )
        return game_board

    def is_user_in_game(self, user: User):
        return user in self.game.players

    def is_available_for_new_user(self):
        return len(self.game.players) < 2

    def is_free_slots(self):
        return len(self.game.active_players) < 2

    def get_game_figure(self, user: User):
        for figure, user_id in self.game_figures.game_model.items():
            if user_id == user.id:
                return figure
        return [figure for figure in GameModel if figure not in self.game_figures.game_model.values()][0]

    def join_game(self, user: User):
        if self.is_user_in_game(user):
            if self.is_free_slots():
                self.game.active_players.add(user.id)
                return True
            else:
                raise LobbyIsFullError("You have already joined this game")
        else:
            if self.is_available_for_new_user():
                self.game.players.append(user)
                self.game.active_players.add(user.id)
                return True

            else:
                raise LobbyIsFullError("Game lobby is full")

    def left_game(self, user: User):
        self.game.active_players.remove(user.id)
        self.update_game_status()

    def get_figure(self, user: User):
        if user.id in self.game_figures.keys():
            return self.game_figures[user.id]

        if len(self.game_figures.keys()) == 2:
            raise UserNotFoundException("You are not member of this game!")

        game_figure = GameFieldState.X if not len(self.game_figures.keys()) else GameFieldState.O

        self.game_figures[user.id] = game_figure
        return game_figure

    def update_game_status(self):
        active_players = len(self.game.active_players)
        if active_players != 2:
            self.game.status = GameStatus.WAITING
        elif self.board.border_winner != BorderWinner.empty:
            self.game.status = GameStatus.ENDED
        else:
            self.game.status = GameStatus.PLAYING


if __name__ == "__main__":
    game_lobby = GameLobby()
    print(game_lobby.board)

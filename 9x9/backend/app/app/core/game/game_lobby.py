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

    def is_field_available(self, field: Move):
        inner_board = self.board.game_fields[field.outer_field.x][field.outer_field.y]
        game_field = inner_board.game_fields[field.inner_field.x][field.inner_field.y]
        return game_field == GameFieldState.empty

    def set_field(self, move: Move):
        inner_board = self.board.game_fields[move.outer_field.x][move.outer_field.y]
        player_figure = self.game_figures.game_model[move.player_id]
        inner_board.game_fields[move.inner_field.x][move.inner_field.y] = player_figure

    def make_move(self, move: Move):
        if not self.is_field_available(move):
            raise FieldNotEmptyError("Field is not empty")

        if self.last_move is not None:
            last_board_coordinates = self.last_move.inner_field
            last_inner_board = self.board.game_fields[last_board_coordinates.x][last_board_coordinates.y]
            if self.last_move.inner_field != move.outer_field and last_inner_board.board_winner == BoardWinner.empty:
                raise WrongOuterFieldException("Selected wrong field")
            if self.game.status != GameStatus.PLAYING:
                raise GameIsWaitingException("Please, wait an opponent!")

        self.set_field(move)
        self.last_move = move
    def check_winner_field(self, field: Coordinate):
        game_board = self.board.game_fields[field.x][field.y]
        board_winner = self.check_board_winner(game_board)
        if board_winner != BoardWinner.empty:
            game_board.board_winner = board_winner
            outer_game_board = [[column.board_winner for column in row] for row in self.board.game_fields]
            outer_game_winner = self.check_board_winner(outer_game_board)
            if outer_game_winner != BoardWinner.empty:
                self.board.board_winner = outer_game_winner

    def check_board_winner(self, game_board) -> BoardWinner:
        # Checks horizontal
        horizontal_winner = [line[0] for line in game_board if len(set(line)) == 1]

        # Check vertical
        vertical_winner = []
        for element in range(3):
            column = [row[element] for row in game_board]
            if len(set(column)) == 1:
                vertical_winner.append(column[0])

        # Check diagonals
        diagonal1 = [game_board[length][length] for length in range(3)]
        diagonal2 = [game_board[length - 1 - length][length] for length in range(3 - 1, -1, -1)]
        diagonal_winner = [diagonal[0] for diagonal in (diagonal1, diagonal2) if len(set(diagonal)) == 1]

        # Check board win
        field_winner = None
        for winner in (horizontal_winner, vertical_winner, diagonal_winner):
            if winner:
                field_winner = winner[0]

        # Update field and outer field if board win
        if field_winner:
            return field_winner
        return BoardWinner.empty


if __name__ == "__main__":
    game_lobby = GameLobby()
    print(game_lobby.board)

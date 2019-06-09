class GameException(Exception):
    pass


class BoardException(GameException):
    pass


class LobbyIsFullError(GameException):
    pass


class UserNotFoundException(GameException):
    pass


class GameNotFoundError(GameException):
    pass


class FieldNotEmptyError(BoardException):
    pass


class WrongOuterFieldException(BoardException):
    pass


class GameIsWaitingException(GameException):
    pass

import typing

from fastapi import APIRouter, Depends
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket

from app import crud
from app.api.utils.db import get_db
from app.api.utils.security import get_current_active_user
from app.db.session import Session
from app.db_models.user import User as DBUser
from app.models.game import Game

router = APIRouter()


@router.post("/create", response_model=Game)
def create_game(
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_active_user),
):
    new_game = crud.game.create(db)
    return new_game.id


@router.websocket_route("/game/{game_id}")
class StartGame(WebSocketEndpoint):

    async def on_connect(self, websocket: WebSocket) -> None:
        pass

    async def on_receive(self, websocket: WebSocket, data: typing.Any) -> None:
        pass

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        pass

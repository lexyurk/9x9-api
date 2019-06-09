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

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost/api/v1/game/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@router.get('/test_websockets')
def test_websockets():
    return HTMLResponse(html)


@router.post('/create')
def create_game(
        *,
        db: Session = Depends(get_db),
        user: DBUser = Depends(get_current_active_user)
):
    game = crud.game.create(db_session=db, creator=user)
    return game.id


@router.websocket_route("/game/{game_id}")
class StartGame(WebSocketEndpoint):

    async def on_connect(self, websocket: WebSocket) -> None:
        pass

    async def on_receive(self, websocket: WebSocket, data: typing.Any) -> None:
        pass

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        pass

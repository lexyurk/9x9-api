from fastapi import Depends, APIRouter
from nejma import Channel, channel_layer
from starlette.endpoints import WebSocketEndpoint
from starlette.responses import HTMLResponse
from starlette.types import Scope
from starlette.websockets import WebSocket

from app import crud
from app.api.utils.db import get_db
from app.api.utils.game import get_game
from app.api.utils.security import get_current_active_user
from app.core.game.exceptions import FieldNotEmptyError, WrongOuterFieldException
from app.core.game.game_lobby import GameLobby
from app.db.session import Session
from app.db_models.user import User as DBUser
from app.models.move import Move, ResponseGameMove

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


@router.websocket_route("/ws")
class Echo(WebSocketEndpoint):
    encoding = "json"
    channel = None

    async def on_connect(self, websocket: WebSocket, **kwargs) -> None:
        await super().on_connect(websocket)
        self.channel = Channel(send=websocket.send)

        await websocket.accept()

    async def on_receive(self, websocket: WebSocket, data):
        room_id = data['room_id']
        message = data['message']
        username = data['username']

        if message.strip():
            group = f"group_{room_id}"

            self.channel_layer.add(group, self.channel)

            payload = {
                "username": username,
                "message": message,
                "room_id": room_id
            }
            await self.channel_layer.group_send(group, payload)

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        pass


@router.websocket_route("/{game_id}/ws")
class GameEndpoint(WebSocketEndpoint):
    encoding = "json"
    channel = None
    channel_layer = None
    game_id: int
    game: GameLobby
    group_id: int

    def __init__(self, game_id: int, scope: Scope):
        self.game_id = game_id
        self.group_id = game_id
        self.game = get_game(game_id)
        self.channel_layer = channel_layer
        super().__init__(scope=scope)

    async def on_connect(
            self,
            websocket: WebSocket,
            user: DBUser = Depends(get_current_active_user),
            **kwargs
    ) -> None:
        print("Connected")
        await super().on_connect(websocket)

        self.game.join_game(user)
        self.game.update_game_status()
        self.channel = Channel(name=self.game_id, send=websocket.send_json)
        self.channel_layer.add(self.group_id, self.channel)

        if len(self.game.game.players) == 1:
            self.game.last_move.player_id = user.id

        await websocket.accept()

    async def on_receive(
            self,
            websocket: WebSocket,
            user: DBUser = Depends(get_current_active_user),
            move: Move = Depends(),
            **kwargs
    ):
        try:
            self.game.make_move(move)
        except (FieldNotEmptyError, WrongOuterFieldException) as e:
            json_response = {"status": "error", "detail": "Wrong field selected"}
            await websocket.send_json(json_response)
        finally:
            response_game_move = ResponseGameMove(
                status=self.game.get_game_status(),
                last_move=move,
                next_player=self.game.get_next_player(),
                outer_field=move.game.get_next_outer_field()
            )
            await self.channel_layer.group_send(self.group_id, response_game_move)

    async def on_disconnect(
            self,
            websocket: WebSocket,
            close_code: int,
            user: DBUser = Depends(get_current_active_user)
    ) -> None:
        self.game.left_game(user)
        self.game.update_game_status()

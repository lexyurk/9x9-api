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
from app.models.move import ResponseGameMove, MoveRequestSchema

router = APIRouter()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="authorizeUser(event)">
            <input type="text" id="username" placeholder="Username">
            <input type="text" id="password" placeholder="Password">
            <button>Authorize</button>
        </form>
        <form action="" onsubmit="testAuthorization(event)">
            <input type="submit" value="Test authorization">
        </form>
        <form action="" onsubmit="connectToGame(event)">
            <input type="text" id="gameId" placeholder="Connect to game">
            <button>Connect</button>
        </form>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = null;
            var authCookies = null;
            function authorizeUser(event) {
                event.preventDefault();
                var userName = document.getElementById("username").value;
                var password = document.getElementById("password").value;
                var http = new XMLHttpRequest();
                http.open("POST", "http://localhost/api/v1/login/access-token");
                http.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
                http.onload  = function() {
                    var jsonResponse = http.response;
                    var json = JSON.parse(jsonResponse);
                    var d = new Date();
                    d.setTime(d.getTime() + (24*60*60*1000));
                    var expires = "expires="+ d.toUTCString();
                    authCookies = "Authorization=Bearer " + json["access_token"] + ";" + expires + ";path=/";
                    console.log(authCookies);
                };
                http.send("grant_type=password&username="+userName+"&password="+password);
                }
            function connectToGame(event) {
                event.preventDefault();
                var game_id = document.getElementById("gameId");
                document.cookie = authCookies;
                ws = new WebSocket("ws://localhost/api/v1/games/" + game_id.value + "/ws");
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages');
                    var message = document.createElement('li');
                    var content = document.createTextNode(event.data);
                    message.appendChild(content);
                    messages.appendChild(message)
                };
            }
            function testAuthorization(event) {
                event.preventDefault();
                var http = new XMLHttpRequest();
                document.cookie = authCookies;
                http.open("POST", "http://localhost/api/v1/login/test-token");
                http.withCredentials = true;
                http.send(null);
            }
            function sendMessage(event) {
                var input = document.getElementById("messageText");
                ws.send(input.value);
                input.value = '';
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


@router.websocket_route("/{game_id:int}/ws")
class GameEndpoint(WebSocketEndpoint):
    encoding = "json"
    channel = None
    channel_layer = None
    game_id: int
    game: GameLobby = None
    group_id: int
    user: DBUser

    async def on_connect(
            self,
            websocket: WebSocket,
            user: DBUser = Depends(get_current_active_user),
            **kwargs
    ) -> None:
        await super().on_connect(websocket)

        game_id = websocket.path_params['game_id']
        self.game_id = game_id
        self.group_id = game_id
        self.channel_layer = channel_layer
        try:
            self.game = get_game(game_id)
        except GameNotFoundError:
            await websocket.close(code=1008)
            return
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
            request_move: MoveRequestSchema = Depends(),
            **kwargs
    ):

        user_move = crud.game.convert_to_move_model(request_move, user.id)
        if not self.game.get_next_player() == user.id:
            json_response = {"status": "error", "detail": "Wait for opponent move."}
            await websocket.send_json(json_response)
        try:
            self.game.make_move(user_move)
        except (FieldNotEmptyError, WrongOuterFieldException) as e:
            json_response = {"status": "error", "detail": "Wrong field selected."}
            await websocket.send_json(json_response)
        finally:
            game_update = ResponseGameMove(
                status=self.game.get_game_status(),
                last_move=crud.game.convert_to_response_model(user_move),
                next_player=self.game.get_next_player(),
                outer_field=self.game.get_next_outer_field()
            )
            await self.channel_layer.group_send(self.group_id, game_update)

    async def on_disconnect(
            self,
            websocket: WebSocket,
            close_code: int,
            user: DBUser = Depends(get_current_active_user)
    ):
        self.game.left_game(user)
        self.game.update_game_status()

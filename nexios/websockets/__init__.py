from .base import WebSocket, WebSocketDisconnect  # type:ignore
import typing

Scope = typing.MutableMapping[str, typing.Any]
Message = typing.MutableMapping[str, typing.Any]

Receive = typing.Callable[[], typing.Awaitable[Message]]
Send = typing.Callable[[Message], typing.Awaitable[None]]


async def get_websocket_session(
    scope: Scope, receive: Receive, send: Send
) -> WebSocket:
    ws = WebSocket(scope, receive, send)
    return ws

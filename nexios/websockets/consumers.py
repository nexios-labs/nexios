from .base import WebSocket
from nexios import status
import typing,json
from nexios.types import Message
class WebSocketEndpoint:
    encoding: str | None = None  # May be "text", "bytes", or "json".

    # def __init__(self, scope, receive, send) -> None:
    #     assert scope["type"] == "websocket"
    #     self.scope = scope
    #     self.receive = receive
    #     self.send = send

   

    async def __call__(self,ws :WebSocket) -> None:
        self.websocket = ws
        await self.on_connect(self.websocket)

        close_code = status.WS_1000_NORMAL_CLOSURE

        try:
            while True:
                message = await self.websocket.receive()
                if message["type"] == "websocket.receive":
                    data = await self.decode(self.websocket, message)
                    await self.on_receive(self.websocket, data)
                elif message["type"] == "websocket.disconnect":
                    close_code = int(message.get("code") or status.WS_1000_NORMAL_CLOSURE)
                    break
        except Exception as exc:
            close_code = status.WS_1011_INTERNAL_ERROR
            raise exc
        finally:
            await self.on_disconnect(self.websocket, close_code)

    async def decode(self, websocket: WebSocket, message :Message) -> typing.Any:
        if self.encoding == "text":
            if "text" not in message:
                await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
                raise RuntimeError("Expected text websocket messages, but got bytes")
            return message["text"]

        elif self.encoding == "bytes":
            if "bytes" not in message:
                await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
                raise RuntimeError("Expected bytes websocket messages, but got text")
            return message["bytes"]

        elif self.encoding == "json":
            if message.get("text") is not None:
                text = message["text"]
            else:
                text = message["bytes"].decode("utf-8")

            try:
                return json.loads(text)
            except json.decoder.JSONDecodeError:
                await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
                raise RuntimeError("Malformed JSON data received.")

        assert self.encoding is None, f"Unsupported 'encoding' attribute {self.encoding}"
        return message["text"] if message.get("text") else message["bytes"]

    async def on_connect(self, websocket: WebSocket) -> None:
        """Override to handle an incoming websocket connection"""
        await websocket.accept()

    async def on_receive(self, websocket: WebSocket, data: typing.Any) -> None:
        """Override to handle an incoming websocket message"""

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        """Override to handle a disconnecting websocket"""

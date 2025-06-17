from unittest.mock import AsyncMock

import pytest

from nexios.websockets import WebSocket, WebSocketConsumer


@pytest.fixture
def mock_websocket():
    scope = {
        "type": "websocket",
        "path": "/ws",
        "headers": [],
        "client": [],
        "server": [],
        "app": None,
        "extensions": {},
        "scope": {},
        "root_path": "",
        "url_scheme": "ws",
        "query_string": "",
        "headers_list": [],
        "cookies": {},
        "session": None,
        "user": None,
        "user_state": {},
        "user_state_policy": None,
    }
    receive = AsyncMock()
    send = AsyncMock()
    return WebSocket(scope, receive, send)


async def test_websocket_connection(mock_websocket):
    mock_websocket._receive.return_value = {"type": "websocket.connect"}
    await mock_websocket.accept()

    mock_websocket._send.assert_called_with(
        {"type": "websocket.accept", "subprotocol": None, "headers": []}
    )
    assert mock_websocket.application_state.value == 1  # CONNECTED


async def test_websocket_send_receive(mock_websocket):
    mock_websocket._receive.return_value = {"type": "websocket.connect"}
    await mock_websocket.accept()

    await mock_websocket.send_text("Hello")
    mock_websocket._send.assert_called_with({"type": "websocket.send", "text": "Hello"})

    mock_websocket._receive.return_value = {
        "type": "websocket.receive",
        "text": "World",
    }
    text = await mock_websocket.receive_text()
    assert text == "World"


async def test_websocket_json(mock_websocket):
    mock_websocket._receive.return_value = {"type": "websocket.connect"}
    await mock_websocket.accept()

    data = {"message": "Hello"}
    await mock_websocket.send_json(data)
    mock_websocket._send.assert_called_with(
        {"type": "websocket.send", "text": '{"message":"Hello"}'}
    )

    mock_websocket._receive.return_value = {
        "type": "websocket.receive",
        "text": '{"reply":"World"}',
    }
    received = await mock_websocket.receive_json()
    assert received == {"reply": "World"}


async def test_websocket_close(mock_websocket):
    # Test normal closure
    await mock_websocket.close(code=1000, reason="Normal closure")
    mock_websocket._send.assert_called_with(
        {"type": "websocket.close", "code": 1000, "reason": "Normal closure"}
    )


# Test WebSocket Consumer
class TestConsumer(WebSocketConsumer):
    encoding = "json"

    async def on_connect(self, websocket):
        await super().on_connect(websocket)
        await self.join_group("test_group")

    async def on_receive(self, websocket, data):
        await self.broadcast(data, group_name="test_group")

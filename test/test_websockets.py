import pytest
import json
import asyncio
from nexios import get_application, NexiosApp
from nexios.websockets.base import WebSocket, WebSocketState, WebSocketDisconnect
from nexios.http import Request, Response
from nexios.testing import Client, transport

# Create an application instance for testing
app = get_application()


# Define WebSocket endpoints for testing
@app.ws_route("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_text(f"Echo: {message}")
    except WebSocketDisconnect:
        pass


@app.ws_route("/ws/json")
async def websocket_json_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            await websocket.send_json({"echo": data})
    except WebSocketDisconnect:
        pass


@app.ws_route("/ws/bytes")
async def websocket_bytes_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            await websocket.send_bytes(data)
    except WebSocketDisconnect:
        pass


@app.ws_route("/ws/state_error")
async def websocket_state_error(websocket: WebSocket):
    # This endpoint deliberately doesn't call accept() to test error states
    pass


# Pytest fixture for WebSocket testing
@pytest.fixture
async def websocket_client():
    async with Client(app) as client:
        yield client


# Test the WebSocket connection lifecycle
async def test_websocket_connection_lifecycle(websocket_client):
    # Connect to the WebSocket endpoint

    async with websocket_client.websocket_connect("/ws") as websocket:
        # Test the WebSocket is connected
        assert websocket.client_state == WebSocketState.CONNECTED
        assert websocket.application_state == WebSocketState.CONNECTED
        assert websocket.is_connected() == True

        # Test basic messaging
        await websocket.send_text("Hello")
        response = await websocket.receive_text()
        assert response == "Echo: Hello"

    # After context exit, the WebSocket should be disconnected
    assert websocket.client_state == WebSocketState.DISCONNECTED


# Test explicit disconnection
async def test_websocket_explicit_disconnect(websocket_client):
    async with websocket_client.websocket_connect("/ws") as websocket:
        # Explicitly close the connection
        await websocket.close(code=1000, reason="Test disconnect")
        assert websocket.client_state == WebSocketState.DISCONNECTED
        assert websocket.is_connected() == False


# Test state transitions
async def test_websocket_state_transitions(websocket_client):
    # Connect to the WebSocket endpoint
    websocket = await websocket_client.websocket_connect("/ws")

    # Initial state should be CONNECTED after the fixture connects and the handler accepts
    assert websocket.client_state == WebSocketState.CONNECTED
    assert websocket.application_state == WebSocketState.CONNECTED

    # Send and receive a message in the CONNECTED state
    await websocket.send_text("State test")
    response = await websocket.receive_text()
    assert response == "Echo: State test"

    # Close the connection and check the DISCONNECTED state
    await websocket.close(code=1000)
    assert websocket.client_state == WebSocketState.DISCONNECTED
    assert websocket.application_state == WebSocketState.DISCONNECTED


# Test basic error handling
async def test_websocket_error_handling(websocket_client):
    # Test trying to send after disconnect
    websocket = await websocket_client.websocket_connect("/ws")
    await websocket.close()

    # Attempting to send after close should raise an error
    with pytest.raises(RuntimeError):
        await websocket.send_text("This should fail")

    # Attempting to receive after close should also raise an error
    with pytest.raises(RuntimeError):
        await websocket.receive_text()

    # Test connecting to a WebSocket endpoint that doesn't call accept()
    websocket = await websocket_client.websocket_connect("/ws/state_error")

    # Attempting to receive_text without the server accepting should raise
    with pytest.raises(RuntimeError):
        await websocket.receive_text()


# Test text message handling
async def test_websocket_text_messages(websocket_client):
    async with websocket_client.websocket_connect("/ws") as websocket:
        # Test simple text message
        await websocket.send_text("Hello")
        response = await websocket.receive_text()
        assert response == "Echo: Hello"

        # Test empty text message
        await websocket.send_text("")
        response = await websocket.receive_text()
        assert response == "Echo: "

        # Test unicode text
        await websocket.send_text("Hello 世界")
        response = await websocket.receive_text()
        assert response == "Echo: Hello 世界"

        # Test special characters
        await websocket.send_text("Special chars: !@#$%^&*()")
        response = await websocket.receive_text()
        assert response == "Echo: Special chars: !@#$%^&*()"


# Test binary message handling
async def test_websocket_binary_messages(websocket_client):
    async with websocket_client.websocket_connect("/ws/bytes") as websocket:
        # Test simple binary message
        test_bytes = b"Hello, binary world!"
        await websocket.send_bytes(test_bytes)
        response = await websocket.receive_bytes()
        assert response == test_bytes

        # Test empty binary message
        await websocket.send_bytes(b"")
        response = await websocket.receive_bytes()
        assert response == b""

        # Test large binary message
        large_bytes = b"x" * 1024
        await websocket.send_bytes(large_bytes)
        response = await websocket.receive_bytes()
        assert response == large_bytes

        # Test binary data with null bytes
        binary_with_nulls = b"Test\x00with\x00null\x00bytes"
        await websocket.send_bytes(binary_with_nulls)
        response = await websocket.receive_bytes()
        assert response == binary_with_nulls


# Test JSON message handling
async def test_websocket_json_messages(websocket_client):
    async with websocket_client.websocket_connect("/ws/json") as websocket:
        # Test simple JSON object
        test_data = {"message": "Hello", "number": 42}
        await websocket.send_json(test_data)
        response = await websocket.receive_json()
        assert response == {"echo": test_data}

        # Test JSON array
        test_array = [1, 2, 3, "test"]
        await websocket.send_json(test_array)
        response = await websocket.receive_json()
        assert response == {"echo": test_array}

        # Test nested JSON
        test_nested = {
            "user": {
                "name": "Test User",
                "settings": {"theme": "dark", "notifications": True},
            },
            "messages": [{"id": 1, "text": "Hello"}, {"id": 2, "text": "World"}],
        }
        await websocket.send_json(test_nested)
        response = await websocket.receive_json()
        assert response == {"echo": test_nested}

        # Test JSON with various data types
        test_types = {
            "string": "text",
            "number": 123,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "object": {"key": "value"},
        }
        await websocket.send_json(test_types)
        response = await websocket.receive_json()
        assert response == {"echo": test_types}


# Test sending JSON with different modes
async def test_websocket_json_modes(websocket_client):
    async with websocket_client.websocket_connect("/ws/json") as websocket:
        # Test JSON in text mode (default)
        data = {"test": "text mode"}
        await websocket.send_json(data, mode="text")
        response = await websocket.receive_json()
        assert response == {"echo": data}

        # Test JSON in binary mode
        data = {"test": "binary mode"}
        await websocket.send_json(data, mode="binary")
        response = await websocket.receive_json()
        assert response == {"echo": data}


# Test iterator methods for text
async def test_websocket_text_iterator(websocket_client):
    async with websocket_client.websocket_connect("/ws") as websocket:
        # Set up messages to send
        messages = ["Message 1", "Message 2", "Message 3"]
        received_messages = []

        # Start a background task to send messages
        async def send_messages():
            for msg in messages:
                await websocket.send_text(msg)
            # Close after sending all messages
            await websocket.close()

        # Use the iterator to receive messages
        send_task = asyncio.create_task(send_messages())
        async for message in websocket.iter_text():
            received_messages.append(message)
        await send_task

        # Verify all messages were received
        assert len(received_messages) == len(messages)
        for i, msg in enumerate(messages):
            assert received_messages[i] == f"Echo: {msg}"


# Test iterator methods for bytes
async def test_websocket_bytes_iterator(websocket_client):
    async with websocket_client.websocket_connect("/ws/bytes") as websocket:
        # Set up binary messages to send
        binary_messages = [b"Binary 1", b"Binary 2", b"Binary 3"]
        received_messages = []

        async def send_messages():
            for msg in binary_messages:
                await websocket.send_bytes(msg)
            await websocket.close()

        send_task = asyncio.create_task(send_messages())
        async for message in websocket.iter_bytes():
            received_messages.append(message)
        await send_task

        # Verify all binary messages were received correctly
        assert len(received_messages) == len(binary_messages)
        for i, msg in enumerate(binary_messages):
            assert received_messages[i] == msg


# Test iterator methods for JSON
async def test_websocket_json_iterator(websocket_client):
    async with websocket_client.websocket_connect("/ws/json") as websocket:
        # Set up JSON messages to send
        json_messages = [
            {"id": 1, "text": "First message"},
            {"id": 2, "text": "Second message"},
            {"id": 3, "text": "Third message"},
        ]
        received_messages = []

        async def send_messages():
            for msg in json_messages:
                await websocket.send_json(msg)
            await websocket.close()

        send_task = asyncio.create_task(send_messages())
        async for message in websocket.iter_json():
            received_messages.append(message)
        await send_task

        # Verify all JSON messages were received with correct echo format
        assert len(received_messages) == len(json_messages)
        for i, msg in enumerate(json_messages):
            assert received_messages[i] == {"echo": msg}


# Test error handling for message formats
async def test_websocket_message_format_errors(websocket_client):
    # Test JSON receive error
    async with websocket_client.websocket_connect("/ws") as websocket:
        # Send invalid JSON format but try to receive as JSON
        await websocket.send_text("This is not valid JSON")

        # This should raise a JSONDecodeError
        with pytest.raises(
            Exception
        ):  # In actual implementation, this might be more specific
            await websocket.receive_json()

    # Test using wrong receive method
    async with websocket_client.websocket_connect("/ws") as websocket:
        # Send text but try to receive as bytes
        await websocket.send_text("Text message")

        # This should raise an error
        with pytest.raises(
            Exception
        ):  # In actual implementation, this might be more specific
            await websocket.receive_bytes()


# Test WebSocket URL scheme handling
@pytest.mark.asyncio
async def test_websocket_url_schemes(websocket_client):
    """Test WebSocket URL scheme handling."""

    # Test cases for different URL formats
    test_cases = [
        ("/ws", True),  # Relative URL
        ("ws://testserver/ws", True),  # Explicit ws:// URL
        ("http://testserver/ws", True),  # http:// URL (should convert to ws://)
        ("https://testserver/ws", True),  # https:// URL (should convert to wss://)
        ("wss://testserver/ws", True),  # Explicit wss:// URL
        ("/invalid", False),  # Invalid endpoint
    ]

    for url, should_succeed in test_cases:
        if should_succeed:
            async with websocket_client.websocket_connect(url) as ws:
                assert ws.is_connected()
                assert ws.client_state == WebSocketState.CONNECTED
                await ws.send_text("test")
                response = await ws.receive_text()
                assert response == "Echo: test"
        else:
            with pytest.raises(RuntimeError):
                async with websocket_client.websocket_connect(url):
                    pass


@pytest.mark.asyncio
async def test_websocket_handshake_headers(websocket_client):
    """Test WebSocket handshake headers format."""

    async with websocket_client.websocket_connect("/ws") as ws:
        # Verify the connection is established
        assert ws.is_connected()

        # Verify WebSocket headers were sent correctly
        request_headers = dict(ws.connection.scope["headers"])
        assert b"upgrade" in request_headers
        assert request_headers[b"upgrade"] == b"websocket"
        assert b"connection" in request_headers
        assert request_headers[b"connection"] == b"upgrade"
        assert b"sec-websocket-version" in request_headers
        assert request_headers[b"sec-websocket-version"] == b"13"

        # Verify WebSocket key is valid base64
        ws_key = request_headers[b"sec-websocket-key"].decode()
        try:
            import base64

            decoded = base64.b64decode(ws_key)
            assert len(decoded) == 16  # Should be 16 bytes of random data
        except Exception:
            pytest.fail("Invalid WebSocket key format")


@pytest.mark.asyncio
async def test_websocket_protocol_negotiation(websocket_client):
    """Test WebSocket subprotocol negotiation."""

    subprotocols = ["chat", "superchat"]
    async with websocket_client.websocket_connect(
        "/ws", subprotocols=subprotocols
    ) as ws:
        assert ws.is_connected()

        # Verify subprotocols were sent in headers
        headers = dict(ws.connection.scope["headers"])
        assert b"sec-websocket-protocol" in headers
        protocols = headers[b"sec-websocket-protocol"].decode()
        assert "chat" in protocols
        assert "superchat" in protocols


@pytest.mark.asyncio
async def test_enhanced_websocket_connection_lifecycle(websocket_client):
    """Test complete WebSocket connection lifecycle with improved handling."""

    ws = await websocket_client.websocket_connect("/ws")
    try:
        # Test initial connection
        assert ws.is_connected()
        assert ws.client_state == WebSocketState.CONNECTED

        # Test basic communication
        await ws.send_text("Hello")
        response = await ws.receive_text()
        assert response == "Echo: Hello"

        # Test graceful closure
        await ws.close(1000, "Normal closure")
        assert not ws.is_connected()
        assert ws.client_state == WebSocketState.DISCONNECTED

        # Verify we can't send after close
        with pytest.raises(RuntimeError):
            await ws.send_text("This should fail")
    finally:
        if ws.is_connected():
            await ws.close()


@pytest.mark.asyncio
async def test_websocket_connection_error_handling(websocket_client):
    """Test WebSocket connection error handling."""

    # Test connection to non-existent endpoint
    with pytest.raises(RuntimeError) as exc_info:
        async with websocket_client.websocket_connect("/nonexistent"):
            pass
    assert "WebSocket upgrade failed" in str(exc_info.value)

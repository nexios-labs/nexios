# 🚀 Day 13: WebSocket Basics

## Learning Objectives
- Understand WebSocket fundamentals in Nexios
- Learn basic WebSocket routing and handlers
- Master message handling and connection lifecycle
- Work with WebSocket channels

## WebSocket Setup

Basic WebSocket setup in Nexios:

```python
from nexios import NexiosApp
from nexios.websockets.base import WebSocket, WebSocketDisconnect

app = NexiosApp()

@app.ws_route("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    
    try:
        while True:
            data = await ws.receive_text()
            await ws.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
```

## WebSocket Routing

Nexios provides multiple ways to handle WebSocket routing:

```python
from nexios.routing import WSRouter, WebsocketRoutes

# Method 1: Direct route
@app.ws_route("/chat")
async def chat_handler(ws: WebSocket):
    await ws.accept()
    ...

# Method 2: WebsocketRoutes
chat_route = WebsocketRoutes("/chat", chat_handler)
app.add_ws_route(chat_route)

# Method 3: WSRouter for grouped routes
router = WSRouter(prefix="/ws")
router.add_ws_route("/chat", chat_handler)
router.add_ws_route("/notifications", notification_handler)
app.mount_ws_router(router)
```

## Message Types and Handling

Nexios supports different message formats:

```python
from nexios.websockets.base import WebSocket

@app.ws_route("/chat")
async def chat_handler(ws: WebSocket):
    await ws.accept()
    
    try:
        while True:
            # Text messages
            text = await ws.receive_text()
            await ws.send_text("Echo: " + text)
            
            # JSON messages
            data = await ws.receive_json()
            await ws.send_json({"status": "received", "data": data})
            
            # Binary messages
            binary = await ws.receive_bytes()
            await ws.send_bytes(binary)
    except WebSocketDisconnect:
        print("Connection closed")
```

## Channel System

Nexios provides a powerful Channel system for WebSocket management:

```python
from nexios.websockets.channels import Channel, PayloadTypeEnum

@app.ws_route("/chat/{room_id}")
async def chat_room(ws: WebSocket, room_id: str):
    # Create a channel with JSON payload and 30-minute expiration
    channel = Channel(
        websocket=ws,
        payload_type=PayloadTypeEnum.JSON.value,
        expires=1800  # 30 minutes
    )
    
    try:
        while True:
            data = await ws.receive_json()
            await channel._send({"message": data})
    except WebSocketDisconnect:
        print(f"Client disconnected from room {room_id}")
```

## Error Handling

Implementing robust error handling:

```python
from nexios.websockets.base import WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)

@app.ws_route("/chat")
async def chat_handler(ws: WebSocket):
    try:
        await ws.accept()
        while True:
            data = await ws.receive_json()
            await ws.send_json({"status": "ok", "data": data})
    except WebSocketDisconnect:
        logger.info("Client disconnected normally")
    except ValueError as e:
        logger.error(f"Invalid JSON received: {e}")
        await ws.send_json({"error": "Invalid JSON format"})
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await ws.close(code=1011)  # Internal error
```

## 📝 Practice Exercise

1. Create a basic echo WebSocket server:
   - Accept text and JSON messages
   - Implement proper error handling
   - Add connection logging

2. Build a simple notification system:
   - Connect multiple clients
   - Broadcast messages to all clients
   - Handle client disconnections

3. Implement a basic chat room:
   - Use channels for message handling
   - Add room-based message broadcasting
   - Implement user presence tracking

## 📚 Additional Resources
- [WebSocket Protocol](https://tools.ietf.org/html/rfc6455)
- [Nexios WebSocket Guide](../../guide/websockets/index.md)
- [Channel Documentation](../../guide/websockets/channels.md)
- [Error Handling Guide](../../guide/error-handling.md)

## 🎯 Next Steps
Tomorrow in [Day 14: Real-Time Chat App](../day14/index.md), we'll explore:
- ChannelBox for group communication
- Real-time events and broadcasting
- Message history and persistence
- Advanced WebSocket features
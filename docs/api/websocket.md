# WebSocket API Reference

The WebSocket API provides real-time bidirectional communication between clients and servers.

## Basic WebSocket Setup

```python
from nexios import WSRouter

ws_router = WSRouter()

# Basic WebSocket route
@ws_router.ws("/ws")
async def websocket_endpoint(ws):
    await ws.accept()
    await ws.send_text("Connected!")
    
    while True:
        data = await ws.receive_text()
        await ws.send_text(f"Echo: {data}")
```

## WebSocket Connection

```python
# Accept connection
await ws.accept()

# Close connection
await ws.close(code=1000, reason="Normal closure")

# Check connection state
if ws.state == WebSocketState.CONNECTED:
    # Connection is active
    pass
```

## Sending Messages

```python
# Send text message
await ws.send_text("Hello, World!")

# Send binary message
await ws.send_bytes(b"Hello, World!")

# Send JSON message
await ws.send_json({"message": "Hello", "type": "greeting"})

# Send ping
await ws.send_ping()

# Send pong
await ws.send_pong()
```

## Receiving Messages

```python
# Receive text message
text = await ws.receive_text()

# Receive binary message
binary = await ws.receive_bytes()

# Receive JSON message
data = await ws.receive_json()

# Receive ping
ping = await ws.receive_ping()

# Receive pong
pong = await ws.receive_pong()
```

## WebSocket Events

```python
# Connection events
@ws_router.on("connect")
async def on_connect(ws):
    print(f"Client connected: {ws.client}")

@ws_router.on("disconnect")
async def on_disconnect(ws):
    print(f"Client disconnected: {ws.client}")

# Message events
@ws_router.on("message")
async def on_message(ws, message):
    print(f"Received message: {message}")
```

## WebSocket Middleware

```python
# WebSocket middleware
@ws_router.middleware
async def auth_middleware(ws, next):
    if not ws.headers.get("Authorization"):
        await ws.close(code=1008, reason="Authentication required")
        return
    return await next(ws)

# Route-specific middleware
@ws_router.ws("/chat", middleware=[auth_middleware])
async def chat(ws):
    await ws.accept()
    # Chat logic...
```

## WebSocket Groups

```python
# Create WebSocket group
chat_group = WSRouter(prefix="/chat")

# Add routes to group
@chat_group.ws("/general")
async def general_chat(ws):
    await ws.accept()
    # General chat logic...

@chat_group.ws("/private")
async def private_chat(ws):
    await ws.accept()
    # Private chat logic...

# Mount group to main app
app.mount_ws_router(chat_group)
```

## WebSocket Broadcasting

```python
# Broadcast to all connected clients
await ws_router.broadcast("Hello, everyone!")

# Broadcast to specific group
await chat_group.broadcast("Hello, chat!")

# Broadcast to specific clients
await ws_router.broadcast_to(["client1", "client2"], "Hello, specific clients!")
```

## WebSocket State Management

```python
# Store client state
ws.state["user_id"] = 42
ws.state["room"] = "general"

# Access client state
user_id = ws.state.get("user_id")
room = ws.state.get("room")
```

## WebSocket Error Handling

```python
# Handle WebSocket errors
@ws_router.exception_handler(WebSocketException)
async def handle_ws_error(ws, exc):
    await ws.close(code=1011, reason=str(exc))

# Custom error handling
@ws_router.ws("/chat")
async def chat(ws):
    try:
        await ws.accept()
        # Chat logic...
    except Exception as e:
        await ws.close(code=1011, reason=str(e))
```

## Advanced Features

### WebSocket Authentication

```python
# WebSocket authentication
@ws_router.ws("/secure")
async def secure_endpoint(ws):
    token = ws.headers.get("Authorization")
    if not await validate_token(token):
        await ws.close(code=1008, reason="Invalid token")
        return
    
    await ws.accept()
    # Secure WebSocket logic...
```

### WebSocket Rate Limiting

```python
# WebSocket rate limiting
@ws_router.middleware
async def rate_limit(ws, next):
    if not await check_rate_limit(ws.client):
        await ws.close(code=1008, reason="Rate limit exceeded")
        return
    return await next(ws)
```

### WebSocket Compression

```python
# Enable WebSocket compression
@ws_router.ws("/compressed")
async def compressed_endpoint(ws):
    await ws.accept()
    ws.enable_compression()
    # Compressed WebSocket logic...
```

## Key Notes

1. **Connection Management**: Always handle connection lifecycle
2. **Error Handling**: Implement proper error handling
3. **Security**: Use authentication and encryption
4. **State Management**: Manage client state appropriately
5. **Broadcasting**: Use broadcasting for group communication
6. **Rate Limiting**: Implement rate limiting for stability
7. **Compression**: Use compression for large messages
8. **Events**: Handle WebSocket events properly
9. **Middleware**: Use middleware for cross-cutting concerns
10. **Testing**: Write tests for WebSocket endpoints 

## Basic WebSocket Setup

### 1. Creating a WebSocket Endpoint

```python
from nexios import get_application, WebSocket
from nexios.routing import WSRouter

app = get_application()
ws_router = WSRouter()
app.mount_ws_router(ws_router)

@ws_router.ws_route("/ws")
async def basic_websocket(ws: WebSocket):
    await ws.accept()  # Must accept connection first
    
    try:
        while True:
            # Receiving messages
            data = await ws.receive_text()
            print(f"Received: {data}")
            
            # Sending messages
            await ws.send_text(f"You said: {data}")
    except Exception as e:
        print(f"Connection closed: {e}")
```

### 2. Handling Different Message Types

Nexios supports three main message formats:

#### Text Messages
```python
text_data = await ws.receive_text()
await ws.send_text("Response message")
```

#### Binary Messages
```python
binary_data = await ws.receive_bytes()
await ws.send_bytes(b"Response bytes")
```

#### JSON Messages
```python
json_data = await ws.receive_json()
await ws.send_json({"response": "data", "status": "success"})
```

### 3. Connection Lifecycle

```python
@ws_router.ws_route("/chat")
async def chat_websocket(ws: WebSocket):
    # 1. Accept connection
    await ws.accept()
    
    try:
        while True:
            # 2. Receive messages
            data = await ws.receive_json()
            
            # 3. Process message
            response = process_message(data)
            
            # 4. Send response
            await ws.send_json(response)
            
    except WebSocketDisconnect:
        # 5. Handle disconnect
        print("Client disconnected")
    finally:
        # 6. Clean up
        await ws.close()
```

## Intermediate Features

### Accessing Connection Details

```python
@ws_router.ws_route("/info")
async def info_websocket(ws: WebSocket):
    await ws.accept()
    
    # Client information
    client_ip = ws.client.host
    client_port = ws.client.port
    
    # Headers
    headers = {k.decode(): v.decode() for k, v in ws.scope["headers"]}
    
    # Query parameters
    query_params = ws.scope["query_string"].decode()
    
    # Path parameters (for routes like "/ws/{room_id}")
    room_id = ws.scope["path_params"].get("room_id")
    
    await ws.send_json({
        "ip": client_ip,
        "headers": headers,
        "query": query_params,
        "room_id": room_id
    })
```

### Error Handling

```python
from nexios.websockets import WebSocketDisconnect

@ws_router.ws_route("/safe")
async def safe_websocket(ws: WebSocket):
    await ws.accept()
    
    try:
        while True:
            try:
                data = await ws.receive_json()
                await ws.send_json({"status": "success", "data": data})
            except json.JSONDecodeError:
                await ws.send_json({"status": "error", "message": "Invalid JSON"})
            except ValueError as ve:
                await ws.send_json({"status": "error", "message": str(ve)})
                
    except WebSocketDisconnect as e:
        print(f"Client disconnected with code {e.code}: {e.reason}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        await ws.close(code=1011)  # 1011 = Internal Error
```

## Advanced Room Management

### Understanding the Channel System

Nexios provides built-in room management through:
- `Channel`: Represents a single WebSocket connection
- `ChannelBox`: Manages groups of channels (rooms)

### Basic Room Operations

#### Function-Based Approach

```python
from nexios.websockets.channels import Channel, ChannelBox, PayloadTypeEnum

@ws_router.ws_route("/room/{room_name}")
async def room_handler(ws: WebSocket, room_name: str):
    await ws.accept()
    
    # Create channel
    channel = Channel(
        websocket=ws,
        payload_type=PayloadTypeEnum.JSON.value,
        expires=3600  # 1 hour expiration
    )
    
    # Join room
    await ChannelBox.add_channel_to_group(channel, room_name)
    
    try:
        while True:
            data = await ws.receive_json()
            
            # Broadcast to room
            await ChannelBox.group_send(
                group_name=room_name,
                payload={
                    "user": data.get("user"),
                    "message": data["message"],
                    "timestamp": time.time()
                },
                save_history=True  # Store in message history
            )
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        await ChannelBox.remove_channel_from_group(channel, room_name)
        await ws.close()
```

#### Class-Based Approach (Recommended)

```python
from nexios.websockets.consumers import WebSocketEndpoint

class ChatEndpoint(WebSocketEndpoint):
    encoding = "json"  # Auto JSON serialization
    
    async def on_connect(self, ws: WebSocket):
        await ws.accept()
        room_name = ws.scope["path_params"]["room_name"]
        await self.join_group(room_name)
        await self.broadcast(
            {"system": f"New user joined {room_name}"},
            room_name
        )
    
    async def on_receive(self, ws: WebSocket, data: typing.Any):
        room_name = ws.scope["path_params"]["room_name"]
        await self.broadcast(
            {
                "user": data["user"],
                "message": data["message"],
                "timestamp": time.time()
            },
            room_name,
            save_history=True
        )
    
    async def on_disconnect(self, ws: WebSocket, close_code: int):
        room_name = ws.scope["path_params"]["room_name"]
        await self.broadcast(
            {"system": f"User left {room_name}"},
            room_name
        )
        await self.leave_group(room_name)
```

### Room Management Features

1. **Listing Rooms and Channels**
```python
# Get all active rooms
rooms = await ChannelBox.show_groups()

# Get channels in a specific room
channels = await ChannelBox.show_groups().get("room_name", {})
```

2. **Message History**
```python
# Save message (shown in broadcast examples above)
# Retrieve history
history = await ChannelBox.show_history("room_name")

# Clear history
await ChannelBox.flush_history()
```

3. **Targeted Messaging**
```python
# Send to specific channel
channel_id = "uuid-of-channel"
await ChannelBox.send_to(channel_id, {"private": "message"})
```

4. **Connection Management**
```python
# Close all connections
await ChannelBox.close_all_connections()

# Clean up expired channels
await ChannelBox._clean_expired()
```

### Complete Chat Room Example

```python
from nexios.websockets.consumers import WebSocketEndpoint
import time
import typing

class ChatRoom(WebSocketEndpoint):
    encoding = "json"
    
    async def on_connect(self, ws: WebSocket):
        await ws.accept()
        self.room = ws.scope["path_params"]["room_id"]
        self.user = ws.scope["query_params"].get("username", "anonymous")
        
        await self.join_group(self.room)
        await self.broadcast(
            {
                "type": "system",
                "message": f"{self.user} joined the chat",
                "timestamp": time.time(),
                "users": await self.get_user_count()
            },
            self.room,
            save_history=True
        )
    
    async def on_receive(self, ws: WebSocket, data: typing.Any):
        if data.get("type") == "message":
            await self.broadcast(
                {
                    "type": "chat",
                    "user": self.user,
                    "message": data["content"],
                    "timestamp": time.time()
                },
                self.room,
                save_history=True
            )
    
    async def on_disconnect(self, ws: WebSocket, close_code: int):
        await self.broadcast(
            {
                "type": "system", 
                "message": f"{self.user} left the chat",
                "timestamp": time.time(),
                "users": await self.get_user_count() - 1
            },
            self.room,
            save_history=True
        )
        await self.leave_group(self.room)
    
    async def get_user_count(self):
        channels = await self.group(self.room)
        return len(channels)
```

## Best Practices

1. **Always handle disconnections** - Use try/finally blocks to clean up resources
2. **Validate incoming data** - Especially for JSON messages
3. **Use appropriate timeouts** - Set reasonable expires values for channels
4. **Limit message history size** - To prevent memory issues
5. **Implement authentication** - Especially for sensitive rooms
6. **Use connection state checks** - `ws.is_connected()` before sending
7. **Monitor room sizes** - Large rooms may need partitioning
8. **Implement rate limiting** - Prevent abuse of your WebSocket endpoints

This comprehensive guide covers everything from basic WebSocket operations to advanced room management in Nexios. The system provides all the tools needed to build robust real-time applications while handling the complexity of connection management behind the scenes.
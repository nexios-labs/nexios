---
icon: zap
---

# WebSockets

## Introduction to WebSockets in Nexios

WebSockets provide a persistent connection between a client and server, allowing for real-time, bidirectional communication. Nexios offers a robust WebSocket implementation that makes it easy to build real-time applications like chat systems, live dashboards, notifications, and collaborative tools.

The Nexios WebSocket system is built around these key components:

- **WebSocket**: The base connection between client and server
- **Channel**: A wrapper around a WebSocket connection with additional functionality
- **ChannelBox**: A manager for organizing channels into groups and handling messaging

## Basic WebSocket Setup

Setting up a WebSocket connection in Nexios is straightforward:

```python
from nexios import get_application
from nexios.websockets import WebSocket

app = get_application()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    
    try:
        while True:
            # Receive message from client
            data = await ws.receive()
            
            # Echo the message back
            if data.get("type") == "websocket.receive":
                if "text" in data:
                    await ws.send_text(f"You said: {data['text']}")
                elif "bytes" in data:
                    await ws.send_bytes(data["bytes"])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await ws.close()
```

## Channel Architecture

Nexios provides a `Channel` class that wraps WebSocket connections with additional functionality. Channels are the foundation of Nexios's WebSocket system, allowing for easier management, grouping, and message distribution.

### The Channel Class

A Channel represents a single WebSocket connection with metadata and helper methods:

```python
from nexios import get_application
from nexios.websockets import WebSocket
from nexios.websockets.channels import Channel, PayloadTypeEnum

app = get_application()

@app.websocket("/ws/channel")
async def channel_example(ws: WebSocket):
    await ws.accept()
    
    # Create a channel with 30 minute expiration and JSON payload support
    channel = Channel(
        websocket=ws,
        payload_type=PayloadTypeEnum.JSON.value,  # "json", "text", or "bytes"
        expires=1800  # TTL in seconds (30 minutes)
    )
    
    try:
        while True:
            data = await ws.receive()
            if data.get("type") == "websocket.receive":
                # Use channel's sending capabilities
                if "text" in data:
                    await channel._send({"message": data["text"], "timestamp": time.time()})
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await ws.close()
```

### Channel Properties

- **websocket**: The underlying WebSocket connection
- **expires**: Time-to-live in seconds (None for no expiration)
- **payload_type**: Format of messages ("json", "text", or "bytes")
- **uuid**: Unique identifier for the channel
- **created**: Timestamp when the channel was created

## ChannelBox: Managing Channel Groups

The `ChannelBox` is a powerful class that manages collections of channels. It allows you to:

1. Organize channels into named groups
2. Send messages to all channels in a group
3. Store message history
4. Clean up expired channels automatically

### Basic ChannelBox Usage

```python
from nexios import get_application
from nexios.websockets import WebSocket
from nexios.websockets.channels import Channel, ChannelBox, PayloadTypeEnum

app = get_application()

@app.websocket("/ws/chat/{room_id}")
async def chat_endpoint(ws: WebSocket):
    await ws.accept()
    room_id = ws.path_params["room_id"]
    
    # Create a channel for this connection
    channel = Channel(
        websocket=ws,
        payload_type=PayloadTypeEnum.JSON.value,
        expires=3600  # 1 hour TTL
    )
    
    # Add channel to the appropriate group
    await ChannelBox.add_channel_to_group(channel, group_name=f"chat_{room_id}")
    
    try:
        # Welcome message
        await channel._send({"type": "system", "message": f"Welcome to room {room_id}"})
        
        # Send last 10 messages from history (if any)
        history = await ChannelBox.show_history(group_name=f"chat_{room_id}")
        if history:
            for message in history[-10:]:
                await channel._send(message.payload)
        
        while True:
            data = await ws.receive()
            if data.get("type") == "websocket.receive" and "text" in data:
                # Broadcast message to the entire room
                message = {
                    "type": "chat",
                    "text": data["text"],
                    "sender_id": str(channel.uuid),
                    "timestamp": time.time()
                }
                
                # Send to all clients in the room and save in history
                await ChannelBox.group_send(
                    group_name=f"chat_{room_id}",
                    payload=message,
                    save_history=True
                )
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Remove channel from group when connection closes
        await ChannelBox.remove_channel_from_group(channel, group_name=f"chat_{room_id}")
        await ws.close()
```

## Payload Types

Nexios supports three different payload types for WebSocket communication:

1. **JSON** (`PayloadTypeEnum.JSON.value` or `"json"`): For structured data
2. **Text** (`PayloadTypeEnum.TEXT.value` or `"text"`): For plain text messages
3. **Bytes** (`PayloadTypeEnum.BYTES.value` or `"bytes"`): For binary data like images or files

The payload type determines how messages are sent and received:

```python
# For JSON payloads
await channel._send({"message": "Hello", "data": [1, 2, 3]})

# For text payloads
await channel._send("Hello World")

# For binary payloads
await channel._send(b"\x00\x01\x02\x03")
```

## Channel Groups and Message Broadcasting

One of the most powerful features of the Nexios WebSocket system is the ability to group channels and broadcast messages to all members of a group.

### Adding a Channel to a Group

```python
from nexios.websockets.channels import Channel, ChannelBox, ChannelAddStatusEnum

# Create a channel
channel = Channel(websocket=ws, payload_type="json", expires=1800)

# Add to group
status = await ChannelBox.add_channel_to_group(channel, group_name="notifications")

if status == ChannelAddStatusEnum.CHANNEL_ADDED:
    print("Channel added to a new group")
elif status == ChannelAddStatusEnum.CHANNEL_EXIST:
    print("Channel added to an existing group")
```

### Removing a Channel from a Group

```python
from nexios.websockets.channels import ChannelRemoveStatusEnum

status = await ChannelBox.remove_channel_from_group(channel, group_name="notifications")

if status == ChannelRemoveStatusEnum.CHANNEL_REMOVED:
    print("Channel removed from group")
elif status == ChannelRemoveStatusEnum.GROUP_REMOVED:
    print("Channel removed and group deleted (was last channel)")
```

### Broadcasting Messages to a Group

```python
from nexios.websockets.channels import ChannelBox, GroupSendStatusEnum

status = await ChannelBox.group_send(
    group_name="notifications",
    payload={"type": "alert", "message": "System maintenance in 5 minutes"},
    save_history=True  # Save in group history
)

if status == GroupSendStatusEnum.GROUP_SEND:
    print("Message sent to group")
elif status == GroupSendStatusEnum.NO_SUCH_GROUP:
    print("Group does not exist")
```

## Message History

Nexios can maintain a history of messages sent to channel groups. This is useful for providing message history to new connections or implementing message replay functionality.

### Accessing Message History

```python
# Get history for a specific group
group_history = await ChannelBox.show_history(group_name="chat_room1")
for message in group_history:
    print(f"Message: {message.payload}")

# Get history for all groups
all_history = await ChannelBox.show_history()
```

### Controlling History Size

The history size is controlled by the `CHANNEL_BOX_HISTORY_SIZE` environment variable (default: 1MB). When the history exceeds this size, it is automatically cleared.

```python
# Set history size to 5MB
import os
os.environ["CHANNEL_BOX_HISTORY_SIZE"] = str(5 * 1024 * 1024)
```

### Clearing History

```python
# Clear history for all groups
await ChannelBox.flush_history()
```

## Channel Expiration and Cleanup

Channels can be configured with a time-to-live (TTL) in seconds. When a channel expires, it is automatically removed from all groups during cleanup operations.

```python
# Create a channel that expires after 5 minutes
channel = Channel(websocket=ws, payload_type="json", expires=300)
```

Expiration checks are performed automatically when removing channels from groups. You can verify if a channel has expired:

```python
is_expired = await channel._is_expired()
if is_expired:
    print("Channel has expired")
```

## Advanced Usage: Building a Chat Application

Here's a complete example of a chat application using Nexios WebSockets:

```python
from nexios import get_application
from nexios.websockets import WebSocket
from nexios.websockets.channels import Channel, ChannelBox, PayloadTypeEnum
import json
import time
import asyncio

app = get_application()

# Keep track of user information
users = {}

@app.on_startup
async def setup():
    # Schedule periodic cleanup of expired channels
    asyncio.create_task(periodic_cleanup())

async def periodic_cleanup():
    while True:
        await ChannelBox._clean_expired()
        await asyncio.sleep(60)  # Run every minute

@app.websocket("/ws/chat/{room_id}")
async def chat_room(ws: WebSocket):
    await ws.accept()
    
    # Get parameters
    room_id = ws.path_params["room_id"]
    username = ws.query_params.get("username", f"Anonymous-{time.time()}")
    
    # Create the channel
    channel = Channel(
        websocket=ws,
        payload_type=PayloadTypeEnum.JSON.value,
        expires=3600  # 1 hour TTL
    )
    
    # Store user information
    user_id = str(channel.uuid)
    users[user_id] = {
        "username": username,
        "room": room_id,
        "joined_at": time.time()
    }
    
    # Add to room group
    group_name = f"chat_room_{room_id}"
    await ChannelBox.add_channel_to_group(channel, group_name=group_name)
    
    try:
        # Announce the new user to everyone in the room
        join_message = {
            "type": "system",
            "action": "join",
            "username": username,
            "user_id": user_id,
            "timestamp": time.time(),
            "message": f"{username} has joined the room"
        }
        
        await ChannelBox.group_send(
            group_name=group_name,
            payload=join_message,
            save_history=True
        )
        
        # Send history to the new user
        history = await ChannelBox.show_history(group_name=group_name)
        if history:
            # Send the last 50 messages
            for message in history[-50:]:
                await channel._send(message.payload)
        
        # Handle messages
        while True:
            data = await ws.receive()
            if data.get("type") == "websocket.receive" and "text" in data:
                try:
                    # Parse the text as JSON
                    text_data = json.loads(data["text"])
                    message_type = text_data.get("type", "message")
                    
                    if message_type == "message":
                        # Regular chat message
                        chat_message = {
                            "type": "message",
                            "content": text_data.get("content", ""),
                            "username": username,
                            "user_id": user_id,
                            "room_id": room_id,
                            "timestamp": time.time()
                        }
                        
                        await ChannelBox.group_send(
                            group_name=group_name,
                            payload=chat_message,
                            save_history=True
                        )
                    
                    elif message_type == "typing":
                        # Typing indicator (no need to save in history)
                        typing_message = {
                            "type": "typing",
                            "username": username,
                            "user_id": user_id,
                            "is_typing": text_data.get("is_typing", True)
                        }
                        
                        await ChannelBox.group_send(
                            group_name=group_name,
                            payload=typing_message,
                            save_history=False
                        )
                        
                except json.JSONDecodeError:
                    # If not valid JSON, send as plain text message
                    text_message = {
                        "type": "message",
                        "content": data["text"],
                        "username": username,
                        "user_id": user_id,
                        "room_id": room_id,
                        "timestamp": time.time()
                    }
                    
                    await ChannelBox.group_send(
                        group_name=group_name,
                        payload=text_message,
                        save_history=True
                    )
    
    except Exception as e:
        print(f"Error in chat websocket: {e}")
    
    finally:
        # User is leaving - announce to room
        leave_message = {
            "type": "system",
            "action": "leave",
            "username": username,
            "user_id": user_id,
            "timestamp": time.time(),
            "message": f"{username} has left the room"
        }
        
        await ChannelBox.group_send(
            group_name=group_name,
            payload=leave_message,
            save_history=True
        )
        
        # Remove from room group
        await ChannelBox.remove_channel_from_group(channel, group_name=group_name)
        
        # Clean up user info
        if user_id in users:
            del users[user_id]
        
        await ws.close()

# Additional endpoints for room management

@app.get("/api/chat/rooms")
async def list_rooms(req, res):
    """List all active chat rooms"""
    # Get unique room names from the users dict
    rooms = set(user["room"] for user in users.values())
    room_data = []
    
    for room in rooms:
        group_name = f"chat_room_{room

---
icon: wifi-fair
---

# Websockets

### Basic WebSocket Setup

#### 1. Creating a WebSocket Endpoint

```python
from nexios import get_application
from nexios.routing import WSRouter
from nexios.websockets.base import WebSocket
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

#### 2. Handling Different Message Types

Nexios supports three main message formats:

**Text Messages**

```python
text_data = await ws.receive_text()
await ws.send_text("Response message")
```

**Binary Messages**

```python
binary_data = await ws.receive_bytes()
await ws.send_bytes(b"Response bytes")
```

**JSON Messages**

```python
json_data = await ws.receive_json()
await ws.send_json({"response": "data", "status": "success"})
```

#### 3. Connection Lifecycle

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

### Intermediate Features

#### Accessing Connection Details

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

#### Error Handling

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

### Advanced Room Management

#### Understanding the Channel System

Nexios provides built-in room management through:

* `Channel`: Represents a single WebSocket connection
* `ChannelBox`: Manages groups of channels (rooms)

#### Basic Room Operations

**Function-Based Approach**

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

**Class-Based Approach (Recommended)**

```python
from nexios.websockets.consumers import WebSocketConsumer

class ChatEndpoint(WebSocketConsumer):
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

#### Room Management Features

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

#### Complete Chat Room Example

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

### Best Practices

1. **Always handle disconnections** - Use try/finally blocks to clean up resources
2. **Validate incoming data** - Especially for JSON messages
3. **Use appropriate timeouts** - Set reasonable expires values for channels
4. **Limit message history size** - To prevent memory issues
5. **Implement authentication** - Especially for sensitive rooms
6. **Use connection state checks** - `ws.is_connected()` before sending
7. **Monitor room sizes** - Large rooms may need partitioning
8. **Implement rate limiting** - Prevent abuse of your WebSocket endpoints

This comprehensive guide covers everything from basic WebSocket operations to advanced room management in Nexios. The system provides all the tools needed to build robust real-time applications while handling the complexity of connection management behind the scenes.

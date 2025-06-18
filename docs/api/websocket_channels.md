# WebSocket Channels API Reference

The WebSocket Channels API in Nexios provides a powerful system for managing real-time communication between clients and the server. It allows you to create channels, manage subscriptions, and broadcast messages to connected clients.

## Channel Class

The `Channel` class is the core component for managing WebSocket channels.

```python
from nexios.websockets import Channel, WebSocket

class MyChannel(Channel):
    def __init__(
        self,
        websocket: WebSocket,
        payload_type: str = "json",
        expires: Optional[int] = None
    ):
        super().__init__(websocket, payload_type, expires)
```

### Initialization

```python
channel = Channel(
    websocket=websocket,
    payload_type="json",  # or "text" or "bytes"
    expires=3600  # channel TTL in seconds
)
```

### Properties

- `websocket`: The underlying WebSocket connection
- `expires`: Channel TTL in seconds
- `payload_type`: Type of payload ("json", "text", or "bytes")
- `uuid`: Unique channel identifier
- `created`: Channel creation timestamp

## Channel Methods

### Sending Messages

#### `send(payload: Any) -> None`

Send a message to the channel.

```python
# Send JSON
await channel.send({"message": "Hello, World!"})

# Send text
await channel.send("Hello, World!")

# Send bytes
await channel.send(b"Hello, World!")
```

#### `send_json(data: Dict[str, Any]) -> None`

Send JSON data to the channel.

```python
await channel.send_json({
    "type": "message",
    "content": "Hello, World!",
    "timestamp": time.time()
})
```

#### `send_text(text: str) -> None`

Send text data to the channel.

```python
await channel.send_text("Hello, World!")
```

#### `send_bytes(data: bytes) -> None`

Send binary data to the channel.

```python
await channel.send_bytes(b"Hello, World!")
```

### Receiving Messages

#### `receive() -> Any`

Receive a message from the channel.

```python
message = await channel.receive()
```

#### `receive_json() -> Dict[str, Any]`

Receive JSON data from the channel.

```python
data = await channel.receive_json()
```

#### `receive_text() -> str`

Receive text data from the channel.

```python
text = await channel.receive_text()
```

#### `receive_bytes() -> bytes`

Receive binary data from the channel.

```python
data = await channel.receive_bytes()
```

## Channel Groups

### Creating Groups

```python
from nexios.websockets import ChannelGroup

group = ChannelGroup("chat")
```

### Group Methods

#### `add(channel: Channel) -> None`

Add a channel to the group.

```python
await group.add(channel)
```

#### `remove(channel: Channel) -> None`

Remove a channel from the group.

```python
await group.remove(channel)
```

#### `send(payload: Any) -> None`

Send a message to all channels in the group.

```python
await group.send({"message": "Hello, everyone!"})
```

#### `send_json(data: Dict[str, Any]) -> None`

Send JSON data to all channels in the group.

```python
await group.send_json({
    "type": "broadcast",
    "content": "Hello, everyone!",
    "timestamp": time.time()
})
```

## Channel Management

### Channel Registry

```python
from nexios.websockets import ChannelRegistry

registry = ChannelRegistry()
```

#### `add(channel: Channel) -> None`

Register a channel.

```python
await registry.add(channel)
```

#### `remove(channel: Channel) -> None`

Unregister a channel.

```python
await registry.remove(channel)
```

#### `get(channel_id: str) -> Optional[Channel]`

Get a channel by ID.

```python
channel = await registry.get(channel_id)
```

#### `get_all() -> List[Channel]`

Get all registered channels.

```python
channels = await registry.get_all()
```

## Channel Middleware

### Authentication Middleware

```python
class AuthChannelMiddleware:
    async def __call__(self, websocket: WebSocket, next):
        # Authenticate the WebSocket connection
        if not await authenticate(websocket):
            await websocket.close(code=4001)
            return
            
        return await next(websocket)
```

### Rate Limiting Middleware

```python
class RateLimitChannelMiddleware:
    def __init__(self, rate_limit: int, time_window: int):
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.requests = {}
        
    async def __call__(self, websocket: WebSocket, next):
        client_id = websocket.client.host
        
        if not self._check_rate_limit(client_id):
            await websocket.close(code=4002)
            return
            
        return await next(websocket)
        
    def _check_rate_limit(self, client_id: str) -> bool:
        now = time.time()
        if client_id not in self.requests:
            self.requests[client_id] = []
            
        # Remove old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.time_window
        ]
        
        if len(self.requests[client_id]) >= self.rate_limit:
            return False
            
        self.requests[client_id].append(now)
        return True
```

## Channel Events

### Connection Events

```python
@channel.on_connect
async def handle_connect(channel: Channel):
    print(f"Channel {channel.uuid} connected")

@channel.on_disconnect
async def handle_disconnect(channel: Channel):
    print(f"Channel {channel.uuid} disconnected")
```

### Message Events

```python
@channel.on_message
async def handle_message(channel: Channel, message: Any):
    print(f"Received message from {channel.uuid}: {message}")
```

### Error Events

```python
@channel.on_error
async def handle_error(channel: Channel, error: Exception):
    print(f"Error in channel {channel.uuid}: {str(error)}")
```

## Best Practices

1. **Error Handling**: Always handle WebSocket errors gracefully.

```python
try:
    while True:
        message = await channel.receive()
        await process_message(message)
except WebSocketDisconnect:
    await handle_disconnect(channel)
except Exception as e:
    await handle_error(channel, e)
```

2. **Connection Management**: Implement proper connection lifecycle management.

```python
async def handle_websocket(websocket: WebSocket):
    channel = Channel(websocket)
    try:
        await channel.accept()
        await handle_connect(channel)
        
        while True:
            message = await channel.receive()
            await process_message(channel, message)
    except WebSocketDisconnect:
        await handle_disconnect(channel)
    finally:
        await cleanup(channel)
```

3. **Message Validation**: Validate incoming messages.

```python
from pydantic import BaseModel

class Message(BaseModel):
    type: str
    content: str
    timestamp: float

async def process_message(channel: Channel, message: Any):
    try:
        validated_message = Message(**message)
        await handle_validated_message(channel, validated_message)
    except ValidationError as e:
        await channel.send_json({
            "error": "Invalid message format",
            "details": str(e)
        })
```

4. **Rate Limiting**: Implement rate limiting for WebSocket connections.

```python
class RateLimitedChannel(Channel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_count = 0
        self.last_reset = time.time()
        
    async def receive(self) -> Any:
        now = time.time()
        if now - self.last_reset >= 60:
            self.message_count = 0
            self.last_reset = now
            
        if self.message_count >= 100:  # 100 messages per minute
            raise RateLimitExceeded()
            
        self.message_count += 1
        return await super().receive()
```

5. **Heartbeat**: Implement heartbeat mechanism to detect stale connections.

```python
class HeartbeatChannel(Channel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_heartbeat = time.time()
        
    async def send_heartbeat(self):
        await self.send_json({"type": "heartbeat"})
        self.last_heartbeat = time.time()
        
    async def check_heartbeat(self):
        if time.time() - self.last_heartbeat > 30:
            await self.close(code=4000)
```

6. **Message Queuing**: Implement message queuing for offline clients.

```python
class QueuedChannel(Channel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_queue = []
        
    async def send(self, message: Any):
        if not self.connected:
            self.message_queue.append(message)
        else:
            await super().send(message)
            
    async def process_queue(self):
        while self.message_queue and self.connected:
            message = self.message_queue.pop(0)
            await super().send(message)
```

7. **Security**: Implement proper security measures.

```python
class SecureChannel(Channel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.authenticated = False
        
    async def authenticate(self, token: str):
        if not await verify_token(token):
            raise AuthenticationError()
        self.authenticated = True
        
    async def send(self, message: Any):
        if not self.authenticated:
            raise AuthenticationError()
        await super().send(message)
``` 
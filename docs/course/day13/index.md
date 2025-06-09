# 🚀 Day 13: WebSocket Basics

## WebSocket Setup

Setting up WebSocket support:

```python
from nexios import NexiosApp
from nexios.websockets import WebSocket
from typing import Dict, Set
import json

app = NexiosApp()

# Store active connections
connections: Dict[str, Set[WebSocket]] = {
    "default": set()
}

@app.ws_route("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections["default"].add(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except:
        connections["default"].remove(websocket)
        await websocket.close()

# Room-based WebSocket
@app.ws_route("/ws/{room_id}")
async def room_websocket(websocket: WebSocket, room_id: str):
    if room_id not in connections:
        connections[room_id] = set()
    
    await websocket.accept()
    connections[room_id].add(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast to all in room
            for client in connections[room_id]:
                await client.send_text(data)
    except:
        connections[room_id].remove(websocket)
        if not connections[room_id]:
            del connections[room_id]
        await websocket.close()
```

## Connection Handling

Managing WebSocket connections:

```python
from nexios.websockets import WebSocketManager
from nexios.security import requires_auth
from datetime import datetime

class ConnectionManager(WebSocketManager):
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        self.user_rooms: Dict[str, Set[str]] = {}
    
    async def connect(
        self,
        websocket: WebSocket,
        room_id: str,
        user_id: str
    ):
        await websocket.accept()
        
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        
        self.active_connections[room_id][user_id] = websocket
        
        if user_id not in self.user_rooms:
            self.user_rooms[user_id] = set()
        
        self.user_rooms[user_id].add(room_id)
    
    async def disconnect(
        self,
        room_id: str,
        user_id: str
    ):
        if room_id in self.active_connections:
            if user_id in self.active_connections[room_id]:
                del self.active_connections[room_id][user_id]
            
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
        
        if user_id in self.user_rooms:
            self.user_rooms[user_id].remove(room_id)
            if not self.user_rooms[user_id]:
                del self.user_rooms[user_id]
    
    async def broadcast(
        self,
        room_id: str,
        message: str,
        exclude_user: str = None
    ):
        if room_id in self.active_connections:
            for user_id, websocket in self.active_connections[room_id].items():
                if user_id != exclude_user:
                    await websocket.send_text(message)
    
    async def send_personal_message(
        self,
        room_id: str,
        user_id: str,
        message: str
    ):
        if (room_id in self.active_connections and
            user_id in self.active_connections[room_id]):
            await self.active_connections[room_id][user_id].send_text(message)

# Initialize manager
manager = ConnectionManager()

@app.websocket("/ws/{room_id}")
@requires_auth
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str
):
    user_id = websocket.user.id
    await manager.connect(websocket, room_id, user_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Add timestamp and user info
            message = {
                "user_id": user_id,
                "username": websocket.user.username,
                "message": data["message"],
                "timestamp": datetime.now().isoformat()
            }
            
            # Broadcast to room
            await manager.broadcast(
                room_id,
                json.dumps(message),
                exclude_user=user_id
            )
    except:
        await manager.disconnect(room_id, user_id)
```

## Message Types

Handling different message types:

```python
from enum import Enum
from pydantic import BaseModel
from typing import Optional, Any

class MessageType(str, Enum):
    CHAT = "chat"
    JOIN = "join"
    LEAVE = "leave"
    SYSTEM = "system"
    ERROR = "error"

class WebSocketMessage(BaseModel):
    type: MessageType
    content: str
    user_id: Optional[str] = None
    room_id: Optional[str] = None
    data: Optional[dict] = None

@app.websocket("/ws/chat/{room_id}")
async def chat_websocket(
    websocket: WebSocket,
    room_id: str
):
    user_id = websocket.user.id
    await manager.connect(websocket, room_id, user_id)
    
    # Send join message
    join_message = WebSocketMessage(
        type=MessageType.JOIN,
        content=f"{websocket.user.username} joined the room",
        user_id=user_id,
        room_id=room_id
    )
    
    await manager.broadcast(
        room_id,
        join_message.json()
    )
    
    try:
        while True:
            data = await websocket.receive_json()
            message = WebSocketMessage(**data)
            
            if message.type == MessageType.CHAT:
                # Regular chat message
                await manager.broadcast(
                    room_id,
                    message.json(),
                    exclude_user=user_id
                )
            elif message.type == MessageType.SYSTEM:
                # System message (e.g., user typing)
                await manager.broadcast(
                    room_id,
                    message.json(),
                    exclude_user=user_id
                )
    except:
        # Send leave message
        leave_message = WebSocketMessage(
            type=MessageType.LEAVE,
            content=f"{websocket.user.username} left the room",
            user_id=user_id,
            room_id=room_id
        )
        
        await manager.broadcast(
            room_id,
            leave_message.json()
        )
        
        await manager.disconnect(room_id, user_id)
```

## Error Handling

Implementing WebSocket error handling:

```python
from nexios.websockets import WebSocketException
from nexios.exceptions import WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)

class WebSocketErrorHandler:
    @staticmethod
    async def handle_error(
        websocket: WebSocket,
        error: Exception
    ):
        error_message = WebSocketMessage(
            type=MessageType.ERROR,
            content=str(error)
        )
        
        try:
            await websocket.send_json(error_message.dict())
        except:
            logger.error(f"Failed to send error message: {error}")
        
        await websocket.close()

@app.websocket("/ws/protected/{room_id}")
async def protected_websocket(
    websocket: WebSocket,
    room_id: str
):
    try:
        # Validate authentication
        if not websocket.user:
            raise WebSocketException("Authentication required")
        
        # Validate room access
        if not await can_access_room(websocket.user, room_id):
            raise WebSocketException("Access denied")
        
        await manager.connect(websocket, room_id, websocket.user.id)
        
        while True:
            try:
                data = await websocket.receive_json()
                message = WebSocketMessage(**data)
                
                # Validate message
                if not await validate_message(message):
                    raise WebSocketException("Invalid message")
                
                await manager.broadcast(
                    room_id,
                    message.json()
                )
            
            except WebSocketDisconnect:
                raise
            
            except Exception as e:
                await WebSocketErrorHandler.handle_error(
                    websocket,
                    e
                )
    
    except WebSocketDisconnect:
        await manager.disconnect(room_id, websocket.user.id)
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await WebSocketErrorHandler.handle_error(
            websocket,
            e
        )
```

## 📝 Practice Exercise

1. Build a real-time chat application:
   - User authentication
   - Multiple chat rooms
   - Private messaging
   - Typing indicators

2. Implement WebSocket features:
   - Connection pooling
   - Message queuing
   - Reconnection handling
   - Heartbeat system

3. Create a notification system:
   - Real-time alerts
   - Event broadcasting
   - User subscriptions
   - Message persistence

## 📚 Additional Resources
- [WebSocket Guide](https://nexios.dev/guide/websockets)
- [Real-time Apps](https://nexios.dev/guide/realtime)
- [Authentication](https://nexios.dev/guide/auth)
- [Error Handling](https://nexios.dev/guide/errors)

## 🎯 Next Steps
Tomorrow in [Day 14: Real-Time Chat App](../day14/index.md), we'll explore:
- Chat room implementation
- User presence
- Message history
- Real-time features
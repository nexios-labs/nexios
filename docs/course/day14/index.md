# 🚀 Day 14: Real-Time Chat App

## Chat Room Implementation

Building a complete chat room system:

```python
from nexios import get_application
from nexios.websockets import WebSocket, WebSocketManager
from nexios.security import requires_auth
from nexios.database import Database
from datetime import datetime
from typing import Dict, Set, Optional, List
import json

app = get_application()
db = Database()

class ChatRoom:
    def __init__(self, room_id: str, name: str):
        self.id = room_id
        self.name = name
        self.users: Set[str] = set()
        self.messages: List[dict] = []
        self.typing_users: Set[str] = set()

class ChatManager(WebSocketManager):
    def __init__(self):
        self.rooms: Dict[str, ChatRoom] = {}
        self.connections: Dict[str, Dict[str, WebSocket]] = {}
    
    async def create_room(self, room_id: str, name: str) -> ChatRoom:
        if room_id not in self.rooms:
            self.rooms[room_id] = ChatRoom(room_id, name)
            self.connections[room_id] = {}
        return self.rooms[room_id]
    
    async def join_room(
        self,
        websocket: WebSocket,
        room_id: str,
        user_id: str
    ):
        await websocket.accept()
        
        if room_id not in self.rooms:
            await self.create_room(room_id, f"Room {room_id}")
        
        room = self.rooms[room_id]
        room.users.add(user_id)
        self.connections[room_id][user_id] = websocket
        
        # Send room history
        await websocket.send_json({
            "type": "history",
            "messages": room.messages[-50:]  # Last 50 messages
        })
        
        # Broadcast join message
        await self.broadcast(room_id, {
            "type": "system",
            "content": f"User {user_id} joined the chat",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })
    
    async def leave_room(
        self,
        room_id: str,
        user_id: str
    ):
        if room_id in self.rooms:
            room = self.rooms[room_id]
            room.users.remove(user_id)
            room.typing_users.discard(user_id)
            
            if user_id in self.connections[room_id]:
                del self.connections[room_id][user_id]
            
            # Remove empty room
            if not room.users:
                del self.rooms[room_id]
                del self.connections[room_id]
            else:
                # Broadcast leave message
                await self.broadcast(room_id, {
                    "type": "system",
                    "content": f"User {user_id} left the chat",
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat()
                })
    
    async def broadcast(
        self,
        room_id: str,
        message: dict,
        exclude_user: Optional[str] = None
    ):
        if room_id in self.connections:
            for user_id, websocket in self.connections[room_id].items():
                if user_id != exclude_user:
                    await websocket.send_json(message)
    
    async def store_message(
        self,
        room_id: str,
        message: dict
    ):
        if room_id in self.rooms:
            self.rooms[room_id].messages.append(message)
            # Keep last 100 messages
            self.rooms[room_id].messages = self.rooms[room_id].messages[-100:]
            
            # Store in database
            await db.messages.insert_one({
                **message,
                "room_id": room_id
            })

# Initialize chat manager
chat_manager = ChatManager()

@app.websocket("/chat/{room_id}")
@requires_auth
async def chat_endpoint(
    websocket: WebSocket,
    room_id: str
):
    user = websocket.user
    await chat_manager.join_room(websocket, room_id, str(user.id))
    
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type", "message")
            
            if message_type == "message":
                message = {
                    "type": "message",
                    "content": data["content"],
                    "user_id": str(user.id),
                    "username": user.username,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Store and broadcast
                await chat_manager.store_message(room_id, message)
                await chat_manager.broadcast(room_id, message)
            
            elif message_type == "typing":
                typing_status = data.get("typing", False)
                room = chat_manager.rooms[room_id]
                
                if typing_status:
                    room.typing_users.add(str(user.id))
                else:
                    room.typing_users.discard(str(user.id))
                
                # Broadcast typing status
                await chat_manager.broadcast(
                    room_id,
                    {
                        "type": "typing",
                        "users": list(room.typing_users)
                    },
                    exclude_user=str(user.id)
                )
    
    except:
        await chat_manager.leave_room(room_id, str(user.id))
```

## User Presence

Implementing user presence features:

```python
from nexios.cache import RedisCache
import time

class PresenceManager:
    def __init__(self):
        self.cache = RedisCache()
        self.presence_timeout = 30  # seconds
    
    async def mark_online(
        self,
        user_id: str,
        room_id: str
    ):
        key = f"presence:{room_id}:{user_id}"
        await self.cache.set(
            key,
            time.time(),
            expire=self.presence_timeout * 2
        )
    
    async def get_online_users(
        self,
        room_id: str
    ) -> Set[str]:
        pattern = f"presence:{room_id}:*"
        keys = await self.cache.keys(pattern)
        online_users = set()
        
        for key in keys:
            user_id = key.split(":")[-1]
            timestamp = float(await self.cache.get(key) or 0)
            
            if time.time() - timestamp <= self.presence_timeout:
                online_users.add(user_id)
        
        return online_users

# Initialize presence manager
presence = PresenceManager()

@app.websocket("/chat/{room_id}")
@requires_auth
async def chat_with_presence(
    websocket: WebSocket,
    room_id: str
):
    user = websocket.user
    user_id = str(user.id)
    
    await chat_manager.join_room(websocket, room_id, user_id)
    
    try:
        # Start presence heartbeat
        while True:
            # Update presence
            await presence.mark_online(user_id, room_id)
            
            # Get online users
            online_users = await presence.get_online_users(room_id)
            
            # Broadcast presence update
            await chat_manager.broadcast(
                room_id,
                {
                    "type": "presence",
                    "online_users": list(online_users)
                }
            )
            
            try:
                # Wait for message or timeout
                data = await websocket.receive_json(timeout=10)
                
                # Handle regular messages
                if data["type"] == "message":
                    message = {
                        "type": "message",
                        "content": data["content"],
                        "user_id": user_id,
                        "username": user.username,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await chat_manager.store_message(room_id, message)
                    await chat_manager.broadcast(room_id, message)
            
            except TimeoutError:
                # Just update presence
                continue
    
    except:
        await chat_manager.leave_room(room_id, user_id)
```

## Message History

Managing chat history:

```python
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

class MessageStore:
    def __init__(self):
        self.client = AsyncIOMotorClient()
        self.db = self.client.chat_db
    
    async def store_message(self, message: dict):
        await self.db.messages.insert_one(message)
    
    async def get_room_history(
        self,
        room_id: str,
        limit: int = 50,
        before_id: Optional[str] = None
    ) -> List[dict]:
        query = {"room_id": room_id}
        
        if before_id:
            query["_id"] = {"$lt": ObjectId(before_id)}
        
        messages = await self.db.messages.find(
            query,
            sort=[("_id", -1)],
            limit=limit
        ).to_list(None)
        
        return list(reversed(messages))
    
    async def search_messages(
        self,
        room_id: str,
        query: str,
        limit: int = 20
    ) -> List[dict]:
        return await self.db.messages.find({
            "room_id": room_id,
            "content": {"$regex": query, "$options": "i"}
        }).limit(limit).to_list(None)

# Initialize message store
message_store = MessageStore()

@app.get("/chat/{room_id}/history")
@requires_auth
async def get_chat_history(
    room_id: str,
    before_id: Optional[str] = None,
    limit: int = 50
):
    messages = await message_store.get_room_history(
        room_id,
        limit,
        before_id
    )
    return {"messages": messages}

@app.get("/chat/{room_id}/search")
@requires_auth
async def search_chat(
    room_id: str,
    q: str,
    limit: int = 20
):
    messages = await message_store.search_messages(
        room_id,
        q,
        limit
    )
    return {"messages": messages}
```

## Real-Time Features

Adding advanced real-time features:

```python
from asyncio import Queue
from dataclasses import dataclass
from typing import Any

@dataclass
class ChatEvent:
    type: str
    room_id: str
    data: Any

class EventManager:
    def __init__(self):
        self.queues: Dict[str, Queue[ChatEvent]] = {}
    
    def add_subscriber(self, room_id: str) -> Queue[ChatEvent]:
        queue = Queue()
        if room_id not in self.queues:
            self.queues[room_id] = set()
        self.queues[room_id].add(queue)
        return queue
    
    def remove_subscriber(self, room_id: str, queue: Queue):
        if room_id in self.queues:
            self.queues[room_id].discard(queue)
            if not self.queues[room_id]:
                del self.queues[room_id]
    
    async def publish(self, event: ChatEvent):
        if event.room_id in self.queues:
            for queue in self.queues[event.room_id]:
                await queue.put(event)

# Initialize event manager
events = EventManager()

@app.websocket("/chat/{room_id}/events")
@requires_auth
async def chat_events(
    websocket: WebSocket,
    room_id: str
):
    await websocket.accept()
    queue = events.add_subscriber(room_id)
    
    try:
        while True:
            event = await queue.get()
            await websocket.send_json({
                "type": event.type,
                "data": event.data
            })
    finally:
        events.remove_subscriber(room_id, queue)

# Publish events
async def notify_typing(
    room_id: str,
    user_id: str,
    is_typing: bool
):
    await events.publish(ChatEvent(
        type="typing",
        room_id=room_id,
        data={
            "user_id": user_id,
            "typing": is_typing
        }
    ))

async def notify_reaction(
    room_id: str,
    message_id: str,
    user_id: str,
    reaction: str
):
    await events.publish(ChatEvent(
        type="reaction",
        room_id=room_id,
        data={
            "message_id": message_id,
            "user_id": user_id,
            "reaction": reaction
        }
    ))
```

## 📝 Practice Exercise

1. Enhance the chat application:
   - File sharing
   - Message reactions
   - Read receipts
   - User mentions

2. Add advanced features:
   - Voice messages
   - Message threading
   - User status
   - Typing indicators

3. Implement chat rooms:
   - Private rooms
   - Group management
   - Room settings
   - Moderation tools

## 📚 Additional Resources
- [WebSocket Guide](https://nexios.dev/guide/websockets)
- [Real-time Features](https://nexios.dev/guide/realtime)
- [MongoDB Integration](https://nexios.dev/guide/mongodb)
- [Redis Pub/Sub](https://nexios.dev/guide/redis)

## 🎯 Next Steps
Tomorrow in [Day 15: Background Tasks](../day15/index.md), we'll explore:
- Task queues
- Async workers
- Scheduled tasks
- Progress tracking
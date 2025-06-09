# Day 9: WebSockets

Welcome to Day 9! Today we'll learn how to implement real-time communication using WebSockets in Nexios.

## Understanding WebSockets

WebSockets provide:
- Full-duplex communication
- Real-time data transfer
- Persistent connections
- Low latency
- Reduced overhead

## Basic WebSocket Setup

```python
from nexios import NexiosApp, WebSocket
from typing import Dict, Set
import json

app = NexiosApp()

# Store connected clients
connected_clients: Set[WebSocket] = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            # Echo message back
            await websocket.send_json({
                "message": f"Server received: {data['message']}"
            })
    except:
        pass
    finally:
        connected_clients.remove(websocket)
```

## Broadcasting Messages

```python
async def broadcast(message: dict):
    """Send message to all connected clients"""
    for client in connected_clients:
        try:
            await client.send_json(message)
        except:
            connected_clients.remove(client)

@app.websocket("/chat")
async def chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            # Broadcast message to all clients
            await broadcast({
                "type": "message",
                "user": data.get("user", "Anonymous"),
                "message": data["message"]
            })
    except:
        pass
    finally:
        connected_clients.remove(websocket)
```

## WebSocket Authentication

```python
import jwt
from nexios.exceptions import WebSocketException

async def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except:
        raise WebSocketException(code=4001, reason="Invalid token")

@app.websocket("/ws/auth")
async def authenticated_websocket(websocket: WebSocket):
    # Get token from query params
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return
    
    try:
        # Verify token
        payload = await verify_token(token)
        user_id = payload["sub"]
        
        # Accept connection
        await websocket.accept()
        websocket.state.user_id = user_id
        
        while True:
            data = await websocket.receive_json()
            await websocket.send_json({
                "user_id": user_id,
                "message": data["message"]
            })
    except WebSocketException as e:
        await websocket.close(code=e.code, reason=e.reason)
    except:
        await websocket.close(code=1011)
```

## Room Management

```python
from dataclasses import dataclass, field
from typing import Dict, Set

@dataclass
class ChatRoom:
    name: str
    clients: Set[WebSocket] = field(default_factory=set)
    
    async def broadcast(self, message: dict):
        for client in self.clients.copy():
            try:
                await client.send_json(message)
            except:
                self.clients.remove(client)

class ChatManager:
    def __init__(self):
        self.rooms: Dict[str, ChatRoom] = {}
    
    def get_or_create_room(self, name: str) -> ChatRoom:
        if name not in self.rooms:
            self.rooms[name] = ChatRoom(name)
        return self.rooms[name]
    
    def remove_client(self, client: WebSocket):
        for room in self.rooms.values():
            room.clients.discard(client)

chat_manager = ChatManager()

@app.websocket("/chat/{room_name}")
async def room_chat(websocket: WebSocket, room_name: str):
    await websocket.accept()
    
    room = chat_manager.get_or_create_room(room_name)
    room.clients.add(websocket)
    
    try:
        # Notify room join
        await room.broadcast({
            "type": "system",
            "message": f"User joined room {room_name}"
        })
        
        while True:
            data = await websocket.receive_json()
            await room.broadcast({
                "type": "message",
                "room": room_name,
                "user": data.get("user", "Anonymous"),
                "message": data["message"]
            })
    except:
        pass
    finally:
        chat_manager.remove_client(websocket)
        await room.broadcast({
            "type": "system",
            "message": f"User left room {room_name}"
        })
```

## Real-time Updates

```python
from asyncio import Queue
from datetime import datetime

class UpdateManager:
    def __init__(self):
        self.subscribers: Dict[str, Set[WebSocket]] = {}
    
    def subscribe(self, topic: str, client: WebSocket):
        if topic not in self.subscribers:
            self.subscribers[topic] = set()
        self.subscribers[topic].add(client)
    
    def unsubscribe(self, topic: str, client: WebSocket):
        if topic in self.subscribers:
            self.subscribers[topic].discard(client)
    
    async def publish(self, topic: str, message: dict):
        if topic in self.subscribers:
            for client in self.subscribers[topic].copy():
                try:
                    await client.send_json({
                        "topic": topic,
                        "data": message,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except:
                    self.subscribers[topic].discard(client)

update_manager = UpdateManager()

# Subscribe to updates
@app.websocket("/updates/{topic}")
async def updates_endpoint(websocket: WebSocket, topic: str):
    await websocket.accept()
    update_manager.subscribe(topic, websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except:
        pass
    finally:
        update_manager.unsubscribe(topic, websocket)

# Publish updates
@app.post("/publish/{topic}")
async def publish_update(request: Request, response: Response, topic: str):
    data = await request.json()
    await update_manager.publish(topic, data)
    return response.json({"message": "Update published"})
```

## Mini-Project: Real-time Chat Application

```python
from nexios import NexiosApp, WebSocket
from typing import Dict, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import asyncio
from enum import Enum

# Message types
class MessageType(str, Enum):
    CHAT = "chat"
    JOIN = "join"
    LEAVE = "leave"
    TYPING = "typing"
    SYSTEM = "system"

@dataclass
class ChatMessage:
    type: MessageType
    room: str
    user: str
    content: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

@dataclass
class ChatUser:
    id: str
    name: str
    room: str
    websocket: WebSocket
    is_typing: bool = False
    last_typed: datetime = field(default_factory=datetime.utcnow)

class ChatRoom:
    def __init__(self, name: str):
        self.name = name
        self.users: Dict[str, ChatUser] = {}
        self.messages: List[ChatMessage] = []
        self.max_messages = 100
    
    def add_message(self, message: ChatMessage):
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
    
    async def broadcast(self, message: ChatMessage):
        for user in self.users.values():
            try:
                await user.websocket.send_json(message.__dict__)
            except:
                await self.remove_user(user.id)
    
    async def remove_user(self, user_id: str):
        if user_id in self.users:
            user = self.users.pop(user_id)
            await self.broadcast(ChatMessage(
                type=MessageType.LEAVE,
                room=self.name,
                user=user.name
            ))

class ChatServer:
    def __init__(self):
        self.rooms: Dict[str, ChatRoom] = {}
    
    def get_or_create_room(self, name: str) -> ChatRoom:
        if name not in self.rooms:
            self.rooms[name] = ChatRoom(name)
        return self.rooms[name]
    
    async def handle_typing(self, user: ChatUser):
        """Handle user typing status"""
        if not user.is_typing:
            user.is_typing = True
            await self.rooms[user.room].broadcast(ChatMessage(
                type=MessageType.TYPING,
                room=user.room,
                user=user.name,
                content="is typing..."
            ))
        
        user.last_typed = datetime.utcnow()
        
        # Reset typing status after 2 seconds
        await asyncio.sleep(2)
        
        if (datetime.utcnow() - user.last_typed).total_seconds() >= 2:
            user.is_typing = False
            await self.rooms[user.room].broadcast(ChatMessage(
                type=MessageType.TYPING,
                room=user.room,
                user=user.name,
                content="stopped typing"
            ))

app = NexiosApp()
chat_server = ChatServer()

@app.websocket("/chat/{room_name}/{user_name}")
async def chat_endpoint(
    websocket: WebSocket,
    room_name: str,
    user_name: str
):
    await websocket.accept()
    
    # Setup user and room
    user = ChatUser(
        id=str(id(websocket)),
        name=user_name,
        room=room_name,
        websocket=websocket
    )
    
    room = chat_server.get_or_create_room(room_name)
    room.users[user.id] = user
    
    # Send room history
    for message in room.messages:
        await websocket.send_json(message.__dict__)
    
    # Announce join
    join_message = ChatMessage(
        type=MessageType.JOIN,
        room=room_name,
        user=user_name
    )
    room.add_message(join_message)
    await room.broadcast(join_message)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "typing":
                asyncio.create_task(
                    chat_server.handle_typing(user)
                )
            else:
                message = ChatMessage(
                    type=MessageType.CHAT,
                    room=room_name,
                    user=user_name,
                    content=data["content"]
                )
                room.add_message(message)
                await room.broadcast(message)
    except:
        pass
    finally:
        await room.remove_user(user.id)

# HTML client
@app.get("/chat-client")
async def chat_client(request: Request, response: Response):
    return response.html("""
<!DOCTYPE html>
<html>
<head>
    <title>Nexios Chat</title>
    <style>
        body { margin: 0; padding: 20px; font-family: Arial; }
        #messages { height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; }
        #typing { height: 20px; color: #666; }
        .message { margin: 5px 0; }
        .system { color: #666; font-style: italic; }
        .join { color: green; }
        .leave { color: red; }
    </style>
</head>
<body>
    <div id="messages"></div>
    <div id="typing"></div>
    <input type="text" id="messageInput" placeholder="Type a message...">
    <button onclick="sendMessage()">Send</button>

    <script>
        const room = prompt('Enter room name:') || 'general';
        const username = prompt('Enter username:') || 'anonymous';
        const ws = new WebSocket(`ws://localhost:5000/chat/${room}/${username}`);
        let typingTimeout;

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const messages = document.getElementById('messages');
            const typing = document.getElementById('typing');

            if (data.type === 'typing') {
                if (data.user !== username) {
                    typing.textContent = data.content === 'is typing...' 
                        ? `${data.user} is typing...`
                        : '';
                }
            } else {
                const div = document.createElement('div');
                div.className = `message ${data.type}`;
                
                if (data.type === 'chat') {
                    div.textContent = `${data.user}: ${data.content}`;
                } else {
                    div.textContent = `${data.user} ${data.type === 'join' ? 'joined' : 'left'} the room`;
                }
                
                messages.appendChild(div);
                messages.scrollTop = messages.scrollHeight;
            }
        };

        document.getElementById('messageInput').onkeyup = (e) => {
            if (typingTimeout) clearTimeout(typingTimeout);
            
            ws.send(JSON.stringify({
                type: 'typing'
            }));
            
            if (e.key === 'Enter') {
                sendMessage();
            }
        };

        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (message) {
                ws.send(JSON.stringify({
                    type: 'chat',
                    content: message
                }));
                input.value = '';
            }
        }
    </script>
</body>
</html>
    """)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
```

## Key Concepts Learned

- WebSocket basics
- Connection management
- Broadcasting messages
- Room management
- Real-time updates
- Authentication
- Error handling
- Client implementation

## Additional Resources

- [WebSocket Protocol](https://tools.ietf.org/html/rfc6455)
- [MDN WebSocket Guide](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [ASGI WebSocket Spec](https://asgi.readthedocs.io/en/latest/specs/www.html#websocket)
- [Real-time Patterns](https://www.nginx.com/blog/websocket-nginx/)

## Homework

1. Implement a real-time dashboard:
   - System metrics
   - User activity
   - Error monitoring
   - Performance stats

2. Create a collaborative editor:
   - Operational transforms
   - Cursor tracking
   - User presence
   - Document sync

3. Build a multiplayer game:
   - Game state sync
   - Player movements
   - Collision detection
   - Score tracking

## Next Steps

Tomorrow, we'll explore testing in [Day 10: Testing](../day10/index.md). 
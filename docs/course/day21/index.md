# Day 21: Project: Chat Application

## Learning Objectives
- Build a real-time chat application using Nexios WebSockets
- Master ChannelBox for group messaging and history
- Implement real-time presence tracking
- Handle message persistence and history

## Project Overview

The chat application will demonstrate Nexios's powerful WebSocket and Channel features:

- Channel-based room management
- Message history with automatic persistence
- Real-time presence tracking
- System messages for user events
- Typing indicators

## Implementation

First, let's create a chat application using ChannelBox:

```python
from nexios import NexiosApp
from nexios.websockets import WebSocket, WebSocketConsumer
from nexios.websockets.channels import Channel, ChannelBox
from nexios.auth import auth
from nexios.http import Request, Response
from datetime import datetime
import json
import uuid

app = NexiosApp()

class ChatConsumer(WebSocketConsumer):
    encoding = "json"
    
    async def on_connect(self, websocket: WebSocket):
        """Handle new WebSocket connection"""
        await websocket.accept()
        
        # Get user and room info
        user = websocket.scope.get("user", {"username": "anonymous"})
        room_id = websocket.scope["path_params"].get("room_id")
        
        # Set up channel groups
        self.room_group = f"chat_room_{room_id}"
        self.presence_group = f"presence_{user['username']}"
        
        # Join channel groups
        await self.join_group(self.room_group)
        await self.join_group(self.presence_group)
        
        # Send room history
        history = await ChannelBox.show_history(self.room_group)
        if history:
            await websocket.send_json({
                "type": "history",
                "messages": [msg.payload for msg in history[-50:]]
            })
        
        # Announce user presence
        await self.broadcast(
            payload={
                "type": "system",
                "content": f"{user['username']} joined",
                "timestamp": datetime.now().isoformat()
            },
            group_name=self.room_group,
            save_history=True
        )
        
        # Send current online users
        groups = await ChannelBox.show_groups()
        online_users = set()
        for group_name in groups:
            if group_name.startswith("presence_"):
                online_users.add(group_name.split("_")[1])
        
        await websocket.send_json({
            "type": "online_users",
            "users": list(online_users)
        })
    
    async def on_receive(self, websocket: WebSocket, data: dict):
        """Handle incoming messages"""
        user = websocket.scope.get("user", {"username": "anonymous"})
        
        if data["type"] == "message":
            # Broadcast message with history
            await self.broadcast(
                payload={
                    "type": "message",
                    "user": user["username"],
                    "content": data["content"],
                    "timestamp": datetime.now().isoformat()
                },
                group_name=self.room_group,
                save_history=True
            )
        
        elif data["type"] == "typing":
            # Broadcast typing status (no history)
            await self.broadcast(
                payload={
                    "type": "typing",
                    "user": user["username"],
                    "is_typing": data.get("is_typing", True)
                },
                group_name=self.room_group,
                save_history=False
            )
        
        elif data["type"] == "private_message":
            # Send private message to specific user
            target_user = data["to_user"]
            await self.broadcast(
                payload={
                    "type": "private",
                    "from_user": user["username"],
                    "content": data["content"],
                    "timestamp": datetime.now().isoformat()
                },
                group_name=f"presence_{target_user}",
                save_history=True
            )
    
    async def on_disconnect(self, websocket: WebSocket, close_code: int):
        """Handle disconnection"""
        user = websocket.scope.get("user", {"username": "anonymous"})
        
        # Announce user left
        await self.broadcast(
            payload={
                "type": "system",
                "content": f"{user['username']} left",
                "timestamp": datetime.now().isoformat()
            },
            group_name=self.room_group,
            save_history=True
        )
        
        # Leave all groups
        await self.leave_group(self.room_group)
        await self.leave_group(self.presence_group)

# Register the WebSocket route
app.add_route("/ws/chat/{room_id}", ChatConsumer.as_route("/ws/chat/{room_id}"))
```

## Client Integration

Here's a JavaScript client that utilizes all the features:

```javascript
class ChatClient {
    constructor(roomId, username) {
        this.roomId = roomId;
        this.username = username;
        this.ws = new WebSocket(`ws://localhost:8000/ws/chat/${roomId}`);
        this.onlineUsers = new Set();
        
        // Set up event handlers
        this.ws.onmessage = this.handleMessage.bind(this);
        this.ws.onclose = () => console.log('Disconnected from chat');
        this.ws.onerror = (error) => console.error('WebSocket error:', error);
    }
    
    handleMessage(event) {
        const data = JSON.parse(event.data);
        
        switch (data.type) {
            case 'message':
                this.handleChatMessage(data);
                break;
            case 'private':
                this.handlePrivateMessage(data);
                break;
            case 'system':
                this.handleSystemMessage(data);
                break;
            case 'typing':
                this.handleTypingStatus(data);
                break;
            case 'history':
                this.handleHistory(data.messages);
                break;
            case 'online_users':
                this.handleOnlineUsers(data.users);
                break;
        }
    }
    
    sendMessage(content) {
        this.ws.send(JSON.stringify({
            type: 'message',
            content: content
        }));
    }
    
    sendPrivateMessage(toUser, content) {
        this.ws.send(JSON.stringify({
            type: 'private_message',
            to_user: toUser,
            content: content
        }));
    }
    
    setTyping(isTyping) {
        this.ws.send(JSON.stringify({
            type: 'typing',
            is_typing: isTyping
        }));
    }
    
    handleChatMessage(data) {
        console.log(`${data.user}: ${data.content}`);
    }
    
    handlePrivateMessage(data) {
        console.log(`[Private] ${data.from_user}: ${data.content}`);
    }
    
    handleSystemMessage(data) {
        console.log(`System: ${data.content}`);
    }
    
    handleTypingStatus(data) {
        if (data.is_typing) {
            console.log(`${data.user} is typing...`);
        }
    }
    
    handleHistory(messages) {
        console.log('Chat history:', messages);
        messages.forEach(msg => {
            switch (msg.type) {
                case 'message':
                    this.handleChatMessage(msg);
                    break;
                case 'system':
                    this.handleSystemMessage(msg);
                    break;
            }
        });
    }
    
    handleOnlineUsers(users) {
        this.onlineUsers = new Set(users);
        console.log('Online users:', Array.from(this.onlineUsers));
    }
    
    disconnect() {
        this.ws.close();
    }
}
```

## Key Features Demonstrated

1. **Channel Management**
   - Room channels for group chat
   - Presence channels for user status
   - Private message channels

2. **Message History**
   - Automatic history saving with `save_history=True`
   - History retrieval on connection
   - System messages in history

3. **Real-time Features**
   - Typing indicators
   - Online user tracking
   - Join/leave notifications

4. **Private Messaging**
   - User-to-user messaging using presence channels
   - Private message history

## 📝 Practice Exercise

1. Enhance the chat application:
   - Add support for chat room categories
   - Implement message reactions using ChannelBox
   - Add user-to-user presence status (online, away, busy)
   - Create a moderation system using private channels

2. Improve error handling:
   - Add reconnection logic
   - Handle message delivery confirmation
   - Implement rate limiting
   - Add channel cleanup for inactive users
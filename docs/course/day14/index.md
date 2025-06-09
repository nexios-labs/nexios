# 🚀 Day 14: Real-Time Chat App with ChannelBox

## Learning Objectives
- Master ChannelBox for WebSocket group management
- Implement real-time chat features
- Handle message history and broadcasting
- Build presence tracking and notifications

## ChannelBox Setup

The ChannelBox class provides powerful tools for organizing WebSocket channels:

```python
from nexios import NexiosApp
from nexios.websockets.base import WebSocket, WebSocketDisconnect
from nexios.websockets.channels import Channel, ChannelBox
from nexios.auth import auth
from datetime import datetime
import json

app = NexiosApp()

@app.ws_route("/chat/{room_id}")
@auth(["jwt"])
async def chat_room(ws: WebSocket, room_id: str):
    await ws.accept()
    user = ws.scope["user"]
    channel = Channel(websocket=ws, payload_type="json")
    
    # Add channel to room group
    await ChannelBox.add_channel_to_group(
        channel, 
        group_name=f"chat_{room_id}"
    )
    
    try:
        # Send join message
        await ChannelBox.group_send(
            group_name=f"chat_{room_id}",
            payload={
                "type": "system",
                "message": f"{user.username} joined the chat",
                "timestamp": datetime.now().isoformat()
            },
            save_history=True
        )
        
        # Get and send chat history
        history = await ChannelBox.show_history(f"chat_{room_id}")
        if history:
            await ws.send_json({
                "type": "history",
                "messages": history[-50:]  # Last 50 messages
            })
        
        while True:
            data = await ws.receive_json()
            # Broadcast message to room
            await ChannelBox.group_send(
                group_name=f"chat_{room_id}",
                payload={
                    "type": "message",
                    "user": user.username,
                    "content": data["message"],
                    "timestamp": datetime.now().isoformat()
                },
                save_history=True
            )
    except WebSocketDisconnect:
        # Send leave message
        await ChannelBox.group_send(
            group_name=f"chat_{room_id}",
            payload={
                "type": "system",
                "message": f"{user.username} left the chat",
                "timestamp": datetime.now().isoformat()
            },
            save_history=True
        )
    finally:
        # Remove channel from group
        await ChannelBox.remove_channel_from_group(
            channel, 
            group_name=f"chat_{room_id}"
        )
```

## Presence Tracking

Implementing user presence with ChannelBox:

```python
@app.ws_route("/presence")
@auth(["jwt"])
async def presence_handler(ws: WebSocket):
    await ws.accept()
    user = ws.scope["user"]
    channel = Channel(websocket=ws, payload_type="json")
    
    # Add to presence group
    await ChannelBox.add_channel_to_group(
        channel, 
        group_name="presence"
    )
    
    try:
        # Send online status
        await ChannelBox.group_send(
            group_name="presence",
            payload={
                "type": "status",
                "user": user.username,
                "status": "online",
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Show active users
        groups = await ChannelBox.show_groups()
        presence_channels = groups.get("presence", {})
        online_users = len(presence_channels)
        
        await ws.send_json({
            "type": "users",
            "count": online_users
        })
        
        while True:
            # Keep connection alive and handle status updates
            data = await ws.receive_json()
            if data.get("type") == "status":
                await ChannelBox.group_send(
                    group_name="presence",
                    payload={
                        "type": "status",
                        "user": user.username,
                        "status": data["status"],
                        "timestamp": datetime.now().isoformat()
                    }
                )
    finally:
        # Remove from presence group
        await ChannelBox.remove_channel_from_group(
            channel, 
            group_name="presence"
        )
        
        # Broadcast offline status
        await ChannelBox.group_send(
            group_name="presence",
            payload={
                "type": "status",
                "user": user.username,
                "status": "offline",
                "timestamp": datetime.now().isoformat()
            }
        )
```

## Private Messaging

Implementing direct messages with ChannelBox:

```python
@app.ws_route("/dm/{user_id}")
@auth(["jwt"])
async def direct_message(ws: WebSocket, user_id: str):
    await ws.accept()
    sender = ws.scope["user"]
    channel = Channel(websocket=ws, payload_type="json")
    
    # Add to user's DM group
    dm_group = f"dm_{sender.id}"
    await ChannelBox.add_channel_to_group(channel, dm_group)
    
    try:
        while True:
            data = await ws.receive_json()
            # Send private message
            await ChannelBox.group_send(
                group_name=f"dm_{user_id}",
                payload={
                    "type": "direct_message",
                    "from": sender.username,
                    "content": data["message"],
                    "timestamp": datetime.now().isoformat()
                },
                save_history=True
            )
    finally:
        await ChannelBox.remove_channel_from_group(
            channel, 
            dm_group
        )
```

## 📝 Practice Exercise

1. Enhance the chat application:
   - Add typing indicators
   - Implement message reactions
   - Add file sharing support
   - Create private chat rooms

2. Implement advanced features:
   - Message threading
   - User mentions
   - Message search
   - Read receipts

3. Add admin features:
   - User moderation
   - Message deletion
   - Room management
   - Usage analytics

## 📚 Additional Resources
- [ChannelBox Guide](../../guide/websockets/groups.md)
- [WebSocket Events](../../guide/websockets/events.md)
- [WebSocket Consumer](../../guide/websockets/consumer.md)
- [Error Handling](../../guide/error-handling.md)

## 🎯 Next Steps
Tomorrow in [Day 15: Background Tasks](../day15/index.md), we'll explore:
- Task queues
- Async workers
- Scheduled tasks
- Progress tracking
# 🚀 Day 16: Real-time Application Patterns

## Learning Objectives
- Master real-time application patterns
- Implement event-driven architectures
- Handle WebSocket scaling
- Build real-time features

## WebSocket Events Integration

Nexios combines WebSockets with a powerful event system:

```python
from nexios import NexiosApp
from nexios.websockets.base import WebSocket
from nexios.websockets.channels import Channel, ChannelBox
from nexios.auth import auth

app = NexiosApp()

@app.ws_route("/notifications")
@auth(["jwt"])
async def notification_handler(ws: WebSocket):
    await ws.accept()
    user = ws.scope["user"]
    channel = Channel(websocket=ws, payload_type="json")
    
    # Add to user's notification group
    await ChannelBox.add_channel_to_group(
        channel, 
        group_name=f"notifications_{user.id}"
    )
    
    try:
        while True:
            data = await ws.receive_json()
            # Handle user acknowledgment
            if data["type"] == "ack":
                await mark_notification_read(data["notification_id"])
    finally:
        await ChannelBox.remove_channel_from_group(
            channel, 
            group_name=f"notifications_{user.id}"
        )

# Event handler for new notifications
@app.events.on("notification.created")
async def handle_new_notification(notification):
    user_id = notification["user_id"]
    await ChannelBox.group_send(
        group_name=f"notifications_{user_id}",
        payload={
            "type": "notification",
            "data": notification
        }
    )
```

## Real-time Dashboard

Building a live dashboard with WebSocket updates:

```python
from datetime import datetime
import asyncio

@app.ws_route("/dashboard")
@auth(["jwt"])
async def dashboard_feed(ws: WebSocket):
    await ws.accept()
    channel = Channel(websocket=ws, payload_type="json")
    
    # Add to dashboard subscribers
    await ChannelBox.add_channel_to_group(
        channel, 
        group_name="dashboard"
    )
    
    try:
        # Send initial data
        metrics = await get_current_metrics()
        await ws.send_json({
            "type": "initial",
            "data": metrics
        })
        
        # Keep connection alive and handle updates
        while True:
            await asyncio.sleep(5)  # Update every 5 seconds
            metrics = await get_current_metrics()
            await ChannelBox.group_send(
                group_name="dashboard",
                payload={
                    "type": "update",
                    "data": metrics,
                    "timestamp": datetime.now().isoformat()
                }
            )
    finally:
        await ChannelBox.remove_channel_from_group(
            channel, 
            group_name="dashboard"
        )

# Update metrics from other parts of the application
async def update_dashboard_metrics(metrics):
    await ChannelBox.group_send(
        group_name="dashboard",
        payload={
            "type": "update",
            "data": metrics,
            "timestamp": datetime.now().isoformat()
        }
    )
```

## Collaborative Features

Implementing real-time collaboration:

```python
@app.ws_route("/collab/{document_id}")
@auth(["jwt"])
async def document_collaboration(ws: WebSocket, document_id: str):
    await ws.accept()
    user = ws.scope["user"]
    channel = Channel(websocket=ws, payload_type="json")
    
    # Join document's collaboration group
    group_name = f"doc_{document_id}"
    await ChannelBox.add_channel_to_group(channel, group_name)
    
    try:
        # Send current document state
        doc = await get_document(document_id)
        await ws.send_json({
            "type": "initial",
            "content": doc["content"],
            "version": doc["version"]
        })
        
        # Handle collaborative edits
        while True:
            data = await ws.receive_json()
            if data["type"] == "edit":
                # Apply edit and broadcast to others
                await ChannelBox.group_send(
                    group_name=group_name,
                    payload={
                        "type": "edit",
                        "user": user.username,
                        "changes": data["changes"],
                        "version": data["version"],
                        "timestamp": datetime.now().isoformat()
                    },
                    exclude=channel  # Don't send back to sender
                )
                
            elif data["type"] == "cursor":
                # Broadcast cursor position
                await ChannelBox.group_send(
                    group_name=group_name,
                    payload={
                        "type": "cursor",
                        "user": user.username,
                        "position": data["position"]
                    },
                    exclude=channel
                )
    finally:
        await ChannelBox.remove_channel_from_group(
            channel, 
            group_name=group_name
        )
```

## 📝 Practice Exercise

1. Build a real-time analytics dashboard:
   - Live metrics updates
   - User activity tracking
   - System health monitoring
   - Alert notifications

2. Create a collaborative editor:
   - Real-time text synchronization
   - Cursor position tracking
   - User presence indicators
   - Edit history

3. Implement a live auction system:
   - Bid broadcasting
   - Time synchronization
   - User notifications
   - Auction status updates

## 📚 Additional Resources
- [WebSocket Events](../../guide/websockets/events.md)
- [Real-time Patterns](../../guide/websockets/consumer.md)
- [ChannelBox Guide](../../guide/websockets/groups.md)
- [Event System](../../guide/events.md)

## 🎯 Next Steps
Tomorrow in [Day 17: Advanced Middleware](../day17/index.md), we'll explore:
- Custom middleware creation
- Request/Response modification
- Error handling middleware
- Authentication middleware
# Day 25: Nexios Event System

## Learning Objectives
- Understand Nexios's event system fundamentals
- Implement event-driven patterns
- Work with WebSocket events
- Manage event listeners effectively

## Event System Overview

Nexios provides a flexible event system that enables loosely coupled, event-driven architectures. The system is built around these core concepts:
- Basic event subscription and emission
- Event namespaces for organization
- Priority-based listeners
- One-time event handlers
- WebSocket integration
- Async event support

## Basic Event Usage

```python
from nexios import NexiosApp

app = NexiosApp()

@app.events.on("user.created")
async def handle_user_created(user):
    print(f"User created: {user['name']}")

# Trigger the event
await app.events.emit("user.created", {"name": "Bob"})
```

## Event Listeners

### Basic Subscription

```python
@app.events.on("data.received")
async def handle_data(data):
    print(f"Processing data: {data}")
```

### Removing Listeners

```python
# Define handler
async def temporary_handler(data):
    print(f"Processing data: {data}")

# Add handler
app.events.on("data.received", temporary_handler)

# Remove specific handler
app.events.off("data.received", temporary_handler)

# Remove all handlers for an event
app.events.off("data.received")
```

### Priority Listeners

```python
from nexios.events import EventPriority

# Different priority levels
app.events.on("data.received", handler1, priority=EventPriority.LOW)
app.events.on("data.received", handler2, priority=EventPriority.MEDIUM)
app.events.on("data.received", handler3, priority=EventPriority.HIGH)
```

### One-time Listeners

```python
@app.events.once('first.login')
async def first_login(user):
    print(f"🎉 Welcome {user}")

await app.events.emit('first.login', 'Alice')  # Fires
await app.events.emit('first.login', 'Alice')  # Doesn't fire
```

## Event Namespaces

```python
# Create a namespace
ui_events = app.events.namespace('ui')

@ui_events.on('button.click')  # Listens to 'ui:button.click'
async def handle_click(btn):
    print(f"{btn} clicked!")

# Both work:
await ui_events.emit('button.click', 'submit')
await app.events.emit('ui:button.click', 'submit')
```

## WebSocket Integration

### Connection Events

```python
@app.ws_route("/chat")
async def chat_handler(ws: WebSocket):
    await ws.accept()
    await app.events.emit("ws.connected", {"client": ws.client})
    
    try:
        while True:
            message = await ws.receive_json()
            await app.events.emit("chat.message", message)
    except Exception as e:
        await app.events.emit("ws.error", {"error": str(e)})
```

### Notifications Example

```python
@app.events.on("notification.created")  
async def push_notification(notification):
    await ChannelBox.group_send(
        group_name="notifications",
        payload=notification
    )
```

## Error Handling

```python
@app.events.on("ws.error")  
async def handle_errors(error):
    logging.error(f"WebSocket failure: {error}")
    # Alert monitoring systems

try:
    # Your code here
    ...
except Exception as e:
    await app.events.emit("ws.error", {"error": str(e)})
```

## Complete Chat Application Example

```python
@app.ws_route("/chat/{room}")  
async def chat_room(ws: WebSocket):
    room = ws.path_params["room"]
    channel = Channel(websocket=ws)
    await ChannelBox.add_channel_to_group(channel, f"chat_{room}")

    try:
        while True:
            msg = await ws.receive_json()
            await app.events.emit("room.message", {
                "room": room,
                "message": msg
            })
    finally:
        await ChannelBox.remove_channel_from_group(channel, f"chat_{room}")

@app.events.on("room.message")  
async def broadcast(msg):
    await ChannelBox.group_send(
        group_name=f"chat_{msg['room']}",
        payload=msg
    )
```

## Best Practices

1. Event Naming:
   - Use descriptive event names
   - Follow a consistent naming pattern
   - Use namespaces for organization

2. Error Handling:
   - Always handle WebSocket exceptions
   - Emit error events for centralized handling
   - Log errors appropriately

3. WebSocket Integration:
   - Use ChannelBox for group messaging
   - Properly manage connections
   - Clean up resources in finally blocks

4. Event Design:
   - Keep events focused and single-purpose
   - Document event payloads
   - Consider using TypeScript for type safety

## 📝 Practice Exercise

1. Build a real-time chat application:
   - Implement room-based chat using WebSockets
   - Use events for message broadcasting
   - Add error handling
   - Implement user presence tracking

2. Create a notification system:
   - Set up event-based notifications
   - Implement priority-based handlers
   - Add WebSocket push notifications
   - Handle offline message queueing
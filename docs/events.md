# Nexios Event System Integration Guide

## Overview

The Nexios framework includes a powerful event system built around the `AsyncEventEmitter` class, which provides asynchronous event handling capabilities that integrate seamlessly with Nexios' async-first architecture.

## Core Event Components

### `AsyncEventEmitter`

The primary event emitter class that works with Nexios' asynchronous environment:

```python
from nexios.events import AsyncEventEmitter

emitter = AsyncEventEmitter()
```

## Integration with Nexios Application

### Initializing the Event System

```python
from nexios import get_application
from nexios.events import AsyncEventEmitter

app = get_application()
emitter = AsyncEventEmitter()
```

### Basic Event Usage

#### Registering Event Listeners

```python
@emitter.on('user_created')
async def handle_user_created(user_data):
    print(f"New user created: {user_data['username']}")
```

#### Triggering Events

```python
@app.post("/users")
async def create_user(req: Request, res: Response):
    user_data = await req.json()
    # Process user creation...
    await emitter.emit('user_created', user_data)
    return res.json({"status": "success"})
```

## Advanced Patterns

### Request-Scoped Events

```python
async def request_logger_middleware(req, res, cnext):
    start_time = time.time()
    
    @emitter.on(f"request:{req.id}")
    async def log_request_complete():
        duration = time.time() - start_time
        print(f"Request {req.id} completed in {duration:.2f}s")
    
    await cnext()
    await emitter.emit(f"request:{req.id}")
```

### Websocket Integration

```python
@app.ws_route("/chat")
async def chat_handler(ws: WebSocket):
    await ws.accept()
    
    @emitter.on('chat_message')
    async def handle_chat_message(message):
        await ws.send_text(message)
    
    try:
        while True:
            message = await ws.receive_text()
            await emitter.emit('chat_message', message)
    except WebSocketDisconnect:
        emitter.remove_listener('chat_message', handle_chat_message)
```

### Error Handling Events

```python
@emitter.on('error')
async def log_errors(error):
    print(f"Application error: {error}")

@app.get("/risky")
async def risky_operation(req, res):
    try:
        # Risky operation
    except Exception as e:
        await emitter.emit('error', str(e))
        return res.status(500).json({"error": str(e)})
```

## Performance Optimization

### Batch Event Processing

```python
async def process_batch(batch_data):
    await asyncio.gather(
        emitter.emit('item_processed', batch_data[0]),
        emitter.emit('item_processed', batch_data[1]),
        emitter.emit('batch_progress', len(batch_data))
    )
```

### Event Throttling

```python
from collections import deque
from typing import Deque

message_queue: Deque[str] = deque(maxlen=100)

@emitter.on('chat_message')
async def throttle_chat(message):
    message_queue.append(message)
    if len(message_queue) >= 100:
        await bulk_process_messages(list(message_queue))
        message_queue.clear()
```

## Best Practices

1. **Namespace Events**: Use clear naming conventions
   ```python
   # Instead of:
   emitter.on('user_created')
   
   # Prefer:
   emitter.on('users:created')
   ```

2. **Keep Listeners Focused**: Each listener should do one thing
   ```python
   @emitter.on('order:placed')
   async def update_inventory(order):
       pass
   
   @emitter.on('order:placed')
   async def send_confirmation(order):
       pass
   ```

3. **Error Handling**: Always handle errors in listeners
   ```python
   @emitter.on('payment:processed')
   async def log_payment(payment):
       try:
           await database.log(payment)
       except Exception as e:
           await emitter.emit('error', f"Payment logging failed: {e}")
   ```

4. **Use Weak References** for listeners that might be garbage collected
   ```python
   @emitter.on('system:alert', weak_ref=True)
   async def handle_alert(alert):
       pass
   ```

## Complete Example

```python
from nexios import get_application, Request, Response
from nexios.events import AsyncEventEmitter
from pydantic import BaseModel

app = get_application()
emitter = AsyncEventEmitter()

class UserCreate(BaseModel):
    username: str
    email: str

# Event listeners
@emitter.on('users:created')
async def send_welcome_email(user):
    print(f"Sending welcome email to {user['email']}")

@emitter.on('users:created')
async def create_user_profile(user):
    print(f"Creating profile for {user['username']}")

# API endpoint
@app.post("/users")
async def create_user(req: Request, res: Response):
    try:
        user_data = UserCreate(**await req.json())
        # Save user to database...
        await emitter.emit('users:created', user_data.dict())
        return res.json({"status": "success"})
    except Exception as e:
        await emitter.emit('system:error', str(e))
        return res.status(400).json({"error": str(e)})

# Error handling
@emitter.on('system:error')
async def log_errors(error):
    print(f"ERROR: {error}")
```

This integrated event system provides a powerful way to build decoupled, maintainable applications within the Nexios framework while leveraging its asynchronous capabilities.
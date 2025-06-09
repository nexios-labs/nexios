# Day 24: Performance Optimization

## Learning Objectives
- Optimize Nexios application performance
- Implement efficient request handling
- Manage WebSocket connections effectively
- Use Nexios's concurrency utilities
- Configure server settings for performance



## Concurrency Optimization

Using Nexios's concurrency utilities:

```python
from nexios.utils.concurrency import (
    TaskGroup,
    create_background_task,
    run_in_threadpool,
    AsyncEvent,
    AsyncLazy
)
import asyncio

# Task group for managing multiple operations
async def process_data(items: list):
    async with TaskGroup() as group:
        for item in items:
            await group.spawn(process_item(item))

# Background task for long-running operations
async def cleanup_expired_data():
    while True:
        await delete_old_records()
        await asyncio.sleep(3600)  # Run hourly

cleanup_task = create_background_task(cleanup_expired_data())

# CPU-bound operations in thread pool
async def process_image(image_data: bytes):
    return await run_in_threadpool(
        cpu_intensive_image_processing,
        image_data
    )

# Event coordination
data_ready = AsyncEvent()
async def wait_for_data():
    await data_ready.wait()
    return "Data available"

# Lazy computation
heavy_computation = AsyncLazy(
    lambda: perform_expensive_calculation()
)
```

## WebSocket Optimization

Efficient WebSocket handling:

```python
from nexios.websockets import WebSocketConsumer
from nexios.websockets.channels import Channel, ChannelBox

class OptimizedWebSocketConsumer(WebSocketConsumer):
    encoding = "json"
    
    async def on_connect(self, websocket):
        await websocket.accept()
        
        # Configure channel with appropriate TTL
        self.channel = Channel(
            websocket=websocket,
            expires=3600,
            payload_type="json"
        )
        
        # Join channel group efficiently
        await ChannelBox.add_channel_to_group(
            self.channel,
            group_name="active_users"
        )
    
    async def on_receive(self, websocket, data):
        # Use broadcast for efficient message distribution
        await self.broadcast(
            payload=data,
            group_name="active_users",
            save_history=False  # Don't save transient messages
        )
    
    async def on_disconnect(self, websocket, close_code):
        # Clean up resources
        if self.channel:
            await ChannelBox.remove_channel_from_group(
                self.channel,
                "active_users"
            )
```

## Request Handling Optimization

Optimizing request processing:

```python
from nexios.http import Request, Response
from nexios.middleware import Middleware
from nexios.types import ASGIApp, Receive, Scope, Send
import gzip
import json

class CompressionMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            accepts_gzip = b"gzip" in headers.get(b"accept-encoding", b"")
            
            async def compressed_send(message):
                if (
                    message["type"] == "http.response.body" and
                    accepts_gzip and
                    message.get("body")
                ):
                    # Compress response body
                    compressed = gzip.compress(message["body"])
                    await send({
                        "type": "http.response.body",
                        "body": compressed,
                        "headers": [
                            (b"content-encoding", b"gzip"),
                            (b"content-length", str(len(compressed)).encode())
                        ]
                    })
                else:
                    await send(message)
            
            await self.app(scope, receive, compressed_send)
        else:
            await self.app(scope, receive, send)

# Add compression middleware
app.add_middleware(CompressionMiddleware)

# Optimize response streaming
@app.get("/stream")
async def stream_data(request: Request, response: Response):
    async def generate():
        for i in range(1000):
            yield json.dumps({"count": i}) + "\n"
    
    return response.stream(
        generate(),
        media_type="application/x-ndjson"
    )
```

## Memory Management

Efficient memory usage:

```python
from nexios.websockets.channels import ChannelBox
import gc
import asyncio

# Periodic cleanup of expired channels
async def cleanup_channels():
    while True:
        # Remove expired channels
        groups = await ChannelBox.show_groups()
        for group_name, channels in groups.items():
            for channel in channels:
                if await channel._is_expired():
                    await ChannelBox.remove_channel_from_group(
                        channel,
                        group_name
                    )
        
        # Clear message history
        if sys.getsizeof(ChannelBox.CHANNEL_GROUPS_HISTORY) > ChannelBox.HISTORY_SIZE:
            ChannelBox.CHANNEL_GROUPS_HISTORY = {}
        
        # Force garbage collection
        gc.collect()
        await asyncio.sleep(300)  # Run every 5 minutes

# Start cleanup task
@app.on_startup
async def start_cleanup():
    asyncio.create_task(cleanup_channels())
```

## Best Practices

1. Server Configuration:
   - Use multiple workers
   - Enable HTTP/2
   - Configure appropriate timeouts
   - Monitor resource usage

2. WebSocket Optimization:
   - Implement channel expiration
   - Use efficient message broadcasting
   - Clean up unused channels
   - Limit message history size

3. Request Handling:
   - Enable compression
   - Use streaming responses
   - Implement caching
   - Optimize payload sizes

4. Memory Management:
   - Regular cleanup tasks
   - Monitor memory usage
   - Implement resource limits
   - Use garbage collection

## 📝 Practice Exercise

1. Optimize a Nexios application:
   - Configure for maximum performance
   - Implement efficient WebSocket handling
   - Add response compression
   - Monitor and optimize memory usage

2. Create performance tests:
   - Measure request latency
   - Test WebSocket throughput
   - Monitor memory consumption
   - Profile CPU usage
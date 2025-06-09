# Day 23: Logging & Monitoring

## Learning Objectives
- Master Nexios's logging system
- Implement custom logging handlers
- Configure logging levels and formats
- Add request/response logging
- Monitor WebSocket connections

## Logging Setup

Configuring Nexios's logging system:

```python
from nexios import NexiosApp
from nexios.logging import create_logger, DEBUG, INFO, ERROR
import logging.handlers
import sys

# Create application logger
logger = create_logger(
    logger_name="myapp",
    log_level=DEBUG,
    log_file="app.log",
    max_bytes=10 * 1024 * 1024,  # 10MB
    backup_count=5
)

app = NexiosApp()

# Add console handler with custom format
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setFormatter(
    logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
)
logger.addHandler(console_handler)
```

## Request Logging

Implementing request logging middleware:

```python
from nexios.middleware import Middleware
from nexios.types import ASGIApp, Receive, Scope, Send
import time

class RequestLoggingMiddleware:
    def __init__(self, app: ASGIApp, logger=None):
        self.app = app
        self.logger = logger or create_logger("request_logger")

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            start_time = time.time()
            
            # Log request
            self.logger.info(
                f"Request: {scope['method']} {scope['path']} "
                f"[{scope.get('client', ('Unknown', 0))[0]}]"
            )
            
            # Wrap send to capture response
            async def wrapped_send(message):
                if message["type"] == "http.response.start":
                    duration = time.time() - start_time
                    status = message["status"]
                    self.logger.info(
                        f"Response: {status} - {duration:.2f}s"
                    )
                await send(message)
            
            await self.app(scope, receive, wrapped_send)
        else:
            await self.app(scope, receive, send)

# Add middleware to app
app.add_middleware(RequestLoggingMiddleware)
```

## WebSocket Logging

Logging WebSocket events:

```python
from nexios.websockets import WebSocketConsumer
from nexios.websockets.channels import Channel, ChannelBox

class LoggedWebSocketConsumer(WebSocketConsumer):
    def __init__(self):
        super().__init__(logging_enabled=True)
    
    async def on_connect(self, websocket):
        """Log connection events"""
        client = websocket.scope.get("client", ("Unknown", 0))[0]
        self.logger.info(f"WebSocket connected: {client}")
        await websocket.accept()
        
        # Create and log channel
        self.channel = Channel(
            websocket=websocket,
            payload_type="json",
            expires=3600
        )
        self.logger.info(
            f"Channel created: {self.channel.uuid} "
            f"[expires={self.channel.expires}s]"
        )
    
    async def on_receive(self, websocket, data):
        """Log received messages"""
        self.logger.debug(
            f"Message received on channel {self.channel.uuid}: "
            f"{str(data)[:100]}..."
        )
        await self.handle_message(data)
    
    async def on_disconnect(self, websocket, close_code):
        """Log disconnection"""
        self.logger.info(
            f"WebSocket disconnected: {close_code} "
            f"[channel={self.channel.uuid}]"
        )

# Register consumer
app.add_route("/ws", LoggedWebSocketConsumer.as_route("/ws"))
```

## Error Logging

Configuring error logging:

```python
from nexios.exceptions import HTTPException
from nexios.http import Request, Response
import traceback

@app.exception_handler(Exception)
async def log_exception(request: Request, exc: Exception):
    """Log unhandled exceptions"""
    error_id = str(uuid.uuid4())
    logger.error(
        f"Unhandled exception [{error_id}]: {str(exc)}\n"
        f"Path: {request.url.path}\n"
        f"Method: {request.method}\n"
        f"Traceback:\n{traceback.format_exc()}"
    )
    
    if isinstance(exc, HTTPException):
        return Response(
            {"error": str(exc), "id": error_id},
            status_code=exc.status_code
        )
    
    return Response(
        {"error": "Internal Server Error", "id": error_id},
        status_code=500
    )
```

## Performance Monitoring

Using hooks for performance monitoring:

```python
from nexios.hooks import before_request, after_request
from statistics import mean
import time

# Store request timings
request_times = []

@before_request(None, log_level="DEBUG")
async def start_timer(request: Request, response: Response):
    request.state.start_time = time.time()

@after_request(None, log_level="DEBUG")
async def log_timing(request: Request, response: Response):
    duration = time.time() - request.state.start_time
    request_times.append(duration)
    
    # Log performance metrics
    logger.debug(
        f"Request completed in {duration:.3f}s "
        f"[avg={mean(request_times[-100:]):.3f}s]"
    )
```

## Channel Monitoring

Monitoring WebSocket channels:

```python
async def monitor_channels():
    """Monitor active channels and groups"""
    while True:
        groups = await ChannelBox.show_groups()
        
        for group_name, channels in groups.items():
            # Log group statistics
            logger.info(
                f"Channel group '{group_name}': "
                f"{len(channels)} active channels"
            )
            
            # Check for expired channels
            for channel in channels:
                if await channel._is_expired():
                    logger.warning(
                        f"Expired channel detected: {channel.uuid} "
                        f"in group '{group_name}'"
                    )
        
        # Log history stats
        history = await ChannelBox.show_history()
        logger.info(
            f"Message history size: "
            f"{sum(len(h) for h in history.values())} messages"
        )
        
        await asyncio.sleep(60)  # Check every minute

# Start monitoring task
@app.on_event("startup")
async def start_monitoring():
    asyncio.create_task(monitor_channels())
```

## Best Practices

1. Logging Configuration:
   - Use appropriate log levels
   - Implement log rotation
   - Include contextual information
   - Format logs for readability

2. Performance Monitoring:
   - Track request durations
   - Monitor resource usage
   - Set up alerts for anomalies
   - Keep historical metrics

3. Security Logging:
   - Log authentication attempts
   - Track suspicious activities
   - Maintain audit trails
   - Protect sensitive data

## 📝 Practice Exercise

1. Implement advanced logging:
   - Custom log formatters
   - Multiple log handlers
   - Structured logging
   - Log aggregation

2. Create monitoring tools:
   - Request timing dashboard
   - WebSocket connection monitor
   - Error rate tracker
   - Performance metrics collector 
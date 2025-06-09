# Day 28: Project: Production-Ready API

## Learning Objectives
- Build a complete production-ready API
- Implement all Nexios best practices
- Set up comprehensive monitoring
- Handle errors and edge cases
- Secure the application

## Project Structure

Setting up a production API:

```python
from nexios import NexiosApp
from nexios.auth import auth
from nexios.http import Request, Response
from nexios.websockets import WebSocketConsumer
from nexios.logging import create_logger
from nexios.middleware import CORSMiddleware
from nexios.exceptions import HTTPException
import jwt
import logging
import os
from nexios.config import MakeConfig
config = MakeConfig(cors =  {
     "allow_origins" : os.getenv("ALLOWED_ORIGINS", "").split(","),
    "allow_methods":["GET", "POST", "PUT", "DELETE"],
    "allow_headers":["Authorization", "Content-Type"],
    "allow_credentials":True,
})
# Application setup
app = NexiosApp()

# Configure logging
logger = create_logger(
    logger_name="production_api",
    log_level=logging.INFO,
    log_file="api.log",
    max_bytes=10 * 1024 * 1024,
    backup_count=5
)

# Security middleware
app.add_middleware(
    CORSMiddleware()
)
```

## Authentication System

Implementing secure authentication:

```python
# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

class AuthenticationError(HTTPException):
    status_code = 401

@app.post("/auth/login")
async def login(request: Request, response: Response):
    data = await request.json
    
    try:
        # Validate credentials
        user = await validate_credentials(
            data.get("username"),
            data.get("password")
        )
        
        # Generate token
        token = jwt.encode(
            {"user_id": user.id, "username": user.username},
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )
        
        return response.json({"token": token})
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise AuthenticationError("Invalid credentials")

async def authenticate(request: Request, response, call_next):
    try:
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM]
            )
            request.scope["user"] = payload
        return await call_next(request)
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise AuthenticationError("Invalid token")

app.add_middleware(authenticate)
```

## API Routes

Implementing secure API endpoints:

```python
@app.get("/api/users")
@auth(["jwt"])
async def list_users(request: Request, response: Response):
    try:
        users = await get_users()
        return response.json({
            "users": [user.to_dict() for user in users]
        })
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        return Response(
            {"error": "Failed to fetch users"},
            status_code=500
        )

@app.post("/api/users")
@auth(["jwt"])
async def create_user(request: Request, response: Response):
    try:
        data = await request.json
        user = await create_new_user(data)
        
        logger.info(f"User created: {user.id}")
        return Response(
            user.to_dict(),
            status_code=201
        )
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        return Response(
            {"error": str(e)},
            status_code=400
        )
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return Response(
            {"error": "Failed to create user"},
            status_code=500
        )
```

## WebSocket Integration

Real-time updates with WebSockets:

```python
class NotificationConsumer(WebSocketConsumer):
    encoding = "json"
    
    async def on_connect(self, websocket):
        # Verify authentication
        try:
            token = websocket.headers.get("Authorization", "").split(" ")[1]
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM]
            )
            websocket.scope["user"] = payload
        except Exception:
            await websocket.close(code=4001)
            return
        
        await websocket.accept()
        
        # Set up notification channel
        user_id = payload["user_id"]
        self.channel = Channel(
            websocket=websocket,
            payload_type="json",
            expires=3600
        )
        await ChannelBox.add_channel_to_group(
            self.channel,
            f"notifications_{user_id}"
        )
    
    async def on_disconnect(self, websocket, close_code):
        if self.channel:
            user_id = websocket.scope["user"]["user_id"]
            await ChannelBox.remove_channel_from_group(
                self.channel,
                f"notifications_{user_id}"
            )

# Register WebSocket route
app.add_route(
    "/ws/notifications",
    NotificationConsumer.as_route("/ws/notifications")
)
```

## Error Handling

Comprehensive error handling:

```python
@app.add_exception_handler(Exception)
async def handle_error(request: Request,response :Response,  exc: Exception):
    error_id = str(uuid.uuid4())
    
    # Log error details
    logger.error(
        f"Error ID: {error_id}\n"
        f"Type: {type(exc).__name__}\n"
        f"Message: {str(exc)}\n"
        f"Path: {request.url.path}\n"
        f"Method: {request.method}\n"
        f"Traceback:\n{traceback.format_exc()}"
    )
    
    # Return appropriate response
    if isinstance(exc, HTTPException):
        return Response(
            {"error": str(exc), "error_id": error_id},
            status_code=exc.status_code
        )
    
    return response.json(
        {
            "error": "Internal server error",
            "error_id": error_id
        },
        status_code=500
    )
```

## Monitoring

Health and monitoring endpoints:

```python
@app.get("/health")
async def health_check(request: Request, response: Response):
    # Check system health
    uptime = time.time() - app.state.startup_time
    
    # Check WebSocket connections
    groups = await ChannelBox.show_groups()
    total_connections = sum(
        len(channels) for channels in groups.values()
    )
    
    return response.json({
        "status": "healthy",
        "uptime": uptime,
        "connections": total_connections,
        "version": "1.0.0"
    })

@app.get("/metrics")
@auth(["jwt"])
async def metrics(request: Request, response: Response):
    # Collect system metrics
    metrics = {
        "requests": app.state.request_count,
        "errors": app.state.error_count,
        "websocket_connections": len(
            await ChannelBox.show_groups()
        ),
        "memory_usage": psutil.Process().memory_info().rss,
        "cpu_usage": psutil.Process().cpu_percent()
    }
    
    return response.json(metrics)
```

## Application Lifecycle

Managing application lifecycle:

```python
@app.on_startup
async def startup():
    # Initialize application state
    app.state.startup_time = time.time()
    app.state.request_count = 0
    app.state.error_count = 0
    
    # Start background tasks
    app.state.cleanup_task = asyncio.create_task(
        cleanup_expired_sessions()
    )
    
    logger.info("Application started")

@app.on_shutdown
async def shutdown():
    # Cancel background tasks
    if hasattr(app.state, "cleanup_task"):
        app.state.cleanup_task.cancel()
        try:
            await app.state.cleanup_task
        except asyncio.CancelledError:
            pass
    
    # Close WebSocket connections
    await ChannelBox.close_all_connections()
    
    logger.info("Application shutdown complete")
```

## Best Practices

1. Security:
   - Implement proper authentication
   - Validate all input
   - Use secure headers
   - Handle errors safely

2. Monitoring:
   - Implement health checks
   - Track metrics
   - Set up comprehensive logging
   - Monitor WebSocket connections

3. Performance:
   - Use connection pooling
   - Implement caching
   - Handle cleanup tasks
   - Manage resources efficiently

4. Reliability:
   - Handle all edge cases
   - Implement proper validation
   - Manage application lifecycle
   - Set up proper error handling

## 📝 Practice Exercise

1. Extend the API:
   - Add more endpoints
   - Implement rate limiting
   - Add data validation
   - Set up caching

2. Enhance monitoring:
   - Add custom metrics
   - Implement logging
   - Set up alerts
   - Create admin dashboard 
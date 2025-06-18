# Application API Reference

The Application API in Nexios provides the core functionality for creating and configuring web applications. The `NexiosApp` class is the main entry point for building Nexios applications.

## Creating an Application

```python
from nexios import NexiosApp, MakeConfig

app = NexiosApp(
    config=MakeConfig({"debug": True}),
    title="My API",
    version="1.0.0",
    description="My awesome API"
)
```

### Configuration

The `MakeConfig` class allows you to configure your application.

```python
config = MakeConfig({
    "debug": True,
    "host": "0.0.0.0",
    "port": 8000,
    "reload": True,
    "workers": 4,
    "openapi": {
        "title": "My API",
        "version": "1.0.0",
        "description": "My awesome API",
        "swagger_url": "/docs",
        "redoc_url": "/redoc",
        "openapi_url": "/openapi.json"
    }
})

app = NexiosApp(config=config)
```

## Application Methods

### Route Registration

#### `@app.get(path, ...)`, `@app.post(path, ...)`, etc.

Register HTTP method handlers.

```python
@app.get("/users")
async def list_users(request, response):
    users = await get_users()
    return response.json({"users": users})

@app.post("/users")
async def create_user(request, response):
    data = await request.json()
    user = await create_user_in_db(data)
    return response.status(201).json({"user": user})
```

#### `@app.route(path, methods=[...], ...)`

Register a handler for multiple HTTP methods.

```python
@app.route("/users", methods=["GET", "POST"])
async def users(request, response):
    if request.method == "GET":
        return response.json({"users": await get_users()})
    elif request.method == "POST":
        data = await request.json()
        user = await create_user_in_db(data)
        return response.status(201).json({"user": user})
```

### WebSocket Routes

#### `@app.ws_route(path, ...)`

Register WebSocket handlers.

```python
@app.ws_route("/ws")
async def websocket_handler(websocket):
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except Exception:
        await websocket.close()
```

### Middleware

#### `app.add_middleware(middleware, **options)`

Add middleware to the application.

```python
from nexios.middleware import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
```

### Event Handlers

#### `@app.on_startup(handler)`

Register startup event handlers.

```python
@app.on_startup
async def startup():
    await database.connect()
    await cache.connect()
```

#### `@app.on_shutdown(handler)`

Register shutdown event handlers.

```python
@app.on_shutdown
async def shutdown():
    await database.disconnect()
    await cache.disconnect()
```

### Exception Handlers

#### `@app.exception_handler(exception_class)`

Register exception handlers.

```python
@app.exception_handler(404)
async def not_found(request, response, exc):
    return response.status(404).json({"error": "Not found"})

@app.exception_handler(500)
async def server_error(request, response, exc):
    return response.status(500).json({"error": "Internal server error"})
```

### OpenAPI Documentation

The application automatically generates OpenAPI documentation.

```python
app = NexiosApp(
    title="My API",
    version="1.0.0",
    description="My awesome API",
    openapi_config={
        "swagger_url": "/docs",
        "redoc_url": "/redoc",
        "openapi_url": "/openapi.json"
    }
)
```

## Application Properties

### `app.router`

Access the application's router.

```python
# Add routes to the router
app.router.add_route("/users", list_users, methods=["GET"])
```

### `app.events`

Access the application's event emitter.

```python
# Emit custom events
app.events.emit("user_created", user)
```

### `app.docs`

Access the OpenAPI documentation.

```python
# Add custom documentation
app.docs.add_security_scheme(
    "bearerAuth",
    HTTPBearer(type="http", scheme="bearer", bearerFormat="JWT")
)
```

## Application Lifecycle

### Startup

The application startup process:

1. Initialize configuration
2. Set up logging
3. Connect to databases
4. Initialize caches
5. Load plugins
6. Start background tasks

```python
@app.on_startup
async def startup():
    # Initialize database
    await database.connect()
    
    # Initialize cache
    await cache.connect()
    
    # Load plugins
    await load_plugins()
    
    # Start background tasks
    app.add_background_task(cleanup_old_sessions)
```

### Shutdown

The application shutdown process:

1. Stop background tasks
2. Close database connections
3. Clear caches
4. Unload plugins
5. Close file handles
6. Clean up resources

```python
@app.on_shutdown
async def shutdown():
    # Stop background tasks
    for task in app.background_tasks:
        task.cancel()
    
    # Close database connection
    await database.disconnect()
    
    # Clear cache
    await cache.clear()
    
    # Unload plugins
    await unload_plugins()
```

## Best Practices

1. **Configuration Management**: Use environment variables for sensitive configuration.

```python
import os

config = MakeConfig({
    "debug": os.getenv("DEBUG", "False").lower() == "true",
    "database_url": os.getenv("DATABASE_URL"),
    "secret_key": os.getenv("SECRET_KEY")
})
```

2. **Error Handling**: Implement comprehensive error handling.

```python
@app.exception_handler(Exception)
async def global_exception_handler(request, response, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return response.status(500).json({
        "error": "Internal server error",
        "detail": str(exc) if app.debug else None
    })
```

3. **Logging**: Set up proper logging.

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("app")
```

4. **Security**: Implement security best practices.

```python
# Add security middleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(CORSMiddleware)
app.add_middleware(CSRFMiddleware)
```

5. **Testing**: Write comprehensive tests.

```python
from nexios.testing import TestClient

client = TestClient(app)

def test_list_users():
    response = client.get("/users")
    assert response.status_code == 200
    assert "users" in response.json()
```

6. **Documentation**: Keep documentation up to date.

```python
@app.get("/users", summary="List users", description="Get a list of all users")
async def list_users(request, response):
    users = await get_users()
    return response.json({"users": users})
```

7. **Performance**: Optimize application performance.

```python
# Enable response compression
app.add_middleware(CompressionMiddleware)

# Enable response caching
app.add_middleware(CacheMiddleware)

# Enable rate limiting
app.add_middleware(RateLimitMiddleware)
```
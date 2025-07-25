# Core Concepts

This guide explains the core concepts and architecture of the Nexios framework.

## Framework Architecture

```mermaid
graph TD
    A["Client Request"] --> B["Router Layer"]
    B --> C["Middleware Chain"]
    C --> D["Route Handler"]
    D --> E["Response"]
    D --> F["Database"]
    D --> G["External Services"]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#bbf,stroke:#333,stroke-width:2px
```

## Key Components

### 1. Router
The router is responsible for URL pattern matching and request routing. Nexios uses a tree-based router for efficient routing:

```python
from nexios import NexiosApp

app = NexiosApp()

@app.get("/users/{user_id}")
async def get_user(request, response):
    user_id = request.path_params.user_id
    return response.json({"user_id": user_id})
```

### 2. Middleware
Middleware provides a way to process requests/responses before/after they reach route handlers:

```python
from nexios import Middleware
from nexios.exceptions import HTTPException

class AuthMiddleware(Middleware):
    async def process_request(self, request):
        token = request.headers.get("Authorization")
        if not token:
            raise HTTPException(401, "Authorization token required")
        request.user = await validate_token(token)
```

### 3. Request Lifecycle

```mermaid
sequenceDiagram
    participant Client
    participant Router
    participant Middleware
    participant Handler
    participant Database
    
    Client->>Router: HTTP Request
    Router->>Middleware: Process Request
    Middleware->>Handler: Handled Request
    Handler->>Database: Query Data
    Database-->>Handler: Return Data
    Handler-->>Client: HTTP Response
```

### 4. Database Integration
Nexios provides built-in database support with async drivers:

```python
from nexios.db import Database

db = Database("postgresql://user:pass@localhost/db")

async def get_users():
    return await db.fetch_all("SELECT * FROM users")
```

## Security Best Practices

::: warning
Always validate and sanitize user inputs to prevent injection attacks:
```python
from nexios.validation import validate_input

@app.post("/users")
async def create_user(request, response):
    data = await validate_input(await request.json, UserSchema)
    # Proceed with validated data
    return response.json({"status": "success", "data": data})
```
:::

## WebSocket Support

Nexios provides first-class WebSocket support:

```python
@app.ws_route("/ws")
async def websocket_endpoint(websocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            await websocket.send_json({"message": "Received"})
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
```

## Authentication

::: tip
Nexios supports multiple authentication methods:
- Session-based authentication
- JWT authentication
- OAuth2 integration
:::

```python
from nexios.auth.backends.jwt import JWTAuthBackend
from nexios.auth.middleware import AuthenticationMiddleware

# Setup JWT authentication
async def get_user_from_payload(**payload):
    # Your user lookup logic here
    return {"username": payload.get("sub")}

jwt_backend = JWTAuthBackend(authenticate_func=get_user_from_payload)
auth_middleware = AuthenticationMiddleware(backend=jwt_backend)

@app.get("/protected")
async def protected_route(request, response):
    user = request.user  # Authenticated user
    return response.json({"message": f"Hello {user.username}"})
```

## Performance Optimization

- Built-in caching support
- Async I/O operations
- Connection pooling
- Request queuing

## Error Handling

```python
from nexios.exceptions import HTTPException

@app.exception_handler(404)
async def not_found(request, response, exc):
    return response.json({"error": "Resource not found"}, status_code=404)

@app.exception_handler(Exception)
async def server_error(request, response, exc):
    # Log the error
    import logging
    logging.error(f"Server error: {exc}")
    return response.json({"error": "Internal server error"}, status_code=500)
```

## Testing

Nexios includes a test client for easy testing:

```python
from nexios.testing import TestClient

async def test_endpoint():
    client = TestClient(app)
    response = await client.get("/api/users")
    assert response.status_code == 200
```

## Deployment

::: tip Best Practices
- Use ASGI servers (Uvicorn/Hypercorn)
- Implement health checks
- Set up monitoring
- Use environment variables for configuration
:::

## Next Steps

- [API Examples](./api-examples.md)
- [Markdown Examples](./markdown-examples.md)
- [Documentation Guide](./docs.md)
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
from nexios import Router

router = Router()

@router.get("/users/{user_id}")
async def get_user(request):
    user_id = request.path_params["user_id"]
    return {"user_id": user_id}
```

### 2. Middleware
Middleware provides a way to process requests/responses before/after they reach route handlers:

```python
from nexios import Middleware

class AuthMiddleware(Middleware):
    async def process_request(self, request):
        token = request.headers.get("Authorization")
        if not token:
            raise UnauthorizedError()
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

@router.post("/users")
async def create_user(request):
    data = await validate_input(request.json(), UserSchema)
    # Proceed with validated data
```
:::

## WebSocket Support

Nexios provides first-class WebSocket support:

```python
@router.websocket("/ws")
async def websocket_endpoint(websocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        await websocket.send_json({"message": "Received"})
```

## Authentication

::: tip
Nexios supports multiple authentication methods:
- Session-based authentication
- JWT authentication
- OAuth2 integration
:::

```python
from nexios.auth import JWTAuth

auth = JWTAuth(secret_key="your-secret")

@router.get("/protected")
@auth.required()
async def protected_route(request):
    user = request.user  # Authenticated user
    return {"message": f"Hello {user.username}"}
```

## Performance Optimization

- Built-in caching support
- Async I/O operations
- Connection pooling
- Request queuing

## Error Handling

```python
from nexios.exceptions import HTTPException

@router.exception_handler(404)
async def not_found(request, exc):
    return {"error": "Resource not found"}, 404

@router.exception_handler(Exception)
async def server_error(request, exc):
    # Log the error
    return {"error": "Internal server error"}, 500
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

- [API Examples](/api-examples)
- [Markdown Examples](/markdown-examples)
- [Documentation Guide](/docs)
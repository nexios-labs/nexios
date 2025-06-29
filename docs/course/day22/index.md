# Day 22: Testing Strategies

## Learning Objectives
- Master Nexios's testing utilities
- Write effective test cases using pytest
- Implement test fixtures for Nexios apps
- Test WebSocket and HTTP endpoints

## Testing Setup

Setting up your testing environment:

```python
from nexios import NexiosApp
from nexios.testing import Client
from nexios.http import Request, Response
import pytest

app = NexiosApp()

@app.get("/hello")
async def hello(request: Request, response: Response):
    return response.text("Hello, World!")

@pytest.fixture
async def async_client():
    async with Client(app) as client:
        yield client
```

## Testing HTTP Endpoints

Testing basic HTTP endpoints:

```python
async def test_hello_endpoint(async_client: Client):
    response = await async_client.get("/hello")
    assert response.status_code == 200
    assert response.text == "Hello, World!"

async def test_not_found(async_client: Client):
    response = await async_client.get("/nonexistent")
    assert response.status_code == 404

async def test_method_not_allowed(async_client: Client):
    response = await async_client.post("/hello")
    assert response.status_code == 405
```

## Testing Route Parameters

Testing routes with parameters:

```python
@app.get("/users/{user_id}")
async def get_user(request: Request, response: Response):
    user_id = request.path_params.user_id
    return response.json({"id": user_id, "name": f"User {user_id}"})

async def test_route_params(async_client: Client):
    response = await async_client.get("/users/123")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "123"
    assert data["name"] == "User 123"
```

## Testing Authentication

Testing authenticated endpoints:

```python
from nexios.auth import auth

@app.get("/protected")
@auth(["jwt"])
async def protected_route(request: Request, response: Response):
    return response.json({"message": "Access granted"})

async def test_protected_route_unauthorized(async_client: Client):
    response = await async_client.get("/protected")
    assert response.status_code == 401

async def test_protected_route_authorized(async_client: Client):
    # Add auth token to headers
    headers = {"Authorization": "Bearer test_token"}
    response = await async_client.get("/protected", headers=headers)
    assert response.status_code == 200
```

## Testing WebSockets

Testing WebSocket endpoints:

```python
from nexios.websockets import WebSocket

@app.ws_route("/ws/echo")
async def websocket_echo(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_text(f"Echo: {message}")
    except Exception:
        await websocket.close()

async def test_websocket_echo(async_client: Client):
    async with async_client.websocket_connect("/ws/echo") as websocket:
        await websocket.send_text("Hello")
        response = await websocket.receive_text()
        assert response == "Echo: Hello"
```

## Testing Middleware

Testing custom middleware:

```python
from nexios.middleware import Middleware
from nexios.types import ASGIApp, Receive, Scope, Send

class CustomHeaderMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            scope["custom_header"] = "test_value"
        await self.app(scope, receive, send)

app.add_middleware(CustomHeaderMiddleware)

async def test_middleware(async_client: Client):
    response = await async_client.get("/hello")
    assert response.status_code == 200
    assert "custom_header" in response.headers
```

## Testing Error Handling

Testing error handlers:

```python
from nexios.exceptions import HTTPException

class CustomError(HTTPException):
    status_code = 418

@app.exception_handler(CustomError)
async def custom_error_handler(request: Request, exc: CustomError):
    return Response(
        {"error": "I'm a teapot"},
        status_code=418
    )

@app.get("/error")
async def trigger_error(request: Request, response: Response):
    raise CustomError()

async def test_error_handler(async_client: Client):
    response = await async_client.get("/error")
    assert response.status_code == 418
    data = response.json()
    assert data["error"] == "I'm a teapot"
```

## Best Practices

1. Test Organization:
   - Group related tests in classes
   - Use descriptive test names
   - Separate fixtures by scope

```python
class TestUserAPI:
    @pytest.fixture
    async def user_data(self):
        return {"username": "testuser", "email": "test@example.com"}
    
    async def test_create_user(self, async_client: Client, user_data: dict):
        response = await async_client.post("/users", json=user_data)
        assert response.status_code == 201
    
    async def test_get_user(self, async_client: Client, user_data: dict):
        response = await async_client.get("/users/testuser")
        assert response.status_code == 200
```

2. Async Testing:
   - Use async fixtures
   - Handle cleanup properly
   - Test both success and failure cases

3. Mocking:
   - Mock external services
   - Use dependency injection
   - Test edge cases

## 📝 Practice Exercise

1. Create a test suite for:
   - User registration and authentication
   - File upload endpoints
   - WebSocket chat room
   - Custom middleware
   - Error handlers

2. Implement test fixtures for:
   - Database connections
   - Authentication tokens
   - Test data setup and cleanup
   - WebSocket connections 
---
layout: home

hero:
  name: Nexios
  text: Async Python Web Framework
  tagline: Nexios is a fast, minimalist Python framework for building async APIs with clean architecture, zero boilerplate, and a Pythonic feel.

  image:
    src: /icon.svg
    alt: Nexios
  actions:
    - theme: brand
      text: Get Started
      link: /guide/getting-started
    - theme: alt
      text: View on GitHub
      link: https://github.com/nexios-labs/nexios
    - theme: alt
      text: Why Nexios?
      link: /guide/why-nexios

features:
  - icon: ⚡
    title: Async by Design
    details: |
      Built on ASGI with native async/await support throughout the framework. 
      - High-performance request handling
      - WebSocket support out of the box
      - Connection pooling for databases
      - Event-driven architecture
      Perfect for building real-time applications and APIs.

  - icon: 🎯
    title: Clean Architecture
    details: |
      Modular design with clear separation of concerns:
      - Dependency injection system
      - Middleware pipeline
      - Event hooks and observers
      - Structured error handling
      - Domain-driven design ready

  - icon: 🛠️
    title: Complete Toolkit
    details: |
      Everything you need in one place:
      - Type-safe routing
      - Session management
      - CORS & CSRF protection
      - WebSocket channels
      - File uploads
      - Template engines
      - OpenAPI/Swagger
      - Testing utilities

  - icon: 🔒
    title: Built-in Security
    details: |
      Security-first approach with:
      - JWT authentication
      - Session management
      - CSRF protection
      - Rate limiting
      - Input validation
      - SQL injection prevention
      - XSS protection

  - icon: 📝
    title: Developer Experience
    details: |
      Focus on productivity:
      - Clear error messages
      - Auto-reload in development
      - CLI tools and scaffolding
      - Comprehensive logging
      - Debug toolbar
      - Type hints everywhere
      - IDE integration

  - icon: 🔌
    title: Extensible Design
    details: |
      Build your way:
      - Plugin system
      - Custom middleware
      - Event hooks
      - Authentication backends
      - Template engines
      - Database integrations
---

## Quick Start

::: code-group

```bash [Install]
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install Nexios
pip install nexios
```

```python [Basic App]
from nexios import NexiosApp

app = NexiosApp()

@app.get("/")
async def index(request, response):
    return response.json({
        "message": "Welcome to Nexios!"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

```python [With Config]
from nexios import NexiosApp, MakeConfig

config = MakeConfig({
    "debug": True,
    "cors_enabled": True,
    "allowed_hosts": ["localhost", "example.com"]
})

app = NexiosApp(
    config=config,
    title="My API",
    version="1.0.0"
)
```

:::

::: tip Quick Development
Use `nexios run --reload` for automatic reloading during development.
:::

## Key Features

### Type-Safe Routing

::: code-group

```python [Basic Routes]
from nexios import NexiosApp

app = NexiosApp()

@app.get("/users/{user_id:int}")
async def get_user(request, response):
    user_id = request.path_params.user_id  # Automatically int
    return response.json({"id": user_id})
```

```python [With Validation]
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

@app.post("/users")
async def create_user(request, response):
    data = await request.json
    user = User(**data)  # Automatic validation
    return response.json(user.dict())
```

```python [Advanced Routing]
from nexios import NexiosApp
from uuid import UUID

app = NexiosApp()

@app.get("/users/{user_id:int}/posts/{post_id:uuid}")
async def get_user_post(request, response):
    user_id = request.path_params.user_id
    post_id = request.path_params.post_id
    return response.json({
        "user_id": user_id,
        "post_id": str(post_id)
    })
```

:::

### WebSocket Support

::: code-group

```python [Basic WebSocket]
@app.ws_route("/ws")
async def websocket_endpoint(websocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            await websocket.send_json({"echo": data})
    except WebSocketDisconnect:
        print("Client disconnected")
```

```python [Chat Room]
from nexios.websockets import Channel

@app.ws_route("/chat/{room_id}")
async def chat_room(websocket, room_id: str):
    channel = Channel(f"room:{room_id}")
    await channel.connect(websocket)

    try:
        while True:
            message = await websocket.receive_json()
            await channel.broadcast(message)
    except WebSocketDisconnect:
        await channel.disconnect(websocket)
```

:::

### Middleware System

::: code-group

```python [Basic Middleware]

async def basic_middleware(request, response, call_next):
  print("do something before handler")
  await call_next()
  print("do something after handler")


app.add_middleware(basic_middleware())
```

```python [Class Based Middleware]
from nexios.middleware import BaseMiddleware
class BasicMiddleware(BaseMiddleware):

  async def process_request(request, response, call_next):
    print("do something before handler")
    await call_next()
  async def process_response(request, response, call_next):
    print("do something after handler")

```

```python [Auth Middleware]
from nexios.auth.middleware import AuthenticationMiddleware
from nexios.auth.backends.jwt import JWTAuthBackend
from nexios.auth.decorator import auth

async def get_user_from_payload(**payload):
  ...
auth = AuthenticationMiddleware(
      backend = JWTAuthBackend(
        get_user_from_payload
      )
)

app.add_middleware(auth)

@app.get("/protected")
@auth(["jwt"])
async def protected(request, response):
    user = request.user
    return response.json({"message": f"Hello {user.username}"})
```

:::

### Dependency Injection

::: code-group

```python [Basic DI]
from nexios import Depend

# Both generator and async generator dependencies are supported.
# Cleanup in the finally block is always run after the request.

def get_db():
    db = connect()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    db = await async_connect()
    try:
        yield db
    finally:
        await db.close()

@app.get("/users")
async def list_users(
    request,
    response,
    db=Depend(get_db)  # or db=Depend(get_async_db)
):
    users = await db.query("SELECT * FROM users")
    return response.json(users)
```

```python [With Auth]
async def get_current_user(
    request,
    auth=Depend(get_auth)
):
    token = request.headers.get("Authorization")
    return await auth.get_user(token)

@app.get("/profile")
async def profile(
    request,
    response,
    user=Depend(get_current_user)
):
    return response.json(user.to_dict())
```

:::

::: tip Production Ready
Nexios is built for production use with:

- Comprehensive error handling
- Security best practices
- Performance optimizations
- Monitoring support
  :::

::: warning Python Version
Nexios requires Python 3.9+ for:

- Native async/await
- Type hints
- Modern language features
  :::

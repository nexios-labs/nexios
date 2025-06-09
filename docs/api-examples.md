---
outline: deep
---

# API Examples

This page demonstrates common API patterns and best practices in Nexios.

## REST API Examples

### Basic CRUD Operations

::: code-group
```python [GET]
from nexios import NexiosApp
from nexios.responses import JSONResponse

app = NexiosApp()

@app.get("/items/{item_id:int}")
async def get_item(request, response):
    """Get a single item by ID."""
    item_id = request.path_params.item_id
    return response.json({
        "id": item_id,
        "name": f"Item {item_id}"
    })

@app.get("/items")
async def list_items(request, response):
    """List all items with pagination."""
    page = request.query_params.get("page", 1)
    limit = request.query_params.get("limit", 10)
    return response.json({
        "items": [],
        "page": page,
        "limit": limit
    })
```

```python [POST]
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str = None
    price: float

@app.post("/items")
async def create_item(request, response):
    """Create a new item with validation."""
    data = await request.json()
    item = Item(**data)
    return response.json(item.dict(), status_code=201)
```

```python [PUT/PATCH]
@app.put("/items/{item_id:int}")
async def update_item(request, response):
    """Full update of an item."""
    item_id = request.path_params.item_id
    data = await request.json()
    return response.json({
        "id": item_id,
        **data
    })

@app.patch("/items/{item_id:int}")
async def partial_update(request, response):
    """Partial update of an item."""
    item_id = request.path_params.item_id
    data = await request.json()
    return response.json({
        "id": item_id,
        "updated_fields": list(data.keys())
    })
```

```python [DELETE]
@app.delete("/items/{item_id:int}")
async def delete_item(request, response):
    """Delete an item."""
    item_id = request.path_params.item_id
    return response.json(None, status_code=204)
```
:::

### Authentication Examples

::: code-group
```python [JWT Auth]
from nexios.auth import JWTAuth, AuthenticationError

auth = JWTAuth(secret_key="your-secret")

@app.post("/login")
async def login(request, response):
    data = await request.json()
    if valid_credentials(data):
        token = auth.create_token({"user_id": 123})
        return response.json({"token": token})
    raise AuthenticationError("Invalid credentials")

@app.get("/protected")
@auth.requires_auth
async def protected_route(request, response):
    user = request.user
    return response.json({"message": f"Hello {user.username}"})
```

```python [Session Auth]
from nexios.session import SessionAuth

auth = SessionAuth(secret_key="your-secret")
app.add_middleware(auth.middleware)

@app.post("/login")
async def login(request, response):
    data = await request.json()
    if valid_credentials(data):
        request.session["user_id"] = 123
        return response.json({"message": "Logged in"})
    raise AuthenticationError("Invalid credentials")
```

```python [OAuth]
from nexios.auth import OAuth2Auth

oauth = OAuth2Auth(
    client_id="your-client-id",
    client_secret="your-client-secret",
    authorize_url="https://provider.com/oauth/authorize",
    token_url="https://provider.com/oauth/token"
)

@app.get("/login/oauth")
async def oauth_login(request, response):
    return await oauth.authorize_redirect(request, "/oauth/callback")

@app.get("/oauth/callback")
async def oauth_callback(request, response):
    token = await oauth.get_token(request)
    user = await oauth.get_user_info(token)
    return response.json(user)
```
:::

### File Handling

::: code-group
```python [Upload]
from nexios.files import UploadFile

@app.post("/upload")
async def upload_file(request, response):
    """Handle file upload with validation."""
    file: UploadFile = await request.file("file")
    
    if not file.content_type.startswith("image/"):
        raise ValueError("Only images allowed")
        
    filename = await file.save("uploads/")
    return response.json({
        "filename": filename,
        "size": file.size
    })
```

```python [Download]
from nexios.responses import FileResponse

@app.get("/files/{filename}")
async def download_file(request, response):
    """Stream file download."""
    filename = request.path_params.filename
    return FileResponse(
        f"uploads/{filename}",
        filename=filename,
        content_type="application/octet-stream"
    )
```

```python [Streaming]
from nexios.responses import StreamingResponse

@app.get("/stream")
async def stream_data(request, response):
    """Stream large datasets."""
    async def generate():
        for i in range(100):
            yield f"data: {i}\n\n"
            await asyncio.sleep(0.1)
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```
:::

### WebSocket Examples

::: code-group
```python [Basic Chat]
from nexios.websockets import WebSocket, WebSocketDisconnect

@app.websocket("/ws/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_text(f"Message received: {message}")
    except WebSocketDisconnect:
        print("Client disconnected")
```

```python [Broadcast]
from nexios.websockets import Channel

chat_channel = Channel("chat")

@app.websocket("/ws/chat/{room_id}")
async def chat_room(websocket: WebSocket, room_id: str):
    await chat_channel.connect(websocket)
    try:
        while True:
            message = await websocket.receive_json()
            await chat_channel.broadcast({
                "room": room_id,
                "message": message
            })
    except WebSocketDisconnect:
        await chat_channel.disconnect(websocket)
```

```python [With Auth]
@app.websocket("/ws/secure")
async def secure_ws(
    websocket: WebSocket,
    user=Depend(get_current_user)
):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_json()
            # Only authenticated users can send/receive
            await websocket.send_json({
                "user": user.username,
                "message": message
            })
    except WebSocketDisconnect:
        print(f"User {user.username} disconnected")
```
:::

### Database Integration

::: code-group
```python [SQLAlchemy]
from nexios.db import Database
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
db = Database(engine)

@app.on_startup()
async def startup():
    await db.connect()

@app.on_shutdown()
async def shutdown():
    await db.disconnect()

@app.get("/users")
async def list_users(request, response, db=Depend(get_db)):
    query = "SELECT * FROM users"
    users = await db.fetch_all(query)
    return response.json(users)
```

```python [MongoDB]
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.database

@app.get("/users")
async def list_users(request, response):
    users = await db.users.find().to_list(length=100)
    return response.json(users)

@app.post("/users")
async def create_user(request, response):
    data = await request.json()
    result = await db.users.insert_one(data)
    return response.json({
        "id": str(result.inserted_id)
    })
```

```python [Redis]
import aioredis

redis = aioredis.from_url("redis://localhost")

@app.get("/cache/{key}")
async def get_cached(request, response):
    key = request.path_params.key
    value = await redis.get(key)
    return response.json({
        "key": key,
        "value": value
    })

@app.post("/cache/{key}")
async def set_cached(request, response):
    key = request.path_params.key
    data = await request.json()
    await redis.set(key, str(data), ex=3600)
    return response.json({"status": "ok"})
```
:::

::: tip Best Practices
- Always validate input data
- Use appropriate HTTP status codes
- Implement proper error handling
- Document your APIs
- Use connection pooling for databases
- Implement rate limiting for public APIs
:::

::: warning Security
- Never trust client input
- Always use HTTPS in production
- Implement proper authentication
- Use secure session configuration
- Validate file uploads
- Set appropriate CORS policies
:::

## More Examples

Check out the [examples directory](https://github.com/nexios-labs/nexios/tree/main/examples) in the GitHub repository for more examples and use cases.

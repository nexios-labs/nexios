---
outline: deep
---

# Nexios API Examples

This guide provides canonical, working examples for building APIs with Nexios. All code is idiomatic and matches the Nexios source, docs, and real-world examples.

::: tip Nexios Request API
- Use `await req.json` (not `req.json()`)
- Use `await req.files` (not `req.files()`)
- Use `req.path_params.param` (not `req.path_params['param']`)
:::

## 1. Minimal App and REST API

```python
from nexios import NexiosApp

app = NexiosApp()

@app.get("/api/items")
async def get_items(req, res):
    items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
    return res.json(items)

@app.get("/api/items/{item_id:int}")
async def get_item(req, res):
    item_id = req.path_params.item_id
    return res.json({"id": item_id, "name": f"Item {item_id}"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000, reload=True)
```

## 2. Request Input Handling (JSON Body)

```python
from pydantic import BaseModel, ValidationError
from nexios import NexiosApp

app = NexiosApp()

class User(BaseModel):
    name: str
    age: int

@app.post("/json")
async def process_json(req, res):
    try:
        data = await req.json
        user = User(**data)
        return res.json({"status": "success", "user": user.dict()})
    except ValidationError as e:
        return res.json({"error": str(e)}, status_code=422)
```

## 3. File Upload and Download

```python
from nexios import NexiosApp
from pathlib import Path

app = NexiosApp()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload")
async def upload_files(req, res):
    files = await req.files
    uploaded = []
    for name, file in files.items():
        # Read file content for processing/saving
        file_content = await file.read()
        file_path = UPLOAD_DIR / file.filename
        
        # Save file to disk
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        uploaded.append({
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(file_content),
            "saved_path": str(file_path)
        })
    return res.json({"uploaded": uploaded})

@app.get("/files/{filename}")
async def download_file(req, res):
    filename = req.path_params.filename
    filepath = UPLOAD_DIR / filename
    if not filepath.exists():
        return res.json({"error": "File not found"}, status_code=404)
    from nexios.responses import FileResponse
    return FileResponse(filepath, filename=filename)
```

## 4. Authentication (Session and JWT)

### Session Auth Example
```python
from nexios import NexiosApp
from nexios.auth.backends.session import SessionAuthBackend
from nexios.auth.middleware import AuthenticationMiddleware

app = NexiosApp()

async def get_user_by_id(user_id: int):
    # Replace with your DB lookup
    return {"id": user_id, "username": "user"}

session_backend = SessionAuthBackend(user_key="user_id", authenticate_func=get_user_by_id)
app.add_middleware(AuthenticationMiddleware(backend=session_backend))

@app.get("/protected")
async def protected(req, res):
    user = req.user
    if user and user.is_authenticated:
        return res.json({"message": f"Hello, {user.username}!"})
    return res.json({"error": "Not authenticated"}, status_code=401)
```

### JWT Auth Example
```python
from nexios import NexiosApp
from nexios.auth.backends.jwt import JWTAuthBackend, create_jwt
from nexios.auth.middleware import AuthenticationMiddleware
from nexios.auth.base import BaseUser

class User(BaseUser):
    def __init__(self, id, username):
        self.id = id
        self.username = username
    @property
    def is_authenticated(self):
        return True
    @property
    def identity(self):
        return self.id
    @property
    def display_name(self):
        return self.username

app = NexiosApp()
async def get_user_by_id(**payload):
    return User(id=payload["sub"], username=payload["sub"])
jwt_backend = JWTAuthBackend(authenticate_func=get_user_by_id)
app.add_middleware(AuthenticationMiddleware(backend=jwt_backend))

@app.post("/login")
async def login(req, res):
    data = await req.json
    username = data.get("username")
    password = data.get("password")
    if username == "admin" and password == "password":
        token = create_jwt({"sub": username})
        return res.json({"token": token})
    return res.json({"error": "Invalid credentials"}, status_code=401)

@app.get("/protected")
async def protected(req, res):
    if req.user and req.user.is_authenticated:
        return res.json({"message": f"Hello, {req.user.username}!"})
    return res.json({"error": "Not authenticated"}, status_code=401)
```

## 5. Middleware Usage

```python
from nexios import NexiosApp
from nexios.middleware import CORSMiddleware, SecurityMiddleware

app = NexiosApp()
app.add_middleware(CORSMiddleware())
app.add_middleware(SecurityMiddleware())
```

## 6. Error Handling

```python
from nexios import NexiosApp
from nexios.exceptions import HTTPException

app = NexiosApp()

@app.get("/error")
async def error_route(req, res):
    raise HTTPException(400, "This is a bad request!")

@app.exception_handler(HTTPException)
async def handle_http_exception(req, res, exc):
    return res.json({"error": exc.detail}, status_code=exc.status_code)
```

## 7. WebSockets (Minimal)

```python
from nexios import NexiosApp
from nexios.websockets import WebSocket

app = NexiosApp()

@app.ws_route("/ws")
async def websocket_handler(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_text(f"Echo: {message}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
```

## 8. WebSockets (Chat Room)

```python
from typing import Dict, Set
from nexios import NexiosApp
from nexios.websockets import WebSocket

app = NexiosApp()
chat_rooms: Dict[str, Set[WebSocket]] = {}

@app.ws_route("/ws/chat/{room_id}")
async def chat_room(websocket: WebSocket):
    room_id = websocket.path_params.room_id
    await websocket.accept()
    if room_id not in chat_rooms:
        chat_rooms[room_id] = set()
    chat_rooms[room_id].add(websocket)
    try:
        for client in chat_rooms[room_id]:
            if client != websocket:
                await client.send_json({"type": "system", "message": "New user joined the chat"})
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            for client in chat_rooms[room_id]:
                if client != websocket:
                    await client.send_json({"type": "message", "message": message})
    except Exception as e:
        print(f"WebSocket error in room {room_id}: {e}")
    finally:
        chat_rooms[room_id].remove(websocket)
        if not chat_rooms[room_id]:
            del chat_rooms[room_id]
        await websocket.close()
```

## 9. Advanced Validation (Pydantic, Enums, Query Params)

```python
from datetime import date, datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ValidationError, constr
from nexios import NexiosApp

app = NexiosApp()

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8)
    full_name: str
    birth_date: Optional[date] = None
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE

@app.post("/users")
async def create_user(request, response):
    try:
        data = await request.json
        user = UserCreate(**data)
        return response.json(user.dict())
    except ValidationError as e:
        return response.json({"error": str(e)}, status_code=422)

class PaginationParams(BaseModel):
    page: int = Field(ge=1, default=1)
    limit: int = Field(ge=1, le=100, default=10)
    sort_by: str = Field(default="created_at")
    order: str = Field(default="desc")

@app.get("/users")
async def list_users(request, response):
    try:
        params = PaginationParams(
            page=int(request.query_params.get("page", 1)),
            limit=int(request.query_params.get("limit", 10)),
            sort_by=request.query_params.get("sort_by", "created_at"),
            order=request.query_params.get("order", "desc"),
        )
    except ValidationError as e:
        return response.json({"error": "Invalid query parameters", "details": e.errors()}, status_code=422)
    # Simulate paginated response
    users = [{"id": i, "username": f"user{i}"} for i in range(1, 6)]
    return response.json({"items": users, "total": len(users), "page": params.page, "limit": params.limit})
```

## 10. Advanced Templating (Inheritance, Context, Filters)

```python
from pathlib import Path
from nexios import NexiosApp
from nexios.templating import TemplateConfig, render

app = NexiosApp()
template_config = TemplateConfig(
    template_dir=Path("templates"), trim_blocks=True, lstrip_blocks=True
)
app.config.templating = template_config

@app.get("/")
async def home(request, response):
    return await render(
        "pages/home.html",
        {"title": "Home", "content": "Welcome!", "features": [
            {"name": "Fast", "description": "Built for speed"},
            {"name": "Secure", "description": "Security first"},
        ]},
    )
```

## 11. Advanced Routing (Typed Path Params, Wildcards)

```python
from nexios import NexiosApp
from nexios.http import Request, Response

app = NexiosApp()

@app.get("/products/{product_id:int}")
async def get_product(req: Request, res: Response):
    product_id = req.path_params.product_id
    return res.json({"product_id": product_id, "type": "integer"})

@app.get("/categories/{category_name:str}")
async def get_category(req: Request, res: Response):
    category_name = req.path_params.category_name
    return res.json({"category_name": category_name, "type": "string"})

@app.get("/wildcard/{wildcard_path:path}")
async def get_wildcard(req: Request, res: Response):
    wildcard_path = req.path_params.wildcard_path
    return res.json({"wildcard_path": wildcard_path, "type": "path"})
```

## 12. Custom Response Types

```python
from nexios import NexiosApp
from nexios.http.response import (
    BaseResponse, FileResponse, HTMLResponse, JSONResponse, PlainTextResponse
)

app = NexiosApp()

@app.get("/json")
async def json_handler(req, res):
    return JSONResponse({"message": "Hello, World!"})

@app.get("/html")
async def html_handler(req, res):
    return HTMLResponse("<h1>Hello, World!</h1>")

@app.get("/text")
async def text_handler(req, res):
    return PlainTextResponse("Hello, World!", content_type="text/plain")

@app.get("/file")
async def file_handler(req, res):
    return FileResponse("examples/responses/example_004.py", content_disposition_type="attachment")

@app.get("/raw")
async def raw_handler(req, res):
    return BaseResponse(b"Hello, World!", content_type="text/plain")
```

---

For more, see the official Nexios documentation and the `examples/` folder in the repo. 
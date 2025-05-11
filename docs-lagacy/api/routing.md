

# Routing

#### **1. Initialization**
```python
app = get_application(
    config=MakeConfig(...),       # App configuration
    title="API Title",            # OpenAPI title
    version="1.0",                # API version
    middlewares=[...],            # Global middleware
    server_error_handler=...,     # Custom error handler
    lifespan=lifespan_manager     # Async context manager
)
```

---

### **2. HTTP Routing**
#### **Basic Routes**
```python
# GET
@app.get("/items")
async def get_items(request, response):
    return {"data": [...]}

# POST with validation
@app.post("/items", request_model=ItemModel)
async def create_item(request, response):
    data = request.validated_data  # Pydantic-validated
    return response.json(data, status=201)
```

#### **Route Parameters**
| Param | Description | Example |
|-------|-------------|---------|
| `path` | URL path with `{params}` | `/users/{id:int}` |
| `methods` | HTTP methods | `["GET", "POST"]` |
| `request_model` | Pydantic model | `UserCreate` |
| `responses` | Status-code schemas | `{200: UserSchema, 404: ErrorSchema}` |
| `middlewares` | Route-specific middleware | `[auth_required]` |

---

### **3. WebSocket Routing**
```python
@app.ws_route("/ws/chat")
async def chat_handler(websocket):
    await websocket.accept()
    while True:
        msg = await websocket.receive_text()
        await websocket.send_text(f"Echo: {msg}")
```

#### **WS Methods**
| Method | Description |
|--------|-------------|
| `add_ws_route()` | Register WS route |
| `add_ws_middleware()` | Add WS middleware |
| `mount_ws_router()` | Mount sub-router |

---

### **4. Middleware**
#### **HTTP Middleware**
```python
@app.add_middleware
async def log_middleware(request, response, next_call):
    print(f"Request: {request.method} {request.url}")
    return await next_call(request, response)
```

#### **WS Middleware**
since nexios does not directly support WS middleware, you can add it manually like this:
```python
def ws_auth(app):
   def handle(scope, receive, send):
       return app(scope, receive, send)

   return handle

app.add_ws_middleware(ws_auth)
```

---

### **5. Lifecycle Events**
```python
@app.on_startup
async def init_db():
    await Database.connect()

@app.on_shutdown 
async def cleanup():
    await Database.disconnect()
```

---

### **6. Advanced Features**
#### **URL Generation**
```python
url = app.url_for("route_name", id=123)
```

#### **Exception Handling**
```python
@app.add_exception_handler(404)
async def handle_404(request, exc):
    return JSONResponse({"error": "Not found"}, status_code=404)
```

#### **Sub-Routers**
```python
admin_router = Router(prefix="/admin")
app.mount_router(admin_router)
```


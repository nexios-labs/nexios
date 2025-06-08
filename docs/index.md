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
    - theme: primary
      text: Get Started
      link: /guide/getting-started
    - theme: alt
      text: View on GitHub
      link: https://github.com/nexios-labs/nexios

features:
  - icon: ⚡
    title: Async by Design
    details: Built on ASGI with native async/await support throughout the framework. From request handling to WebSockets and middleware, everything is async-first for maximum performance and scalability. Perfect for building real-time applications and APIs.

  - icon: 🎯 
    title: Clean Architecture
    details: Modular design with clear separation of concerns. Features include dependency injection, middleware system, event hooks, and structured error handling. The codebase follows clean architecture principles making it easy to maintain and extend.

  - icon: 🛠️
    title: Complete Toolkit
    details: Comes with everything you need - routing with type converters, session handling, CORS & CSRF protection, WebSocket channels, file handling, template support, OpenAPI integration, and comprehensive testing utilities.

  - icon: 🔒
    title: Built-in Security
    details: Security-first approach with built-in authentication system, session management, CSRF protection, and secure WebSocket implementation. Easily add custom security middleware and authentication backends.

  - icon: 📝
    title: Developer Experience
    details: Excellent developer experience with clear error messages, automatic OpenAPI documentation, CLI tools, and comprehensive logging. The framework is designed to be intuitive and productive from day one.

  - icon: 🔌
    title: Extensible Design
    details: Highly extensible architecture with hooks system, event handling, custom middleware support, and pluggable components. Build and integrate your own extensions seamlessly.

---

## Getting Started

Install Nexios using pip:

```sh
pip install nexios
```

Create a basic application:

```python
from nexios import NexiosApp

app = NexiosApp()

@app.get("/")
async def index(request, response):
    return response.json({
        "message": "Welcome to Nexios!"
    })

@app.get("/items/{item_id:int}")
async def get_item(request, response):
    item_id = request.path_params.item_id
    return response.json({
        "id": item_id,
        "name": f"Item {item_id}"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

## Key Features

### Type-Safe Routing
```python
@app.get("/users/{user_id:int}/posts/{post_id:uuid}")
async def get_user_post(request, response):
    user_id = request.path_params.user_id  # Automatically converted to int
    post_id = request.path_params.post_id  # Automatically converted to UUID
    return response.json({"user_id": user_id, "post_id": post_id})
```

### WebSocket Support
```python
@app.ws_route("/ws")
async def websocket_endpoint(websocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            await websocket.send_json({"message": f"Received: {data}"})
    except WebSocketDisconnect:
        print("Client disconnected")
```

### Middleware System
```python
from nexios.middleware import BaseMiddleware

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, request, response, call_next):
        print(f"Request to {request.url}")
        response = await call_next()
        print(f"Response status: {response.status_code}")
        return response

app.add_middleware(LoggingMiddleware())
```

### Dependency Injection
```python
from nexios import Depend

async def get_current_user(request):
    user_id = request.headers.get("X-User-Id")
    return await fetch_user(user_id)

@app.get("/profile")
async def profile(request, response, user=Depend(get_current_user)):
    return response.json(user.to_dict())
```



```py [config.js]
from NexiosApp()

app = NexiosApp

@app.get("/")
async def index(request, response):

  return {"message" : "Nexios , Fast Async , Minimal"}
```

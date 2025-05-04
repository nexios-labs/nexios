---
icon: question
cover: .gitbook/assets/icon.svg
coverY: 0
---

# What is Nexios 🤷‍♂️?
Nexios is a modern, high-performance ASGI framework for building asynchronous web applications in Python. It combines the simplicity of Express.js with Python's async capabilities to create a powerful, developer-friendly web framework that's easy to learn and easy to use 🚀.

Think of it as Express.js but speaking fluent Python. It doesn't force you into strict rules, doesn't ask for long configurations, and definitely doesn't judge your coding habits. It just works—so you can focus on writing awesome code instead of wrestling with boilerplate.

---

Nexios is a modern Python web framework designed for developers who value simplicity, performance, and flexibility. Built with the philosophy that web development shouldn't be complicated, Nexios brings the elegance of Express.js to the Python ecosystem.

Whether you're building APIs, microservices, or full-stack web applications, Nexios provides the tools you need without the overhead of complex configurations or rigid conventions.

```python
# A taste of Nexios - create a complete API in just a few lines
from nexios import get_application

app = get_application()

@app.get("/hello/{name}")
async def hello(request, response, name: str):
    return {"message": f"Hello, {name}!"}

@app.post("/api/data")
async def create_data(request, response):
    data = await request.json
    # Process your data here
    return {"status": "success", "id": 123, "data": data}

```

With Nexios, you're in charge. Want to structure your app your way? Go for it. Need to slap together a quick API in minutes? Done. It's all about freedom, speed, and keeping things simple—just like Express, but Pythonic.

No magic. No unnecessary fluff. Just clean, modular, and fun development. Because let's be honest—who doesn't love a framework that gets out of the way and lets you ship fast?

## Architecture Overview

Nexios follows a modular, middleware-based architecture that provides both simplicity and power:
```
┌─────────────────────────────────────────────────┐
│                  Client Request                 │
└───────────────────────┬─────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────┐
│                Middleware Stack                 │
│  ┌─────────┐   ┌─────────┐   ┌─────────────┐    │
│  │ Session │──►│  Auth   │──►│ CORS/CSRF   │──► │
│  └─────────┘   └─────────┘   └─────────────┘    │
└───────────────────────┬─────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────┐
│             Dependency Injection (DI)           │
└───────────────────────┬─────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────┐
│                 Route Handlers                  │
│  ┌─────────┐   ┌─────────┐   ┌─────────────┐    │
│  │ get()   │   │ post()  │   │ websocket() │    │
│  └─────────┘   └─────────┘   └─────────────┘    │
└───────────────────────┬─────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────┐
│                    Response                     │
└─────────────────────────────────────────────────┘
```

### Core Concepts

1. **Application**: The central object that manages routes, middleware, and configuration.
2. **Request/Response**: Objects representing HTTP requests and responses with intuitive APIs.
3. **Routing**: Flexible route definition with support for parameters, query strings, and more.
4. **Middleware**: Modular components that process requests before they reach your handlers.
5. **Dependency Injection**: A powerful system for managing dependencies and promoting testability.
6. **WebSockets**: First-class support for real-time communications.

## Quick Start

### Installation

```bash
# Install Nexios with pip
pip install nexios

# Or with Poetry
poetry add nexios
```

### Create a Basic Application

```python
# app.py
from nexios import get_application

app = get_application()

@app.get("/")
async def index(request, response):
    return {"message": "Welcome to Nexios!"}

@app.get("/users/{user_id}")
async def get_user(request, response, user_id: int):
    # In a real app, you would fetch this from a database
    return {"user_id": user_id, "name": "John Doe", "email": "john@example.com"}


```

### Run Your Application

```bash
# Run directly with uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000

# Or use the Nexios CLI (recommended for production)
nexios run app:app --host 0.0.0.0 --port 8000
```

Then visit [http://localhost:8000](http://localhost:8000) in your browser or use a tool like curl:

```bash
curl http://localhost:8000/users/42
# {"user_id": 42, "name": "John Doe", "email": "john@example.com"}
```

## Why Nexios?

* **Lightweight & Fast** – No unnecessary bloat, just install and start coding immediately. Benchmarks show Nexios performing on par with the fastest Python frameworks.

* **Modular & Flexible** – Use what you need, ignore what you don't. No rigid structures. Add middleware, extend functionality, or integrate with your favorite libraries.

* **Pythonic & Expressive** – Clean, readable, and intuitive, designed to feel natural in Python. Write code that makes sense to you and other Python developers.

* **API-First Approach** – Ideal for building RESTful APIs, microservices, or full-stack applications with automatic documentation via OpenAPI/Swagger.

* **ORM-Agnostic** – Works with SQLAlchemy, Tortoise, Django ORM, or even raw SQL. Use the database toolkit you're comfortable with.

* **Inspired by Express.js** – Minimal yet powerful, giving you full control over your application without unnecessary abstractions.

## Features

Nexios aims to be the most comprehensive yet intuitive web framework out there. It comes packed with powerful features right out of the box while still allowing you to extend its capabilities with plugins.

### Key Features

#### Robust Routing System

```python
# Parameter types with automatic validation
@app.get("/users/{user_id:int}")
async def get_user(request, response, user_id: int):
    return {"user_id": user_id}

# Request methods support
@app.post("/users")
@app.put("/users/{user_id}")
@app.delete("/users/{user_id}")

# Handler organization with Blueprint objects
users = Router(prefix="/api/users")

@users.get("/")
async def list_users(request, response):
    return {"users": [...]}

app.mount_router(users)
```

#### Powerful Middleware System

```python
@app.middleware
async def custom_middleware(request, response, next_handler):
    # Do something before the request is processed
    print("Processing request to", request.url.path)
    
    # Call the next middleware or route handler
    response = await next_handler()
    
    # Do something after the request is processed
    print("Completed request to", request.url.path)
    
    return response
```

#### Built-in Session Management

```python
from nexios.session.middleware import SessionMiddleware

app.add_middleware(SessionMiddleware())

@app.get("/visit-counter")
async def count_visits(request, response):
    if "visits" not in request.session:
        request.session["visits"] = 0
    request.session["visits"] += 1
    return {"visits": request.session["visits"]}
```

#### Integrated WebSocket Support

```python
@app.websocket("/chat")
async def chat_websocket(ws):
    await ws.accept()
    while True:
        data = await ws.receive_text()
        await ws.send_text(f"Echo: {data}")
```

#### Dependency Injection

```python
from nexios import Depend

async def get_db():
    # Connect to database...
    db = Database()
    try:
        yield db
    finally:
        # Close connection when done
        await db.close()

@app.get("/items")
async def list_items(request, response, db=Depend(get_db)):
    items = await db.query("SELECT * FROM items")
    return {"items": items}
```

## Framework Comparison

How does Nexios stack up against other Python web frameworks?

| Feature | Nexios | Django | Flask | FastAPI |
|---------|--------|--------|-------|---------|
| Learning Curve | Low | High | Low | Medium |
| Speed | Fast | Moderate | Moderate | Fast |
| Built-in ORM | No (Flexible) | Yes | No | No |
| Async Support | Full | Partial | Partial | Full |
| Middleware | Simple | Complex | Simple | Simple |
| Dependency Injection | Yes | No | No | Yes |
| WebSockets | Built-in | Addon | Addon | Built-in |
| API Documentation | Built-in OpenAPI | Addon | Addon | Built-in OpenAPI |
| Community Size | Growing | Large | Large | Medium |

## Next Steps

Ready to start building with Nexios? Check out these resources:

- [Basic Example](./basic-example.md) - A complete walkthrough of your first Nexios application
- [Installation Guide](./fundamentals/installation-guide.md) - Detailed installation instructions
- [Routing](./routing.md) - Learn more about Nexios' powerful routing system
- [Dependency Injection](./dependency-injection.md) - Master the DI system
- [Authentication](./authentication.md) - Secure your applications

## Community and Support

- [GitHub Repository](https://github.com/nexios-labs/nexios) - Star us, fork us, contribute!
- [Discord Community](https://discord.gg/nexios) - Get help and share your experiences
- [Issue Tracker](https://github.com/nexios-labs/nexios/issues) - Report bugs or request features


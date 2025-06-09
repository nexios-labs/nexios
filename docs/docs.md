---
title : Nexios
description : A fast and simple framework for building APIs with Python
icon : 😁
icon_color : #ff7f00
---

# Happy , You made it !

A lightweight, high-performance Python web framework built for speed, simplicity, and flexibility. Inspired by the ease of Express.js and powered by async capabilities.

---

Nexios allows you to create scalable applications quickly without compromising on performance. Whether you're building a microservice or a full-stack solution, Nexios gives you the tools to ship clean, efficient code with ease.

## Simple Example

::: tip What's happening here?
This example demonstrates the core concepts of Nexios: routing, async handlers, and type-safe responses.
:::

```python {3}
from nexios import Nexios

app = Nexios()

@app.get("/")
async def home(request: Request, response: Response):
    """Simple endpoint to verify the app is running"""
    return {"message": "Hello, World!"}
```

That's it! You can create API endpoints with just a few lines of code. 🚀

## Where To Start 😕

Getting started with Nexios is quick and simple. Whether you're building your first web app or integrating Nexios into an existing project, you'll find it easy to hit the ground running. Here's how you can get started:

---

### Installation Guide ⬇️

First things first, you need to install Nexios. It's as easy as running the following command:

::: tip Best Practice
Always install dependencies in a virtual environment for project isolation.
:::

```bash
pip install nexios
```

::: warning Python Version
Nexios requires Python 3.9 or higher for its async features and type hints.
:::

This will install the latest version of Nexios and all its dependencies. You're now ready to start building! For more clarity on the installation process, visit our detailed [installation guide](/docs/getting-started/installation-guide/).

---

### Create Your First Application 🚀

Now that you have Nexios installed, it's time to create your first application. Here's how you can do that:

```bash
nexios new myproject
cd myproject
```



This will create a new directory called `myproject` and install the necessary dependencies. You can then start building your application using the command `nexios run` in your terminal.

### Run Your Application

```bash
nexios run
```

::: tip Development Mode
Use `nexios run --reload` for automatic reloading during development.
:::

To run your application, you can use the command `nexios run` in your terminal. This will start the development server and make your application available at http://localhost:4000.

That's it! You're all set to start building your web app with Nexios. Have fun!

## Features

### Fast and Simple Framework 🚀
Built on ASGI with native async/await support, Nexios delivers high performance while maintaining code simplicity.

::: tip Performance
Nexios uses connection pooling and efficient routing for optimal performance:
```python
from nexios.db import Database, ConnectionPool

pool = ConnectionPool(min_size=5, max_size=20)
db = Database(pool)
```
:::

### Auto OpenAPI Documentation 📃
Automatic API documentation generation with support for OpenAPI/Swagger:

::: code-group
```python [Basic Usage]
@app.get("/items/{item_id}")
async def get_item(request, response, item_id: int):
    """Get an item by ID"""
    return response.json({"id": item_id})
```

```python [With Schema]
from pydantic import BaseModel

class Item(BaseModel):
    id: int
    name: str
    price: float

@app.post("/items")
async def create_item(request, response):
    """Create a new item"""
    item = Item(**await request.json())
    return response.json(item)
```
:::

### Authentication 🔒
Built-in authentication with support for multiple backends:

::: warning Security
Always use secure password hashing and token validation in production.
:::

```python
from nexios.auth import JWTAuth

auth = JWTAuth(secret_key="your-secret")
app.add_middleware(auth.middleware)
```

### CORS Support 🚧
Configurable CORS middleware with safe defaults:

```python
from nexios.middleware import CORSMiddleware

app.add_middleware(CORSMiddleware, 
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)
```

### Async Support 💞
Native async/await support throughout the framework:

::: tip Async Best Practices
- Use connection pooling for databases
- Implement proper error handling
- Don't block the event loop
:::

### ASGI Compatibility 🧑‍💻
Works with any ASGI server (Uvicorn, Hypercorn, etc.):

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Built-in CLI Tools 🛠️
Comprehensive CLI for project management:

::: code-group
```bash [Create Project]
nexios new myproject
```

```bash [Run Server]
nexios run --reload
```

```bash [Create Component]
nexios generate route users
```
:::

## Who is Nexios For?

### Beginners 🌱
If you're new to web development:
- Simple, intuitive API design
- Comprehensive documentation
- Built-in development tools
- Clear error messages

### Professionals 💼
For experienced developers:
- High performance async capabilities
- Advanced features like dependency injection
- Extensive middleware system
- WebSocket support

### Enterprise 🏢
For large-scale applications:
- Scalable architecture
- Security features built-in
- Monitoring and metrics
- Production-ready tools

## Why Use Nexios?

### Simple 📝
::: tip Simplicity
Nexios follows Python's "explicit is better than implicit" principle while reducing boilerplate code.
:::

### Fast ⚡
::: details Performance Features
- ASGI-based async runtime
- Efficient routing system
- Connection pooling
- Resource management
- Caching support
:::

### Flexible 🔧
::: tip Extensibility
Every part of Nexios can be customized:
- Custom middleware
- Authentication backends
- Database integrations
- Template engines
:::


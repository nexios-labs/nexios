---
icon: down-to-line
---

# Getting Started

This guide will help you get started with Nexios, a modern async Python web framework.

## Requirements

- Python 3.9 or higher
- pip or poetry for package management
- A basic understanding of async/await in Python

## Installation

### Using pip

```bash
# Basic installation
pip install nexios

# With optional dependencies
pip install nexios[all]      # All optional dependencies
pip install nexios[granian]  # Granian ASGI server support
pip install nexios[uvicorn]  # Uvicorn ASGI server
```

### Using poetry

```bash
# Basic installation
poetry add nexios

# With optional dependencies
poetry add nexios[all]
```

## Your First Application

Create a new file `main.py`:

```python
from nexios import NexiosApp

app = NexiosApp(
    title="My First API",
    version="1.0.0",
    description="A simple Nexios application"
)

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
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
```

## Running the Application

### Using the Nexios CLI

Nexios comes with a built-in CLI for running applications:

```bash
# Run with default settings
nexios run

# Run with custom host and port
nexios run --host 0.0.0.0 --port 8080

# Run with auto-reload for development
nexios run --reload
```

### Using ASGI Servers

You can also use any ASGI server directly:

```bash
# Using Uvicorn
uvicorn main:app --reload

# Using Hypercorn
hypercorn main:app --reload

# Using Granian (high performance)
granian --interface asgi main:app
```

## Configuration

Nexios uses a flexible configuration system through the `MakeConfig` class:

```python
from nexios import NexiosApp, MakeConfig

config = MakeConfig({
    "debug": True,
    "secret_key": "your-secret-key",
    "allowed_hosts": ["localhost", "example.com"],
    "cors_origins": ["http://localhost:3000"],
    "static_dir": "static",
    "template_dir": "templates"
})

app = NexiosApp(config=config)
```

### Quick Setup with get_application()

For rapid development, use `get_application()` which sets up common middleware:

```python
from nexios import get_application

app = get_application(
    config=MakeConfig({"debug": True}),
    title="Quick Start API"
)
```

This automatically includes:
- Session middleware
- CORS middleware
- CSRF protection
- Basic error handling

## Project Structure

For larger applications, consider this structure:

```
myapp/
├── app/
│   ├── __init__.py
│   ├── main.py          # Application entry point
│   ├── config.py        # Configuration
│   ├── routes/          # Route handlers
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── items.py
│   ├── middleware/      # Custom middleware
│   ├── models/          # Data models
│   └── utils/           # Utility functions
├── static/              # Static files
├── templates/           # Template files
├── tests/               # Test files
└── requirements.txt     # Dependencies
```

Example `app/main.py`:

```python
from nexios import NexiosApp, MakeConfig
from .config import get_config
from .routes import users, items

def create_app():
    config = get_config()
    app = NexiosApp(config=config)
    
    # Register routes
    app.include_router(users.router)
    app.include_router(items.router)
    
    # Setup middleware
    app.add_middleware(CustomMiddleware)
    
    # Register startup/shutdown handlers
    @app.on_startup()
    async def startup():
        await initialize_database()
    
    @app.on_shutdown()
    async def shutdown():
        await cleanup_resources()
    
    return app

app = create_app()
```

## Next Steps

- [Routing Guide](./routing.md) - Learn about URL routing and parameters
- [Middleware Guide](./middleware.md) - Understanding middleware and request processing
- [WebSocket Guide](./websockets/index.md) - Real-time communication with WebSockets
- [Authentication](./authentication.md) - Adding authentication to your API
- [Dependency Injection](./dependency-injection.md) - Managing dependencies
- [Error Handling](./error-handling.md) - Handling errors and exceptions
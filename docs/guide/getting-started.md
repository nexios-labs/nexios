---
icon: down-to-line
---

# Getting Started with Nexios

This guide will help you get started with Nexios and understand its core concepts.

## Requirements

- Python 3.9 or higher
- pip or poetry for package management
- A basic understanding of async/await in Python

## Installation

::: code-group
```bash [pip]
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Nexios
pip install nexios
```

```bash [poetry]
# Create a new project
poetry new my-nexios-app
cd my-nexios-app

# Add Nexios
poetry add nexios

# Activate environment
poetry shell
```

```bash [pipenv]
# Create a new project directory
mkdir my-nexios-app
cd my-nexios-app

# Initialize project
pipenv install nexios

# Activate environment
pipenv shell
```
:::

::: tip Version Requirements
Nexios requires Python 3.9 or higher. To check your Python version:
```bash
python --version
```
:::

## Quick Start

### 1. Create Your First App

Create a file named `main.py`:

::: code-group
```python [Basic App]
from nexios import NexiosApp

app = NexiosApp()

@app.get("/")
async def hello(request, response):
    return response.json({
        "message": "Hello from Nexios!"
    })

if __name__ == "__main__":
    app.run()
```

```python [With Config]
from nexios import NexiosApp, MakeConfig

config = MakeConfig(
    debug=True,
    cors_enabled=True,
    allowed_hosts=["localhost", "127.0.0.1"]
)

app = NexiosApp(
    config=config,
    title="My API",
    version="1.0.0"
)

@app.get("/")
async def hello(request, response):
    return response.json({
        "message": "Hello from Nexios!"
    })

if __name__ == "__main__":
    app.run()
```

```python [With Middleware]
from nexios import NexiosApp
from nexios.middleware import (
    CORSMiddleware,
    SecurityMiddleware
)

app = NexiosApp()

# Add middleware
app.add_middleware(CORSMiddleware())
app.add_middleware(SecurityMiddleware())

@app.get("/")
async def hello(request, response):
    return response.json({
        "message": "Hello from Nexios!"
    })

if __name__ == "__main__":
    app.run()
```
:::

### 2. Run the Application

::: code-group
```bash [Development]
# Run with auto-reload
nexios run --reload

# Or with Python directly
python main.py
```

```bash [Production]
# Using Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Using Gunicorn with Uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```
:::

::: tip Development Mode
In development:
- Use `--reload` for automatic reloading
- Enable debug mode for detailed error messages
- Use a single worker for easier debugging
:::

### 3. Test Your API

::: code-group
```python [Using httpx]
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get("http://localhost:8000")
    print(response.json())
```

```python [Using requests]
import requests

response = requests.get("http://localhost:8000")
print(response.json())
```

```bash [Using curl]
curl http://localhost:8000
```
:::

## Project Structure

Here's a recommended project structure for a Nexios application:

```
my_project/
├── app/
│   ├── __init__.py
│   ├── main.py          # Application entry point
│   ├── config.py        # Configuration
│   ├── routes/          # Route handlers
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── items.py
│   ├── models/          # Data models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/        # Business logic
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── middleware/      # Custom middleware
│   │   ├── __init__.py
│   │   └── logging.py
│   └── utils/           # Utility functions
│       ├── __init__.py
│       └── helpers.py
├── tests/               # Test files
│   ├── __init__.py
│   ├── test_routes.py
│   └── test_models.py
├── static/             # Static files
├── templates/          # Template files
├── .env               # Environment variables
├── .gitignore
├── README.md
├── requirements.txt   # Dependencies
└── setup.py          # Package setup
```

::: tip Project Organization
- Keep related code together in modules
- Use clear, descriptive names
- Follow Python package conventions
- Separate concerns into different modules
:::

## Basic Concepts

### 1. Route Handlers

```python
from nexios import NexiosApp

app = NexiosApp()

@app.get("/users/{user_id:int}")
async def get_user(request, response):
    """Get user by ID."""
    user_id = request.path_params.user_id
    return response.json({
        "id": user_id,
        "name": "John Doe"
    })

@app.post("/users")
async def create_user(request, response):
    """Create a new user."""
    data = await request.json()
    return response.json(data, status_code=201)
```

### 2. Request Handling

```python
@app.post("/upload")
async def upload_file(request, response):
    # Get form data
    form = await request.form()
    
    # Get files
    files = await request.files()
    
    # Get headers
    token = request.headers.get("Authorization")
    
    # Get query params
    page = request.query_params.get("page", 1)
    
    return response.json({"status": "ok"})
```

### 3. Response Types

```python
from nexios.responses import (
    JSONResponse,
    HTMLResponse,
    FileResponse,
    RedirectResponse
)

@app.get("/json")
async def json_response(request, response):
    return response.json({"hello": "world"})

@app.get("/html")
async def html_response(request, response):
    return HTMLResponse("<h1>Hello World</h1>")

@app.get("/file")
async def file_response(request, response):
    return FileResponse("path/to/file.pdf")

@app.get("/redirect")
async def redirect(request, response):
    return RedirectResponse("/new-url")
```

## Next Steps

After getting started, explore these topics:

1. [Routing and URL Patterns](/guide/routing)
2. [Request Handling](/guide/request-inputs)
3. [Response Types](/guide/sending-responses)
4. [Middleware](/guide/middleware)
5. [Authentication](/guide/authentication)
6. [Database Integration](/guide/database)
7. [WebSockets](/guide/websockets/)
8. [Testing](/guide/testing)

::: tip Learning Path
Start with basic concepts and gradually move to advanced topics. Practice with small examples before building larger applications.
:::

## Common Patterns

### Error Handling

```python
from nexios.exceptions import HTTPException

@app.get("/items/{item_id:int}")
async def get_item(request, response):
    item_id = request.path_params.item_id
    if item_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Item ID must be positive"
        )
    return response.json({"id": item_id})

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return response.json({
        "error": exc.detail
    }, status_code=exc.status_code)
```

### Dependency Injection

```python
from nexios import Depend

async def get_db():
    async with Database() as db:
        yield db

@app.get("/users")
async def list_users(
    request, 
    response,
    db=Depend(get_db)
):
    users = await db.fetch_all("SELECT * FROM users")
    return response.json(users)
```

### Configuration Management

```python
from nexios import NexiosApp, MakeConfig
from nexios.config import load_env

# Load environment variables
load_env()

config = MakeConfig(
    debug=True,
    database_url="${DATABASE_URL}",
    secret_key="${SECRET_KEY}",
    allowed_hosts=["localhost", "api.example.com"]
)

app = NexiosApp(config=config)
```

::: warning Security
Never commit sensitive configuration values. Use environment variables or secure vaults in production.
:::

## Development Tools

### 1. CLI Commands

```bash
# Create new project
nexios new my-project

# Run development server
nexios run --reload


```

### 2. Debug Toolbar

```python
from nexios.debug import DebugToolbarMiddleware

if app.debug:
    app.add_middleware(DebugToolbarMiddleware())
```



## Production Deployment

::: warning Production Setup
Before deploying to production:
1. Disable debug mode
2. Set secure configuration
3. Use proper ASGI server
4. Set up monitoring
5. Configure logging
:::

```python
# production.py
from nexios import NexiosApp, MakeConfig

config = MakeConfig(
    debug=False,
    secret_key="your-secure-key",
    allowed_hosts=["api.example.com"],
    cors_enabled=True,
    cors_origins=["https://example.com"],
    database_url="postgresql+asyncpg://user:pass@localhost/db"
)

app = NexiosApp(config=config)

)
```

## Need Help?

- Check the [API Reference](/api/)
- Join our [Discord Community](https://discord.gg/nexios)
- Open an issue on [GitHub](https://github.com/nexios-labs/nexios/issues)
- Read the [FAQ](/guide/faq)
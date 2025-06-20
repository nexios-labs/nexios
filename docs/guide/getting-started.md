---
icon: down-to-line
---

# Getting Started with Nexios

This guide will help you get started with Nexios and understand its core concepts. Nexios is a modern, async-first Python web framework that combines high performance with developer-friendly features.

::: tip Why Nexios?
Nexios is designed to be:
- **Fast**: Built on ASGI for high-performance async operations
- **Simple**: Clean, intuitive API that's easy to learn
- **Flexible**: Extensive customization options for any use case
- **Modern**: Full async/await support with type hints
- **Production-ready**: Built-in security, testing, and deployment features
:::

## Requirements

- Python 3.9 or higher
- pip or poetry for package management
- A basic understanding of async/await in Python

::: tip Python Version
Nexios requires Python 3.9+ because it leverages modern Python features like:
- Type annotations with generics
- Async context managers
- Pattern matching (Python 3.10+)
- Union types and other type system improvements
:::

::: tip Async/Await Knowledge
If you're new to async/await in Python, here are the key concepts:
- `async def`: Defines an asynchronous function
- `await`: Waits for an async operation to complete
- `async with`: Asynchronous context manager
- `async for`: Asynchronous iteration

Nexios uses async/await extensively for handling concurrent requests efficiently.
:::

## Installation

::: tip Recommended: Use [uv](https://github.com/astral-sh/uv)
We recommend using the [uv](https://github.com/astral-sh/uv) package manager for the fastest and most reliable Python dependency management. `uv` is a drop-in replacement for pip, pip-tools, and virtualenv, and is much faster than traditional tools.
:::

::: code-group
```bash [uv]
# Install uv (if you don't have it)
pip install uv

# Create a virtual environment and install Nexios
uv venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
uv pip install nexios
```

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

If you need to upgrade Python, consider using a version manager like `pyenv` or `asdf`.
:::

::: tip Virtual Environments
Always use virtual environments to isolate your project dependencies. This prevents conflicts between different projects and keeps your system Python clean.

**Benefits of virtual environments:**
- Isolate project dependencies
- Avoid version conflicts
- Easy project sharing and deployment
- Clean system Python installation
- Reproducible builds
:::

::: tip Package Manager Comparison
**uv (Recommended):**
- Fastest installation and dependency resolution
- Built-in virtual environment management
- Compatible with pip and pip-tools
- Excellent for both development and production

**pip:**
- Standard Python package manager
- Widely supported and documented
- Good for simple projects

**poetry:**
- Advanced dependency management
- Built-in project scaffolding
- Lock file for reproducible builds
- Good for complex projects

**pipenv:**
- Combines pip and virtualenv
- Automatic dependency resolution
- Good for development workflows
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

::: tip Application Structure
The basic Nexios application consists of:
1. **App Instance**: The main application object that manages routes, middleware, and configuration
2. **Route Handlers**: Async functions that handle specific HTTP requests
3. **Configuration**: Settings that control application behavior
4. **Middleware**: Components that process requests/responses

Each component is modular and can be customized independently.
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
- Use `--reload` for automatic reloading when files change
- Enable debug mode for detailed error messages and stack traces
- Use a single worker for easier debugging
- Enable CORS for frontend development
:::

::: tip Production Considerations
For production deployment:
- Disable debug mode for security and performance
- Use multiple workers for better concurrency
- Set up proper logging and monitoring
- Configure CORS with specific origins
- Use environment variables for sensitive configuration
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

::: tip Testing Tools
For testing your Nexios applications:
- **httpx**: Async HTTP client for Python (recommended)
- **requests**: Synchronous HTTP client
- **curl**: Command-line tool for quick tests
- **Postman/Insomnia**: GUI tools for API testing
- **pytest**: For automated testing
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
- **Keep related code together** in modules for better maintainability
- **Use clear, descriptive names** for files and directories
- **Follow Python package conventions** with `__init__.py` files
- **Separate concerns** into different modules (routes, models, services)
- **Group related functionality** in subdirectories
:::

::: tip Package Structure Best Practices
1. **Single Responsibility**: Each module should have one clear purpose
2. **Dependency Direction**: Dependencies should flow inward (routes → services → models)
3. **Configuration**: Keep configuration separate from business logic
4. **Testing**: Mirror your package structure in tests
5. **Documentation**: Include docstrings and README files
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

::: tip Route Handler Best Practices
1. **Use descriptive function names** that indicate the action
2. **Add docstrings** to explain what the handler does
3. **Use type hints** for better IDE support and documentation
4. **Keep handlers focused** on a single responsibility
5. **Extract business logic** to service functions
:::

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
    page = int(request.query_params.get("page", 1))
    
    return response.json({"status": "ok"})
```

::: tip Request Processing
- **Form data**: Use `await request.form()` for application/x-www-form-urlencoded
- **Files**: Use `await request.files()` for multipart/form-data
- **JSON**: Use `await request.json()` for application/json
- **Headers**: Access via `request.headers` dictionary
- **Query params**: Access via `request.query_params` dictionary
- **Path params**: Access via `request.path_params` with type conversion
:::

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

::: tip Response Best Practices
1. **Use appropriate status codes** for different scenarios
2. **Set proper headers** for content type and caching
3. **Handle errors gracefully** with meaningful messages
4. **Use streaming responses** for large files or real-time data
5. **Implement proper CORS** for cross-origin requests
:::

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

**Recommended learning order:**
1. Basic routing and handlers
2. Request/response handling
3. Middleware and authentication
4. Database integration
5. Advanced features (WebSockets, file uploads)
6. Testing and deployment
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

::: tip Error Handling Best Practices
1. **Use specific exception types** for different error scenarios
2. **Provide meaningful error messages** to help with debugging
3. **Log errors appropriately** for monitoring and debugging
4. **Don't expose sensitive information** in error messages
5. **Use consistent error response formats** across your API
:::

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

::: tip Dependency Injection Benefits
1. **Testability**: Easy to mock dependencies for testing
2. **Reusability**: Dependencies can be shared across multiple handlers
3. **Resource Management**: Automatic cleanup with `yield`
4. **Configuration**: Dependencies can be configured centrally
5. **Lazy Loading**: Dependencies are only created when needed
:::

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

**Security best practices:**
- Use environment variables for secrets
- Rotate keys regularly
- Use different keys for different environments
- Validate configuration values
- Use secure vaults in production
:::

## Development Tools

### 1. CLI Commands

```bash
# Create new project
nexios new my-project

# Run development server
nexios run --reload

# Generate OpenAPI documentation
nexios docs

# Run tests
nexios test
```

::: tip CLI Features
The Nexios CLI provides:
- **Project scaffolding** for quick setup
- **Development server** with auto-reload
- **Documentation generation** from your code
- **Testing utilities** for running tests
- **Database migrations** (when using ORM)
:::

### 2. Debug Toolbar

```python
from nexios.debug import DebugToolbarMiddleware

if app.config.debug:
    app.add_middleware(DebugToolbarMiddleware())
```

::: tip Debug Features
When debug mode is enabled:
- **Detailed error pages** with stack traces
- **Request/response inspection**
- **Database query logging**
- **Performance profiling**
- **Environment information**
:::

## Production Deployment

::: warning Production Setup
Before deploying to production:
1. **Disable debug mode** for security and performance
2. **Set secure configuration** with proper secrets
3. **Use proper ASGI server** (Uvicorn, Hypercorn, etc.)
4. **Set up monitoring** and logging
5. **Configure CORS** with specific origins
6. **Set up SSL/TLS** for HTTPS
7. **Configure rate limiting** and security headers
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
```

::: tip Production Checklist
- [ ] Debug mode disabled
- [ ] Secure secret key configured
- [ ] CORS properly configured
- [ ] Database connection secured
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] SSL/TLS configured
- [ ] Rate limiting enabled
- [ ] Security headers set
- [ ] Backup strategy in place
:::

## Need Help?

If you need help with Nexios:

1. **Check the documentation** for detailed guides and examples
2. **Look at the examples** in the `examples/` directory
3. **Search existing issues** on GitHub
4. **Create a new issue** if you found a bug
5. **Ask questions** in the community discussions

::: tip Getting Help
When asking for help:
- **Provide a minimal example** that reproduces the issue
- **Include error messages** and stack traces
- **Describe what you're trying to achieve**
- **Mention your Python and Nexios versions**
- **Show your current code** and what you've tried
:::



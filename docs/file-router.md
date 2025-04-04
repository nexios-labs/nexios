The FileRouter is a filesystem-based routing system for Nexios that automatically discovers and registers route handlers from Python files in a specified directory structure. This system follows convention-over-configuration principles, making API route management intuitive and scalable while reducing boilerplate code.

## Core Features

- **Automatic Route Registration**: Scans directories for route files and maps them to URL paths
- **HTTP Method Detection**: Recognizes standard HTTP methods (GET, POST, PUT, etc.) from handler function names
- **Dynamic Path Parameters**: Supports parameterized routes using curly brace syntax
- **Metadata Support**: Enables OpenAPI documentation through decorators
- **Flexible Configuration**: Allows exclusion of specific directories from scanning

## Installation and Setup

To use the FileRouter, first ensure Nexios is installed, then configure the router in your application entry point:

```python
from nexios import get_application
from nexios.file_router import FileRouter

app = get_application()

# Basic configuration scanning './routes' directory
FileRouter(app, config={"root": "./routes"})
```

## Configuration Options

The FileRouter accepts a configuration dictionary with the following properties:

- **root** (str): Required. The base directory to scan for route files
- **exempt_paths** (list[str]): Optional. List of directory names to exclude from scanning

Example with custom configuration:

```python
FileRouter(app, config={
    "root": "./api_endpoints",
    "exempt_paths": ["tests", "templates"]
})
```

## Filesystem Routing Conventions

The router maps directory structure to URL paths following these rules:

1. Each directory represents a path segment
2. Files must be named `route.py` to be detected
3. Dynamic parameters are specified using curly braces `{param}`

### Example Structure

```
routes/
├── products/
│   └── {product_id}/
│       └── route.py    # → /products/{product_id}
└── users/
    ├── route.py        # → /users
    └── {user_id}/
        └── route.py    # → /users/{user_id}
```

## Route Handlers

### Basic Route Handling

For simple routes, define functions named after HTTP methods in your `route.py` files:

```python
# routes/users/route.py

def get(req, res):
    """Handle GET /users"""
    return res.json({"users": ["user1", "user2"]})

def post(req, res):
    """Handle POST /users"""
    data = await req.json()
    return res.json({"created": True, "data": data}, status_code=201)
```

### Accessing Path Parameters

Dynamic route parameters are available in the request object:

```python
# routes/products/{product_id}/route.py

def get(req, res):
    product_id = req.path_params.product_id
    return res.json({"product": {"id": product_id}})
```

## Advanced Route Configuration

For more control over route behavior and documentation, use the `@mark_as_route` decorator:

```python
from nexios.utils import mark_as_route
from pydantic import BaseModel

class UserModel(BaseModel):
    name: str
    email: str

@mark_as_route(
    path="/custom-path",
    methods=["POST"],
    summary="Create user",
    description="Creates a new user with the provided data",
    request_model=UserModel,
    tags=["users"],
)
async def create_user(req, res):
    user_data = await req.json()
    return res.json(user_data, status_code=201)
```

### Available Decorator Options

| Parameter     | Description                                              |
| ------------- | -------------------------------------------------------- |
| path          | Custom URL path (overrides auto-detected path)           |
| methods       | List of HTTP methods (defaults to function name)         |
| summary       | Brief description for OpenAPI docs                       |
| description   | Detailed route description                               |
| request_model | Pydantic model for request validation                    |
| responses     | Dictionary mapping status codes to response descriptions |
| tags          | OpenAPI tags for grouping related routes                 |
| security      | Security requirements for the route                      |
| middlewares   | Route-specific middleware functions                      |
| operation_id  | Unique identifier for the operation in OpenAPI docs      |
| deprecated    | Marks the route as deprecated in documentation           |
| parameters    | Additional OpenAPI parameter definitions                 |

## Error Handling

The FileRouter integrates with Nexios's exception handling system. Define custom error handlers in your application:

```python
@app.add_exception_handler(404)
async def not_found_handler(req, res, exc):
    return res.json({"error": "Not Found"}, status_code=404)
```

## Limitations

1. Route files must be named `route.py`
2. Directory scanning occurs at startup (changes require restart in production)
3. Complex routing patterns may require manual route registration

## Example Project Structure

```
project/
├── app.py
└── api/
    ├── products/
    │   ├── {product_id}/
    │   │   └── route.py
    │   └── route.py
    ├── users/
    │   ├── {user_id}/
    │   │   └── route.py
    │   └── route.py
    └── admin/
        └── route.py
```

## Template Rendering System

The `html.py` module provides Jinja2 template rendering capabilities for Nexios applications. This system integrates seamlessly with the FileRouter to enable server-side HTML rendering.

### Core Components

1. **Template Environment Configuration**

   - Global Jinja2 environment management
   - Custom loader implementation
   - Auto-escaping and auto-reloading support

2. **Rendering Decorator**
   - `@render()` decorator for route handlers
   - Automatic template discovery
   - Context passing from handlers to templates

## Template Configuration

### Global Setup

Configure the template system at application startup:

```python
from nexios.file_router.html import configure_templates

# Basic configuration with template directory
configure_templates(template_dir="./templates")
```

```py
# Advanced configuration with custom environment
from jinja2 import Environment, FileSystemLoader
custom_env = Environment(
    loader=FileSystemLoader("./views"),
    autoescape=True,
    extensions=['jinja2.ext.i18n']
)
configure_templates(env=custom_env)
```

### Configuration Options

- `template_dir`: Base directory for template files
- `env`: Pre-configured Jinja2 environment (overrides template_dir)
- `**env_options`: Additional Jinja2 environment parameters

## Template Rendering in Routes

### Basic Usage

```python
from nexios.file_router.html import render

@render("user_profile.html")
def get(req, res):
    return {
        "username": "johndoe",
        "email": "john@example.com",
        "joined": "2023-01-15"
    }
```

```python
# routes/users/{id}/route.py
from nexios.file_router.html import render

from nexios.file_router.utils import mark_as_route


@render("users/profile.html")
def get(req, res):
    user_id = req.path_params.id
    return {
        "user_id": user_id,
        "profile": get_user_profile(user_id)
    }
```

## Template Directory Structure

Recommended structure for templates:

```
project/
├── templates/
│   ├── base.html          # Base template
│   ├── users/
│   │   ├── profile.html   # User profile template
│   │   └── list.html      # User list template
│   └── products/
│       ├── view.html
│       └── list.html
└── routes/
    └── users/
        └── {id}/
            └── route.py   # Route handler
```

## Advanced Features

### Template Inheritance

```html
<!-- templates/base.html -->
<html>
  <head>
    <title>{% block title %}My App{% endblock %}</title>
  </head>
  <body>
    {% block content %}{% endblock %}
  </body>
</html>

<!-- templates/users/profile.html -->
{% extends "base.html" %} {% block title %}User Profile - {{ username }}{%
endblock %} {% block content %}
<h1>{{ username }}</h1>
<p>Email: {{ email }}</p>
{% endblock %}
```

### Custom Loader Behavior

The included `Loader` class provides:

- Template file discovery
- Modification time checking
- Automatic reloading in development

### Context Validation

For type-safe templates, use Pydantic models:

```python
from pydantic import BaseModel

class ProfileContext(BaseModel):
    username: str
    email: str
    joined: str

@render("profile.html")
def get(req, res):
    return ProfileContext(
        username="johndoe",
        email="john@example.com",
        joined="2023-01-15"
    ).dict()
```

## Error Handling

The rendering system provides clear error messages for:

- Missing templates
- Invalid context data
- Template syntax errors

## Performance Considerations

1. **Template Caching**: Enabled by default in production
2. **Auto-reload**: Disable in production for better performance
3. **Pre-compilation**: Consider pre-compiling templates for deployment

## Debugging Tips

1. Set `auto_reload=True` during development
2. Use `print(template_directory)` in the render decorator to verify paths
3. Check Jinja2's built-in debugging features

## Complete Example

```python
# routes/products/{id}/route.py
from nexios.html import render
from nexios.utils import mark_as_route
from pydantic import BaseModel

class ProductViewContext(BaseModel):
    product_id: str
    name: str
    price: float
    in_stock: bool


@render("products/detail.html")
def get(req, res):
    product = get_product(req.path_params.id)
    return ProductViewContext(
        product_id=product.id,
        name=product.name,
        price=product.price,
        in_stock=product.quantity > 0
    ).dict()
```

This system provides a robust, type-safe way to render HTML templates while maintaining clean separation of concerns in your Nexios application.

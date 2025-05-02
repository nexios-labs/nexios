---
icon: swap
---

# File Router

## File Router

The File Router system in Nexios allows you to define your application's routes using the filesystem structure, providing a convention-over-configuration approach to routing that can make your API more organized and maintainable.

### Introduction

File routing is an intuitive approach to organizing web application endpoints. Instead of defining all routes explicitly in code, the file system itself becomes the router based on predefined conventions. This is similar to the file-based routing systems used in frameworks like Next.js and Nuxt.js, but adapted for backend API development.

#### Benefits of File Routing

* **Visual Structure**: Your directory structure gives a clear visual map of your API endpoints
* **Organization**: Keeps related route handlers together and organized by domain
* **Discoverability**: Easier to find specific endpoint implementations
* **Scalability**: Routes can grow naturally as your application expands
* **Convention over Configuration**: Reduces boilerplate code needed for routing setup

### Basic Setup

To use the File Router in your Nexios application, set it up in your main application file:

```python
from nexios import get_application
from nexios.file_router import FileRouter

app = get_application()

# Configure the File Router
FileRouter(app, config={
    "root": "./routes",
    "exempt_paths": [],
    "exclude_from_schema": False
})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### Configuration Options

| Option                | Description                                               | Default      |
| --------------------- | --------------------------------------------------------- | ------------ |
| `root`                | The root directory where route files will be located      | `"./routes"` |
| `exempt_paths`        | List of path patterns to exclude from file routing        | `[]`         |
| `exclude_from_schema` | Whether to exclude file routes from OpenAPI documentation | `False`      |

### Directory Structure and Conventions

File Router looks for files named `route.py` in your routes directory and its subdirectories. The path to each `route.py` file determines the URL endpoint it will handle.

#### Basic Structure Example

```
routes/
├── route.py              # Handles "/"
├── users/
│   ├── route.py          # Handles "/users"
│   ├── _id/              # Dynamic parameter 'id'
│   │   └── route.py      # Handles "/users/{id}"
│   └── settings/
│       └── route.py      # Handles "/users/settings"
└── products/
    ├── route.py          # Handles "/products"
    └── categories/
        ├── route.py      # Handles "/products/categories"
        └── _category_id/ # Dynamic parameter 'category_id'
            └── route.py  # Handles "/products/categories/{category_id}"
```

#### Creating Route Handlers

Each `route.py` file contains handlers for different HTTP methods at that endpoint:

```python
# routes/users/route.py

def get(req, res):
    """Handle GET request to /users"""
    return res.json({"message": "List all users"})

def post(req, res):
    """Handle POST request to /users"""
    return res.json({"message": "Create new user"})

def delete(req, res):
    """Handle DELETE request to /users"""
    return res.json({"message": "Bulk delete users"})
```

The file router automatically maps the functions named after HTTP methods (`get`, `post`, `put`, `delete`, `patch`, etc.) to the corresponding HTTP verbs for that route.

### Dynamic Route Parameters

Dynamic route segments are indicated by prefixing a directory name with an underscore (`_`). This tells the File Router that this segment of the path should be treated as a parameter.

#### Simple Parameters

```
routes/
└── users/
    └── _user_id/         # Creates parameter 'user_id'
        └── route.py
```

The parameter becomes available in the `req.path_params` dictionary:

```python
# routes/users/_user_id/route.py

def get(req, res):
    user_id = req.path_params.user_id
    return res.json({"message": f"Get user {user_id}"})
```

#### Nested Parameters

Parameters can be nested at multiple levels:

```
routes/
└── users/
    └── _user_id/
        └── posts/
            └── _post_id/
                └── route.py  # Handles /users/{user_id}/posts/{post_id}
```

```python
# routes/users/_user_id/posts/_post_id/route.py

def get(req, res):
    user_id = req.path_params.user_id
    post_id = req.path_params.post_id
    return res.json({"message": f"Get post {post_id} by user {user_id}"})
```

#### Catch-all Parameters

For catch-all route segments that can include multiple path parts, use multiple underscores:

```
routes/
└── files/
    └── __filepath/        # Creates catch-all parameter 'filepath'
        └── route.py       # Handles /files/{filepath:path}
```

```python
# routes/files/__filepath/route.py

def get(req, res):
    filepath = req.path_params.filepath
    # filepath can contain slashes, e.g. "documents/reports/2023.pdf"
    return res.text(f"Serving file: {filepath}")
```

### Advanced Route Configuration

While the file-based routing system provides default behavior based on file names, you can enhance your routes with additional configuration using decorators.

#### Custom Route Decorators

Nexios provides several decorators to configure route behavior:

```python
# routes/products/route.py
from nexios.decorators import route, summary, description, tags

@route("/products", methods=["GET"])
@summary("List all products")
@description("Returns a paginated list of all available products")
@tags(["products"])
def get(req, res):
    return res.json({"products": [{"id": 1, "name": "Example Product"}]})
```

#### Custom Path Override

You can override the automatically determined path:

```python
# routes/special.py
from nexios.decorators import route

@route("/custom-path")
def get(req, res):
    # This will handle /custom-path, not /special
    return res.json({"message": "Custom path"})
```

#### Route Metadata for OpenAPI Documentation

Add OpenAPI metadata to your routes:

```python
# routes/users/route.py
from nexios.decorators import summary, description, responses, request_model
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

class CreateUserRequest(BaseModel):
    name: str
    email: str
    password: str

@summary("Create new user")
@description("Register a new user in the system")
@responses({201: User, 400: {"description": "Invalid input"}})
@request_model(CreateUserRequest)
def post(req, res):
    user_data = await req.json
    # Create user logic...
    return res.json({"id": 1, "name": user_data["name"], "email": user_data["email"]}, status_code=201)
```

#### Route-Specific Middleware

Apply middleware to specific routes:

```python
# routes/admin/route.py
from nexios.decorators import middleware
from nexios.middlewares import AuthMiddleware, LoggingMiddleware

@middleware([AuthMiddleware, LoggingMiddleware])
def get(req, res):
    return res.json({"message": "Admin dashboard"})
```

### Custom Route Handlers

For more complex routes, you can use a custom function instead of the standard HTTP method handlers:

```python
# routes/complex/route.py
from nexios.decorators import route

@route("/complex", methods=["GET", "POST"])
def handle_complex(req, res):
    """Custom handler for multiple methods"""
    if req.method == "GET":
        return res.json({"message": "GET method"})
    elif req.method == "POST":
        return res.json({"message": "POST method"})
```

### Common Patterns and Best Practices

#### API Versioning

Organize your API versions in the file structure:

```
routes/
├── v1/
│   ├── users/
│   │   └── route.py      # Handles "/v1/users"
│   └── products/
│       └── route.py      # Handles "/v1/products"
├── v2/
│   ├── users/
│   │   └── route.py      # Handles "/v2/users"
│   └── products/
│       └── route.py      # Handles "/v2/products"
```

#### Resource-Based Organization

Structure your routes around your resources:

```
routes/
├── users/
│   ├── route.py          # User collection endpoints
│   ├── _id/
│   │   ├── route.py      # Single user endpoints
│   │   ├── posts/
│   │   │   └── route.py  # User's posts collection 
│   │   └── profile/
│   │       └── route.py  # User's profile
├── posts/
│   ├── route.py          # Post collection endpoints
│   └── _id/
│       └── route.py      # Single post endpoints
```

#### Index Routes vs. Route Files

For clarity, you can use `index.py` instead of `route.py` to indicate the default route for a directory:

```
routes/
├── index.py              # Handles "/"
├── users/
│   ├── index.py          # Handles "/users"
│   └── _id/
│       └── index.py      # Handles "/users/{id}"
```

The File Router will treat `index.py` the same as `route.py` if you configure it to recognize both patterns.

### Complete Example

Let's put it all together with a complete example of a blog API:

#### Directory Structure

```
routes/
├── route.py              # API home
├── auth/
│   ├── route.py          # Authentication endpoints
│   ├── login/
│   │   └── route.py      # Login endpoint
│   └── register/
│       └── route.py      # Registration endpoint
├── users/
│   ├── route.py          # Users collection
│   └── _user_id/
│       ├── route.py      # Single user operations
│       └── posts/
│           └── route.py  # Posts by specific user
└── posts/
    ├── route.py          # Posts collection
    ├── _post_id/
    │   ├── route.py      # Single post operations
    │   └── comments/
    │       └── route.py  # Comments on specific post
    └── categories/
        ├── route.py      # Categories collection
        └── _category/
            └── route.py  # Posts by category
```

#### Implementation Example

```python
# routes/route.py
def get(req, res):
    return res.json({
        "name": "Blog API",
        "version": "1.0.0",
        "endpoints": [
            "/auth", "/users", "/posts"
        ]
    })
```

```python
# routes/posts/route.py
from pydantic import BaseModel
from typing import List, Optional
from nexios.decorators import summary, description, tags, responses, request_model

class PostPreview(BaseModel):
    id: int
    title: str
    excerpt: str
    author_name: str

class PostCreate(BaseModel):
    title: str
    content: str
    category_id: Optional[int] = None

@summary("List all posts")
@description("Get a paginated list of all blog posts")
@tags(["posts"])
@responses({200: List[PostPreview]})
def get(req, res):
    # Get query parameters
    page = int(req.query_params.get("page", 1))
    limit = int(req.query_params.get("limit", 10))
    
    # Simulated database query
    posts = [
        {"id": i, "title": f"Post {i}", "excerpt": f"Excerpt {i}", "author_name": "Author"}
        for i in range((page-1)*limit + 1, page*limit + 1)
    ]
    
    return res.json(posts)

@summary("Create a new post")
@description("Create a new blog post")
@tags(["posts"])
@request_model(PostCreate)
@responses({201: PostPreview, 400: {"description": "Invalid data"}})
async def post(req, res):
    post_data = await req.json
    # Simulated post creation
    new_post = {
        "id": 123,
        "title": post_data["title"],
        "excerpt": post_data["content"][:100] + "...",
        "author_name": "Current User"
    }
    return res.json(new_post, status_code=201)
```

```python
# routes/posts/_post_id/route.py
def get(req, res):
    post_id = req.path_params.post_id
    # Simulated post retrieval
    post = {
        "id": post_id,
        "title": f"Post {post_id}",
        "content": f"This is the content of post {post_id}",
        "author": {
            "id": 1,
            "name": "Author Name"
        },
        "created_at": "2023-01-01T12:00:00Z"
    }
    return res.json(post)

def put(req, res):
    post_id = req.path_params.post_id
    return res.json({"message": f"Post {post_id} updated"})

def delete(req, res):
    post_id = req.path_params.post_id
    return res.json({"message": f"Post {post_id} deleted"})
```

### Integration with Traditional Routing

The File Router can coexist with traditional decorator-based routes in the same application:

```python
from nexios import get_application
from nexios.file_router import FileRouter

app = get_application()

# Set up File Router
FileRouter(app, config={"root": "./routes"})

# Add traditional routes
@app.get("/health")
async def health_check(req, res):
    return res.json({"status": "ok"})

# The file routes and traditional routes will work together
```

This approach gives you the flexibility to use file-based routing for the majority of your application while still allowing for special cases to be handled with traditional routes.

### Conclusion

The File Router system in Nexios provides a powerful, organized approach to structuring your API endpoints. By leveraging the filesystem hierarchy, you can create intuitive, maintainable route structures that grow naturally with your application. Combined with the various decorators and configuration options, File Router offers both simplicity and flexibility for your web API development.

***

### icon: swap

## File Router

The FileRouter is a filesystem-based routing system for Nexios that automatically discovers and registers route handlers from Python files in a specified directory structure. This system follows convention-over-configuration principles, making API route management intuitive and scalable while reducing boilerplate code.

#### Core Features

* **Automatic Route Registration**: Scans directories for route files and maps them to URL paths
* **HTTP Method Detection**: Recognizes standard HTTP methods (GET, POST, PUT, etc.) from handler function names
* **Dynamic Path Parameters**: Supports parameterized routes using curly brace syntax
* **Metadata Support**: Enables OpenAPI documentation through decorators
* **Flexible Configuration**: Allows exclusion of specific directories from scanning

#### Installation and Setup

To use the FileRouter, first ensure Nexios is installed, then configure the router in your application entry point:

```python
from nexios import get_application
from nexios.file_router import FileRouter

app = get_application()

# Basic configuration scanning './routes' directory
FileRouter(app, config={"root": "./routes"})
```

#### Configuration Options

The FileRouter accepts a configuration dictionary with the following properties:

* **root** (str): Required. The base directory to scan for route files
* **exempt\_paths** (list\[str]): Optional. List of directory names to exclude from scanning

Example with custom configuration:

```python
FileRouter(app, config={
    "root": "./api_endpoints",
    "exempt_paths": ["tests", "templates"],
    "exclude_from_schema":True #or False
})
```

#### Filesystem Routing Conventions

The router maps directory structure to URL paths following these rules:

1. Each directory represents a path segment
2. Files must be named `route.py` to be detected
3. Dynamic parameters are specified using curly braces `{param}`

**Example Structure**

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

#### Route Handlers

**Basic Route Handling**

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

**Accessing Path Parameters**

Dynamic route parameters are available in the request object:

```python
# routes/products/{product_id}/route.py

def get(req, res):
    product_id = req.path_params.product_id
    return res.json({"product": {"id": product_id}})
```

#### Advanced Route Configuration

For more control over route behavior and documentation, use the `@mark_as_route` decorator:

```python
from nexios.file_router.utils import mark_as_route
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

**Available Decorator Options**

| Parameter      | Description                                              |
| -------------- | -------------------------------------------------------- |
| path           | Custom URL path (overrides auto-detected path)           |
| methods        | List of HTTP methods (defaults to function name)         |
| summary        | Brief description for OpenAPI docs                       |
| description    | Detailed route description                               |
| request\_model | Pydantic model for request validation                    |
| responses      | Dictionary mapping status codes to response descriptions |
| tags           | OpenAPI tags for grouping related routes                 |
| security       | Security requirements for the route                      |
| middlewares    | Route-specific middleware functions                      |
| operation\_id  | Unique identifier for the operation in OpenAPI docs      |
| deprecated     | Marks the route as deprecated in documentation           |
| parameters     | Additional OpenAPI parameter definitions                 |

#### Error Handling

The FileRouter integrates with Nexios's exception handling system. Define custom error handlers in your application:

```python
@app.add_exception_handler(404)
async def not_found_handler(req, res, exc):
    return res.json({"error": "Not Found"}, status_code=404)
```

#### Limitations

1. Route files must be named `route.py`
2. Directory scanning occurs at startup (changes require restart in production)
3. Complex routing patterns may require manual route registration

#### Example Project Structure

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

#### Template Rendering System

The `html.py` module provides Jinja2 template rendering capabilities for Nexios applications. This system integrates seamlessly with the FileRouter to enable server-side HTML rendering.

**Core Components**

1. **Template Environment Configuration**
   * Global Jinja2 environment management
   * Custom loader implementation
   * Auto-escaping and auto-reloading support
2. **Rendering Decorator**
   * `@render()` decorator for route handlers
   * Automatic template discovery
   * Context passing from handlers to templates

#### Template Configuration

**Global Setup**

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

**Configuration Options**

* `template_dir`: Base directory for template files
* `env`: Pre-configured Jinja2 environment (overrides template\_dir)
* `**env_options`: Additional Jinja2 environment parameters

#### Template Rendering in Routes

**Basic Usage**

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

#### Template Directory Structure

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

#### Advanced Features

**Template Inheritance**

```html
<!-- templates/base.html -->
<html>
  <head>
    <title><div data-gb-custom-block data-tag="block">My App</div></title>
  </head>
  <body>
    <div data-gb-custom-block data-tag="block"></div>
  </body>
</html>

<!-- templates/users/profile.html -->

<div data-gb-custom-block data-tag="extends" data-0="base.html"></div>
<div data-gb-custom-block data-tag="block"></div>
User Profile - {{ username }}</div>
<div data-gb-custom-block data-tag="block">
  <h1>{{ username }}</h1>
  <p>Email: {{ email }}</p>
</div>
```

**Custom Loader Behavior**

The included `Loader` class provides:

* Template file discovery
* Modification time checking
* Automatic reloading in development

**Context Validation**

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

#### Error Handling

The rendering system provides clear error messages for:

* Missing templates
* Invalid context data
* Template syntax errors

#### Performance Considerations

1. **Template Caching**: Enabled by default in production
2. **Auto-reload**: Disable in production for better performance
3. **Pre-compilation**: Consider pre-compiling templates for deployment

#### Debugging Tips

1. Set `auto_reload=True` during development
2. Use `print(template_directory)` in the render decorator to verify paths
3. Check Jinja2's built-in debugging features

#### Complete Example

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

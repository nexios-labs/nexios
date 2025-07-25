# Handlers

Handlers are the heart of your Nexios application. They define how your application responds to incoming HTTP requests. Every route in your application is handled by a handler function that processes the request and returns a response.

## Core Requirements

**Critical Requirement**: All Nexios handlers MUST be async functions. This is a strict requirement that cannot be overridden. Synchronous handlers are not supported and will raise errors.

Handlers receive a Request object and return a Response, dict, str, or other supported types. They are the core building blocks of your application where business logic is implemented.

### Handler Fundamentals

Every Nexios handler follows these fundamental principles:

- **Must be async**: All handlers use `async def` for non-blocking operations
- **Receive request/response**: Standard parameters for accessing request data and building responses
- **Return responses**: Can return various types that Nexios converts to HTTP responses
- **Handle errors**: Can raise exceptions that are caught by exception handlers
- **Support dependencies**: Can use dependency injection for clean, testable code

### Handler Best Practices

1. **Keep handlers focused**: Each handler should do one thing well
2. **Extract business logic**: Move complex logic to service functions
3. **Use type hints**: Improve IDE support and code documentation
4. **Handle errors gracefully**: Use appropriate exception handling
5. **Validate inputs**: Check request data before processing
6. **Return consistent responses**: Use standard response formats
7. **Document your handlers**: Add docstrings explaining purpose and parameters

## Basic Handler Structure

Every Nexios handler must be an async function triggered by a route and returns a value that becomes the response.
```python
from nexios import NexiosApp

app = NexiosApp()

@app.get("/")  
async def index(request, response): 
    return "Hello, world!" 
```

**Important**: Nexios handlers must take at least two arguments: `request` and `response`.

The `request` and `response` objects are provided by Nexios and contain information about the incoming request and the outgoing response.

### Type Annotations for Better Development Experience

Using type annotations provides better IDE support, improved documentation, static type checking, better refactoring support, and clearer interfaces between components.

```python
from nexios.http import Request, Response

@app.get("/")  
async def index(request: Request, response: Response): 
    return "Hello, world!" 
```

For more detailed information about request and response objects, see the Request and Response documentation.

## Alternative Handler Registration

You can also register handlers using the `Routes` class for more control over route configuration:

```python
from nexios.routing import Routes
from nexios import NexiosApp

app = NexiosApp()

async def dynamic_handler(req, res):
    return "Hello, world!"

app.add_route(Routes("/dynamic", dynamic_handler))  # Handles All Methods by default
```

## Request Handlers

Request handlers are the core building blocks of your Nexios application. They process incoming HTTP requests and return appropriate responses.

### Function Handlers

Handlers can be defined in several ways depending on your needs:

```python
from nexios import NexiosApp

app = NexiosApp()

# Basic handler returning JSON
@app.get("/")
async def index(request, response):
    return response.json({
        "message": "Hello, World!"
    })

# Handler with path parameters
@app.get("/users/{user_id:int}")
async def get_user(request, response):
    user_id = request.path_params.user_id
    return response.json({
        "id": user_id,
        "name": "John Doe"
    })

# Handler with query parameters
@app.get("/search")
async def search(request, response):
    query = request.query_params.get("q", "")
    page = int(request.query_params.get("page", 1))
    return response.json({
        "query": query,
        "page": page,
        "results": []
    })
```

### HTTP Method Handlers

Nexios provides decorators for all standard HTTP methods:

```python
# GET request - Retrieve data
@app.get("/items")
async def list_items(request, response):
    return response.json({"items": []})

# POST request - Create new resource
@app.post("/items")
async def create_item(request, response):
    data = await request.json
    return response.json(data, status_code=201)

# PUT request - Replace entire resource
@app.put("/items/{item_id:int}")
async def update_item(request, response):
    item_id = request.path_params.item_id
    data = await request.json
    return response.json({
        "id": item_id,
        **data
    })

# DELETE request - Remove resource
@app.delete("/items/{item_id:int}")
async def delete_item(request, response):
    item_id = request.path_params.item_id
    return response.json(None, status_code=204)

# PATCH request - Partial update
@app.patch("/items/{item_id:int}")
async def partial_update(request, response):
    item_id = request.path_params.item_id
    data = await request.json
    return response.json({
        "id": item_id,
        **data
    })

# HEAD request - Get headers only
@app.head("/status")
async def status(request, response):
    response.set_header("X-KEY", "Value")
    return response.json(None)

# OPTIONS request - Get allowed methods
@app.options("/items")
async def options(request, response):
    response.set_header("Allow", "GET, POST, PUT, DELETE")
    return response.json(None)
```

## Request Processing

### Accessing Request Information

Handlers have access to comprehensive request information through the request object:

```python
@app.post("/upload")
async def upload_file(request, response):
    # Request method
    method = request.method  # "POST"
    
    # URL information
    url = request.url  # Full URL
    path = request.path  # Path component
    query = request.query  # Query string
    
    # Headers
    content_type = request.headers.get("content-type")
    user_agent = request.headers.get("user-agent")
    
    # Client information
    client_ip = request.client.host
    client_port = request.client.port
    
    # Request body
    body = await request.body  # Raw bytes
    json_data = await request.json  # Parsed JSON
    form_data = await request.form  # Form data
    
    return response.json({
        "method": method,
        "path": path,
        "content_type": content_type,
        "client_ip": client_ip
    })
```

### Path Parameters

Path parameters allow you to capture dynamic segments of the URL:

```python
@app.get("/users/{user_id:int}")
async def get_user(request, response):
    user_id = request.path_params.user_id  # Automatically converted to int
    return response.json({"id": user_id})

@app.get("/posts/{post_id}/comments/{comment_id}")
async def get_comment(request, response):
    post_id = request.path_params.post_id
    comment_id = request.path_params.comment_id
    return response.json({
        "post_id": post_id,
        "comment_id": comment_id
    })
```

### Query Parameters

Query parameters are accessed through the `query_params` attribute:

```python
@app.get("/search")
async def search(request, response):
    # Get single parameter with default
    query = request.query_params.get("q", "")
    
    # Get parameter with type conversion
    page = int(request.query_params.get("page", 1))
    limit = int(request.query_params.get("limit", 10))
    
    # Get multiple values for the same parameter
    tags = request.query_params.getlist("tag")
    
    # Get all query parameters as dict
    all_params = dict(request.query_params)
    
    return response.json({
        "query": query,
        "page": page,
        "limit": limit,
        "tags": tags,
        "all_params": all_params
    })
```

### Request Body

Handlers can access the request body in various formats:

```python
@app.post("/data")
async def process_data(request, response):
    # JSON data
    json_data = await request.json
    
    # Form data
    form_data = await request.form
    
    # Raw bytes
    raw_body = await request.body
    
    # Text content
    text_content = await request.text
    
    return response.json({
        "json": json_data,
        "form": dict(form_data),
        "body_size": len(raw_body)
    })
```

## Response Handling

### Creating Responses

Nexios provides multiple ways to create responses:

```python
@app.get("/responses")
async def demonstrate_responses(request, response):
    # JSON response
    return response.json({
        "message": "Hello",
        "status": "success"
    })
    
    # Text response
    return response.text("Hello, World!")
    
    # HTML response
    return response.html("<h1>Hello</h1>")
    
    # File response
    return response.file("path/to/file.pdf")
    
    # Redirect
    return response.redirect("/new-location")
    
    # Custom status code
    return response.json({"error": "Not found"}, status_code=404)
```

### Setting Headers

You can set custom headers on responses:

```python
@app.get("/custom-headers")
async def custom_headers(request, response):
    response.set_header("X-Custom-Header", "Custom Value")
    response.set_header("Cache-Control", "no-cache")
    response.set_header("Content-Type", "application/json")
    
    return response.json({"message": "Headers set"})
```

### Response Status Codes

Nexios provides convenient methods for common status codes:

```python
@app.get("/status-examples")
async def status_examples(request, response):
    # Success responses
    return response.json({"data": "success"}, status_code=200)
    return response.json({"created": True}, status_code=201)
    return response.json(None, status_code=204)
    
    # Client error responses
    return response.json({"error": "Bad request"}, status_code=400)
    return response.json({"error": "Unauthorized"}, status_code=401)
    return response.json({"error": "Forbidden"}, status_code=403)
    return response.json({"error": "Not found"}, status_code=404)
    
    # Server error responses
    return response.json({"error": "Internal error"}, status_code=500)
    return response.json({"error": "Service unavailable"}, status_code=503)
```

## Error Handling

### Raising Exceptions

Handlers can raise exceptions that will be caught by exception handlers:

```python
from nexios.exceptions import HTTPException

@app.get("/users/{user_id:int}")
async def get_user(request, response):
    user_id = request.path_params.user_id
    
    # Simulate user not found
    if user_id > 1000:
        raise HTTPException(404, f"User {user_id} not found")
    
    # Simulate server error
    if user_id == 0:
        raise HTTPException(500, "Internal server error")
    
    return response.json({"id": user_id, "name": "John Doe"})
```

### Custom Exception Handling

You can define custom exception handlers:

```python
@app.add_exception_handler(ValueError)
async def handle_value_error(request, response, exc):
    return response.json({
        "error": "Invalid value provided",
        "details": str(exc)
    }, status_code=400)

@app.add_exception_handler(404)
async def handle_not_found(request, response, exc):
    return response.json({
        "error": "Resource not found",
        "path": request.path
    }, status_code=404)
```

## Dependency Injection

### Using Dependencies

Handlers can use dependency injection for clean, testable code:

```python
from nexios import Depend

async def get_database():
    # This could return a database connection
    return {"connection": "active"}

async def get_current_user(request, db=Depend(get_database)):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(401, "Unauthorized")
    
    # Use the database connection
    user = await db.get_user_by_token(token)
    return user

@app.get("/profile")
async def get_profile(request, response, user=Depend(get_current_user)):
    return response.json({
        "id": user.id,
        "name": user.name,
        "email": user.email
    })
```

### Dependency Scopes

Dependencies can have different scopes:

```python
# Application-scoped dependency (shared across all requests)
async def get_config():
    return load_configuration()

# Request-scoped dependency (new instance per request)
async def get_db_connection():
    return await create_db_connection()

@app.get("/data")
async def get_data(
    request, 
    response, 
    config=Depend(get_config, scope="application"),
    db=Depend(get_db_connection, scope="request")
):
    # config is shared across all requests
    # db is a new connection for each request
    return response.json(await db.query("SELECT * FROM data"))
```

## Advanced Handler Patterns

### Handler Composition

You can compose handlers using middleware and decorators:

```python
def require_auth(handler):
    async def wrapper(request, response, *args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return response.json({"error": "Unauthorized"}, status_code=401)
        
        # Add user to request context
        request.user = await get_user_from_token(token)
        return await handler(request, response, *args, **kwargs)
    
    return wrapper

@app.get("/protected")
@require_auth
async def protected_route(request, response):
    return response.json({
        "message": "Hello, authenticated user!",
        "user_id": request.user.id
    })
```

### Async Context Managers

Use async context managers for resource management:

```python
@app.post("/process-file")
async def process_file(request, response):
    async with open_file("data.txt") as file:
        content = await file.read()
        processed = await process_content(content)
        
    return response.json({"processed": processed})
```

### Background Tasks

Handlers can trigger background tasks:

```python
@app.post("/send-email")
async def send_email(request, response):
    email_data = await request.json
    
    # Start background task
    app.add_background_task(send_email_task, email_data)
    
    return response.json({"message": "Email queued for sending"})

async def send_email_task(email_data):
    # This runs in the background
    await send_email(email_data)
```

## Handler Testing

### Unit Testing Handlers

```python
import pytest
from nexios.testing import TestClient

@pytest.fixture
def client():
    return TestClient(app)

def test_get_user(client):
    response = client.get("/users/123")
    assert response.status_code == 200
    assert response.json()["id"] == 123

def test_create_user(client):
    user_data = {"name": "John", "email": "john@example.com"}
    response = client.post("/users", json=user_data)
    assert response.status_code == 201
    assert response.json()["name"] == "John"
```

### Integration Testing

```python
async def test_user_workflow(client):
    # Create user
    user_data = {"name": "Jane", "email": "jane@example.com"}
    create_response = await client.post("/users", json=user_data)
    assert create_response.status_code == 201
    
    user_id = create_response.json()["id"]
    
    # Get user
    get_response = await client.get(f"/users/{user_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Jane"
    
    # Update user
    update_data = {"name": "Jane Doe"}
    update_response = await client.put(f"/users/{user_id}", json=update_data)
    assert update_response.status_code == 200
    
    # Delete user
    delete_response = await client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204
```

## Performance Considerations

### Async Best Practices

1. **Use async for I/O operations**: Database queries, HTTP requests, file operations
2. **Avoid blocking operations**: Use async alternatives when available
3. **Use connection pooling**: Reuse connections for better performance
4. **Cache expensive operations**: Cache results to avoid repeated computation

### Handler Optimization

1. **Keep handlers lightweight**: Move complex logic to service functions
2. **Use early returns**: Return early when possible to avoid unnecessary processing
3. **Validate inputs early**: Check request data before expensive operations
4. **Use appropriate status codes**: Return correct HTTP status codes for better client handling

## Common Patterns and Examples

### CRUD Operations

```python
# Create
@app.post("/users")
async def create_user(request, response):
    user_data = await request.json
    user = await create_user_in_db(user_data)
    return response.json(user, status_code=201)

# Read
@app.get("/users/{user_id:int}")
async def get_user(request, response):
    user_id = request.path_params.user_id
    user = await get_user_from_db(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return response.json(user)

# Update
@app.put("/users/{user_id:int}")
async def update_user(request, response):
    user_id = request.path_params.user_id
    user_data = await request.json
    user = await update_user_in_db(user_id, user_data)
    return response.json(user)

# Delete
@app.delete("/users/{user_id:int}")
async def delete_user(request, response):
    user_id = request.path_params.user_id
    await delete_user_from_db(user_id)
    return response.json(None, status_code=204)
```

### File Upload Handler

```python
@app.post("/upload")
async def upload_file(request, response):
    # Get uploaded file
    file = await request.file.get("file")
    
    if not file:
        return response.json({"error": "No file provided"}, status_code=400)
    
    # Validate file type
    if not file.filename.endswith(('.jpg', '.png', '.pdf')):
        return response.json({"error": "Invalid file type"}, status_code=400)
    
    # Save file
    file_path = f"uploads/{file.filename}"
    await save_file(file, file_path)
    
    return response.json({
        "message": "File uploaded successfully",
        "filename": file.filename,
        "size": file.size
    })
```

### Search Handler with Pagination

```python
@app.get("/search")
async def search_items(request, response):
    query = request.query_params.get("q", "")
    page = int(request.query_params.get("page", 1))
    limit = int(request.query_params.get("limit", 10))
    
    # Validate parameters
    if page < 1:
        return response.json({"error": "Page must be >= 1"}, status_code=400)
    
    if limit < 1 or limit > 100:
        return response.json({"error": "Limit must be between 1 and 100"}, status_code=400)
    
    # Perform search
    results, total = await search_database(query, page, limit)
    
    return response.json({
        "query": query,
        "page": page,
        "limit": limit,
        "total": total,
        "results": results,
        "has_next": (page * limit) < total,
        "has_prev": page > 1
    })
```

This comprehensive guide covers all aspects of handlers in Nexios, from basic usage to advanced patterns. Handlers are the foundation of your application, and understanding how to write them effectively is crucial for building robust, maintainable web applications.
- [Testing Guide](/guide/testing)

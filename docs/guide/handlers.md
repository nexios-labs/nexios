# Handlers

In Nexios, all route handlers must be async functions. These handlers receive a Request object and return a Response, dict, str, or other supported types.

::: tip  💡Tip
Every Nexios handler must be async def; it's triggered by a route and returns a value that becomes the response.
:::

Example
```py 
from nexios import NexiosApp

app = NexiosApp()

@app.get("/")  
async def index(request, response): 
    return "Hello, world!" 
```

::: warning ⚠️ Warning
Nexios Handler must take at least two arguments: `request` and `response`.
:::

The `request` and `response` objects are provided by Nexios and contain information about the incoming request and the outgoing response.

::: tip  💡Tip
User type annotation for more IDE support .

```py

from nexios.http import Request, Response

@app.get("/")  
async def index(request: Request, response: Response): 
    return "Hello, world!" 
```

:::

For more information, see [Request](/guide/request) and [Response](/guide/response)



You can also use handler with `Routes` class

```py
from nexios.routing import Routes
from nexios import NexiosApp
app = NexiosApp()

async def dynamic_handler(req, res):
    return "Hello, world!"

app.add_route(Routes("/dynamic", dynamic_handler))  # Handles All Methods by default

```

# Request Handlers

Request handlers are the core building blocks of your Nexios application. They process incoming HTTP requests and return appropriate responses.

## Basic Handlers

### Function Handlers

::: code-group
```python [Basic Handler]
from nexios import NexiosApp

app = NexiosApp()

@app.get("/")
async def index(request, response):
    return response.json({
        "message": "Hello, World!"
    })
```

```python [With Parameters]
@app.get("/users/{user_id:int}")
async def get_user(request, response,user_id):
    return response.json({
        "id": user_id,
        "name": "John Doe"
    })
```

```python [With Query Params]
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
:::

### Request Methods

```python
# GET request
@app.get("/items")
async def list_items(request, response):
    return response.json({"items": []})

# POST request
@app.post("/items")
async def create_item(request, response):
    data = await request.json
    return response.json(data, status_code=201)

# PUT request
@app.put("/items/{item_id:int}")
async def update_item(request, response):
    item_id = request.path_params.item_id
    data = await request.json
    return response.json({
        "id": item_id,
        **data
    })

# DELETE request
@app.delete("/items/{item_id:int}")
async def delete_item(request, response):
    item_id = request.path_params.item_id
    return response.json(None, status_code=204)

# PATCH request
@app.patch("/items/{item_id:int}")
async def partial_update(request, response):
    item_id = request.path_params.item_id
    data = await request.json
    return response.json({
        "id": item_id,
        **data
    })

# HEAD request
@app.head("/status")
async def status(request, response):
    response.set_header("X-KEY","Value")
    return response.json(None)

# OPTIONS request
@app.options("/items")
async def options(request, response):
    response.set_header("Allow", "GET, POST, PUT, DELETE")
    return response.json(None)
```

## Request Processing

### Request Information

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
    headers = request.headers
    content_type = headers.get("Content-Type")
    
    # Client info
    client = request.client
    host = client.host
    port = client.port
    
    # State (for middleware)
    state = request.state
    
    return response.json({
        "method": method,
        "path": path,
        "content_type": content_type
    })
```

### Request Body

::: code-group
```python [JSON Data]
@app.post("/api/data")
async def handle_json(request, response):
    data = await request.json
    return response.json(data)
```

```python [Form Data]
@app.post("/api/form")
async def handle_form(request, response):
    form = await request.form
    name = form.get("name")
    email = form.get("email")
    return response.json({
        "name": name,
        "email": email
    })
```

```python [File Upload]
@app.post("/api/upload")
async def handle_upload(request, response):
    files = await request.files
    file = files.get("file")
    
    if file:
        content = await file.read()
        filename = file.filename
        content_type = file.content_type
        
        return response.json({
            "filename": filename,
            "size": len(content),
            "type": content_type
        })
    
    return response.json({
        "error": "No file uploaded"
    }, status_code=400)
```
:::

### Request Validation

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from nexios.validation import validate_request

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

@app.post("/users")
@validate_request(UserCreate)
async def create_user(request, response, data: UserCreate):
    return response.json({
        "username": data.username,
        "email": data.email,
        "full_name": data.full_name
    }, status_code=201)
```

## Response Handling

### Response Types

::: code-group
```python [JSON Response]
@app.get("/api/data")
async def get_data(request, response):
    return response.json({
        "message": "Success",
        "data": {"key": "value"}
    })
```

```python [HTML Response]


@app.get("/page")
async def get_page(request, response):
    return response.html("""
        <html>
            <body>
                <h1>Hello, World!</h1>
            </body>
        </html>
    """)
```

```python [File Response]

@app.get("/download/{filename}")
async def download(request, response):
    filename = request.path_params.filename
    return response.file(
        f"files/{filename}",
        filename=filename
    )
```

```python [Stream Response]


@app.get("/stream")
async def stream_data(request, response):
    async def generate():
        for i in range(10):
            yield f"data: {i}\n\n"
            await asyncio.sleep(1)
    
    return response.file(
        generate(),
     
    )
```
:::

### Response Headers

```python
@app.get("/api/secure")
async def secure_endpoint(request, response):
    # Set security headers
    response.headers.set_headers({
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Cache-Control": "no-store, max-age=0"
    })
    
    return response.json({
        "message": "Secure response"
    })
```

### Status Codes

```python
@app.post("/items")
async def create_item(request, response):
    # 201 Created
    return response.json(
        {"id": 1},
        status_code=201
    )

@app.get("/items/{item_id}")
async def get_item(request, response):
    item_id = request.path_params.item_id
    item = await find_item(item_id)
    
    if not item:
        # 404 Not Found
        return response.json(
            {"error": "Item not found"},
            status_code=404
        )
    
    # 200 OK
    return response.json(item)

@app.put("/items/{item_id}")
async def update_item(request, response):
    try:
        data = await request.json
    except ValueError:
        # 400 Bad Request
        return response.json(
            {"error": "Invalid JSON"},
            status_code=400
        )
    
    # 200 OK
    return response.json(data)
```

## Error Handling

### Exception Handling

```python
from nexios.exceptions import HTTPException

@app.add_exception_handler(HTTPException)
async def http_add_excepti(request, response, exc):
    return response.json({
        "error": exc.detail
    }, status_code=exc.status_code)

@app.add_exception_handler(ValueError)
async def value_error_handler(request, response, exc):
    return response.json({
        "error": str(exc)
    }, status_code=400)

@app.add_exception_handler(Exception)
async def generic_error_handler(request,response, exc):
    return response.json({
        "error": "Internal server error"
    }, status_code=500)

@app.get("/items/{item_id:int}")
async def get_item(request, response):
    item_id = request.path_params.item_id
    if item_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Item ID must be positive"
        )
    return response.json({"id": item_id})
```

### Custom Exceptions

```python
class APIError(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        code: str = None
    ):
        super().__init__(status_code, detail)
        self.code = code

@app.add_exception_handler(APIError)
async def api_error_handler(request,response, exc):
    return response.json({
        "error": exc.detail,
        "code": exc.code
    }, status_code=exc.status_code)

@app.get("/users/{user_id}")
async def get_user(request, response):
    user_id = request.path_params.user_id
    if not is_valid_user(user_id):
        raise APIError(
            status_code=404,
            detail="User not found",
            code="USER_NOT_FOUND"
        )
    return response.json({"id": user_id})
```

## Advanced Features

### Dependency Injection

```python
from nexios import Depend
from typing import Annotated

async def get_db():
    async with Database() as db:
        yield db

async def get_current_user(
    request,
    db=Depend(get_db)
):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(401, "Not authenticated")
    return await get_user_from_token(token, db)

@app.get("/users/me")
async def get_profile(
    request,
    response,
    user=Depend(get_current_user)
):
    return response.json(user)
```


### Request Lifecycle Hooks

```python

@app.on_startup
async def startup():
    # Initialize resources
    pass

@app.on_shutdown
async def shutdown():
    # Cleanup resources
    pass
```

## Testing

### Handler Testing

```python
from nexios.testing import TestClient
import pytest

@pytest.fixture
async def client():
    app = create_test_app()
    async with TestClient(app) as client:
        yield client

async def test_create_user(client):
    response = await client.post(
        "/users",
        json={
            "username": "testuser",
            "email": "test@example.com"
        }
    )
    assert response.status_code == 201
    data = response.json
    assert data["username"] == "testuser"

async def test_get_user(client):
    # Create test user
    user = await create_test_user()
    
    # Test get user
    response = await client.get(f"/users/{user.id}")
    assert response.status_code == 200
    data = response.json
    assert data["id"] == user.id
```

## Best Practices

### Handler Organization

::: tip Best Practices
1. Group related handlers
2. Keep handlers focused
3. Use proper status codes
4. Validate input data
5. Handle errors gracefully
6. Document handlers
7. Test handlers
8. Use type hints
9. Follow naming conventions
10. Implement proper security
:::

### Security Considerations

::: warning Security
1. Validate input
2. Sanitize output
3. Use proper authentication
4. Implement rate limiting
5. Set security headers
6. Use HTTPS
7. Handle errors securely
8. Validate file uploads
9. Prevent CSRF
10. Log security events
:::

## More Information

- [Routing Guide](/guide/routing)
- [Middleware Guide](/guide/middleware)
- [Authentication Guide](/guide/authentication)
- [Database Guide](/guide/database)
- [Testing Guide](/guide/testing)
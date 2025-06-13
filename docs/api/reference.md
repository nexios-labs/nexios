# API Reference

This document provides a comprehensive reference for the Nexios API.

::: warning API Stability
The core API is stable, but some features may change in future versions. Check the changelog for updates.
:::

## Core Components

### NexiosApp

The main application class that handles routing and middleware.

```python
from nexios import NexiosApp

app = NexiosApp(
    title="My API",
    description="API Description",
    version="1.0.0",
    debug=True
)
```

#### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `title` | str | "Nexios API" | API title |
| `description` | str | "" | API description |
| `version` | str | "1.0.0" | API version |
| `debug` | bool | False | Enable debug mode |
| `docs_url` | str | "/docs" | OpenAPI docs URL |
| `redoc_url` | str | "/redoc" | ReDoc URL |
| `openapi_url` | str | "/openapi.json" | OpenAPI schema URL |

### Router

Router for grouping related endpoints.

```python
from nexios import Router

router = Router(
    prefix="/api/v1",
    tags=["v1"],
    responses={401: UnauthorizedError}
)
```

#### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `prefix` | str | "" | Route prefix |
| `tags` | List[str] | [] | OpenAPI tags |
| `responses` | Dict[int, Type] | {} | Common responses |
| `dependencies` | List[Depend] | [] | Route dependencies |

## Request/Response

### Request

The request object provides access to request data.

```python
@app.get("/items")
async def get_items(request, response):
    # Query parameters
    page = request.query_params.get("page", 1)
    
    # Path parameters
    item_id = request.path_params.id
    
    # Headers
    auth = request.headers.get("Authorization")
    
    # Body
    data = await request.json()
    
    # Form data
    form = await request.form()
    
    # Files
    files = await request.files()
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `method` | str | HTTP method |
| `url` | URL | Request URL |
| `headers` | Headers | Request headers |
| `query_params` | QueryParams | Query parameters |
| `path_params` | PathParams | Path parameters |
| `cookies` | Cookies | Request cookies |
| `client` | Client | Client information |
| `state` | State | Request state |

### Response

The response object for sending HTTP responses.

```python
@app.get("/items")
async def get_items(request, response):
    # JSON response
    return response.json({"items": []})
    
    # HTML response
    return response.html("<h1>Hello</h1>")
    
    # File response
    return response.file("file.pdf")
    
    # Stream response
    return response.stream(generate_data())
    
    # Redirect
    return response.redirect("/new-location")
```

#### Methods

| Method | Description |
|--------|-------------|
| `json()` | Send JSON response |
| `html()` | Send HTML response |
| `text()` | Send text response |
| `file()` | Send file response |
| `stream()` | Send stream response |
| `redirect()` | Send redirect response |

## Middleware

### Built-in Middleware

#### CORS

```python
from nexios.middleware import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)
```

#### Authentication

```python
from nexios.middleware import AuthMiddleware

app.add_middleware(
    AuthMiddleware,
    auth_class=JWTAuth,
    exclude_paths=["/public"]
)
```

#### Rate Limiting

```python
from nexios.middleware import RateLimitMiddleware

app.add_middleware(
    RateLimitMiddleware,
    rate_limit=100,
    time_window=60
)
```

### Custom Middleware

```python
from nexios.middleware import Middleware

class CustomMiddleware(Middleware):
    async def process_request(self, request, handler):
        # Pre-processing
        request.custom_data = {}
        
        # Call handler
        response = await handler(request)
        
        # Post-processing
        response.headers["X-Custom"] = "processed"
        
        return response
```

## Database

### Models

```python
from nexios.db import Model, Column, types

class User(Model):
    id = Column(types.Integer, primary_key=True)
    username = Column(types.String, unique=True)
    email = Column(types.String, unique=True)
    created_at = Column(types.DateTime, default=datetime.utcnow)
```

#### Field Types

| Type | Description |
|------|-------------|
| `String` | String field |
| `Integer` | Integer field |
| `Float` | Float field |
| `Boolean` | Boolean field |
| `DateTime` | DateTime field |
| `JSON` | JSON field |
| `Array` | Array field |
| `Enum` | Enum field |

### Queries

```python
# Find one
user = await User.query.filter_by(username="john").first()

# Find many
users = await User.query.filter_by(active=True).all()

# Pagination
users = await User.query.paginate(page=1, limit=10)

# Sorting
users = await User.query.order_by(User.created_at.desc()).all()

# Joins
posts = await Post.query.join(User).filter(User.id == user_id).all()
```

## Authentication

### JWT Authentication

```python
from nexios.auth import JWTAuth

auth = JWTAuth(
    secret_key="your-secret",
    algorithm="HS256",
    access_token_expire=timedelta(minutes=30)
)

@app.post("/login")
async def login(request, response):
    token = auth.create_access_token({"sub": user_id})
    return response.json({"token": token})
```

### OAuth2

```python
from nexios.auth import OAuth2

oauth2 = OAuth2(
    client_id="your-client-id",
    client_secret="your-client-secret",
    authorize_url="https://oauth2.example.com/authorize",
    token_url="https://oauth2.example.com/token"
)

@app.get("/login")
async def login(request, response):
    return response.redirect(oauth2.get_authorize_url())
```

## Validation

### Request Validation

```python
from nexios.validation import validate_params
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

@app.post("/users")
@validate_params(UserCreate)
async def create_user(request, response, data: UserCreate):
    return response.json(data.dict())
```

### Response Validation

```python
from nexios.validation import validate_response

@app.get("/users")
@validate_response(UserResponse)
async def get_users(request, response):
    return response.json({"users": []})
```

## Error Handling

### HTTP Exceptions

```python
from nexios.exceptions import HTTPException

@app.get("/items/{id}")
async def get_item(request, response):
    item = await Item.get(request.path_params.id)
    if not item:
        raise HTTPException(404, "Item not found")
    return response.json(item)
```

### Error Handlers

```python
@app.error_handler(404)
async def not_found(request, response, exc):
    return response.json(
        {"error": "Not found", "detail": str(exc)},
        status_code=404
    )
```

## Testing

### Test Client

```python
from nexios.testing import TestClient

client = TestClient(app)

def test_get_items():
    response = client.get("/items")
    assert response.status_code == 200
    assert "items" in response.json()
```

### Fixtures

```python
import pytest
from nexios.testing import TestClient

@pytest.fixture
def client():
    return TestClient(app)

def test_create_item(client):
    response = client.post("/items", json={"name": "Test"})
    assert response.status_code == 201
```

## Deployment

### ASGI Server

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Docker

```dockerfile
FROM python:3.9

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## CLI

### Available Commands

| Command | Description |
|---------|-------------|
| `nexios new` | Create new project |
| `nexios run` | Run development server |
| `nexios test` | Run tests |
| `nexios migrate` | Run database migrations |
| `nexios generate` | Generate code |

### Configuration

```toml
[tool.nexios]
name = "my-project"
version = "1.0.0"
description = "My Nexios Project"
```

## Best Practices

### Security

- Use HTTPS in production
- Implement proper authentication
- Validate all input
- Use secure headers
- Handle errors properly
- Rate limit endpoints
- Sanitize output

### Performance

- Use connection pooling
- Implement caching
- Optimize database queries
- Use async operations
- Monitor resource usage
- Profile application
- Handle timeouts

### Development

- Write tests
- Use type hints
- Document code
- Follow PEP 8
- Use linting
- Version control
- CI/CD pipeline

::: tip Contributing
Check our [contributing guide](/contributing) for more information on how to contribute to Nexios.
::: 
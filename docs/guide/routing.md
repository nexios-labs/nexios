# Routing 

Nexios provides a powerful and flexible routing system that supports path parameters, query parameters, and various HTTP methods.

## Basic Routing

### HTTP Methods

::: code-group
```python [Basic Routes]
from nexios import NexiosApp

app = NexiosApp()

@app.get("/")
async def index(request, response):
    return response.json({"message": "Hello"})

@app.post("/items")
async def create_item(request, response):
    data = await request.json()
    return response.json(data, status_code=201)

@app.put("/items/{id}")
async def update_item(request, response):
    item_id = request.path_params.id
    data = await request.json()
    return response.json({"id": item_id, **data})

@app.delete("/items/{id}")
async def delete_item(request, response):
    item_id = request.path_params.id
    return response.json(None, status_code=204)
```

```python [Multiple Methods]
@app.route("/items", methods=["GET", "POST"])
async def handle_items(request, response):
    if request.method == "GET":
        return response.json({"items": []})
    elif request.method == "POST":
        data = await request.json()
        return response.json(data, status_code=201)
```

```python [Head/Options]
@app.head("/status")
async def status(request, response):
    response.headers["X-API-Version"] = "1.0"
    return response.json(None)

@app.options("/items")
async def items_options(request, response):
    response.headers["Allow"] = "GET, POST, PUT, DELETE"
    return response.json(None)
```
:::

## Path Parameters

### Parameter Types

::: code-group
```python [Basic Types]
@app.get("/users/{user_id:int}")
async def get_user(request, response):
    user_id = request.path_params.user_id  # Automatically converted to int
    return response.json({"id": user_id})

@app.get("/files/{filename:str}")
async def get_file(request, response):
    filename = request.path_params.filename
    return response.json({"file": filename})

@app.get("/items/{item_id:uuid}")
async def get_item(request, response):
    item_id = request.path_params.item_id  # UUID object
    return response.json({"id": str(item_id)})
```

```python [Custom Types]
from nexios.types import PathParam
from datetime import datetime

class DateParam(PathParam):
    async def convert(self, value: str) -> datetime:
        return datetime.strptime(value, "%Y-%m-%d")

@app.get("/events/{date:date}")
async def get_events(request, response):
    date = request.path_params.date  # datetime object
    return response.json({"date": date.isoformat()})
```

```python [Regex Patterns]
@app.get("/users/{username:str(pattern=[a-zA-Z0-9_-]+)}")
async def get_user_by_username(request, response):
    username = request.path_params.username
    return response.json({"username": username})

@app.get("/products/{sku:str(pattern=[A-Z]{2}\d{6})}")
async def get_product(request, response):
    sku = request.path_params.sku
    return response.json({"sku": sku})
```
:::

### Available Parameter Types

| Type | Description | Example |
|------|-------------|---------|
| `str` | String (default) | `{name:str}` |
| `int` | Integer | `{id:int}` |
| `float` | Floating point | `{price:float}` |
| `bool` | Boolean | `{active:bool}` |
| `uuid` | UUID | `{id:uuid}` |
| `path` | Full path including slashes | `{path:path}` |
| `date` | Date (custom type) | `{date:date}` |
| `datetime` | DateTime (custom type) | `{dt:datetime}` |

## Query Parameters

### Basic Usage

::: code-group
```python [Optional Params]
@app.get("/users")
async def list_users(request, response):
    page = request.query_params.get("page", 1)
    limit = request.query_params.get("limit", 10)
    sort = request.query_params.get("sort", "id")
    return response.json({
        "page": int(page),
        "limit": int(limit),
        "sort": sort
    })
```

```python [Required Params]
from nexios.exceptions import HTTPException

@app.get("/search")
async def search(request, response):
    query = request.query_params.get("q")
    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search query is required"
        )
    return response.json({"query": query})
```

```python [Multiple Values]
@app.get("/filter")
async def filter_items(request, response):
    tags = request.query_params.getlist("tag")
    return response.json({"tags": tags})
```
:::

### Parameter Validation

```python
from nexios.validation import QueryParam, validate_params

class PaginationParams:
    page: int = QueryParam(ge=1, default=1)
    limit: int = QueryParam(ge=1, le=100, default=10)
    sort: str = QueryParam(regex="^[a-zA-Z_]+$", default="id")

@app.get("/items")
@validate_params(PaginationParams)
async def list_items(request, response, params: PaginationParams):
    return response.json({
        "page": params.page,
        "limit": params.limit,
        "sort": params.sort
    })
```

## Route Groups

### Using Routers

::: code-group
```python [Basic Router]
from nexios import Router

router = Router(prefix="/api/v1")

@router.get("/users")
async def list_users(request, response):
    return response.json({"users": []})

@router.post("/users")
async def create_user(request, response):
    data = await request.json()
    return response.json(data, status_code=201)

# In main.py
app.mount_router(router)
```

```python [Nested Routers]
users_router = Router(prefix="/users")
posts_router = Router(prefix="/posts")

@users_router.get("/{user_id}/posts")
async def get_user_posts(request, response):
    user_id = request.path_params.user_id
    return response.json({"user_id": user_id, "posts": []})

api_v1 = Router(prefix="/api/v1")
api_v1.mount_router(users_router)
api_v1.mount_router(posts_router)

app.mount_router(api_v1)
```

```python [With Tags]
router = Router(
    prefix="/admin",
    tags=["admin"],
    responses={401: PyDanticModel}
)

@router.get("/stats")
async def admin_stats(request, response):
    return response.json({"stats": {}})
```
:::

### Route Dependencies

```python
from nexios import Depend
from nexios.auth import requires_auth

async def get_current_user(request):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(401, "Not authenticated")
    return await get_user_from_token(token)

router = Router(
    prefix="/admin",
    dependencies=[Depend(get_current_user)]
)

@router.get("/dashboard")
async def admin_dashboard(request, response):
    return response.json({"dashboard": "data"})
```

## Advanced Routing

### Route Metadata

```python
@app.get(
    "/items/{id}",
    name="get_item",
    description="Get item by ID",
    tags=["items"],
    responses={
        200: {"description": "Item found"},
        404: {"description": "Item not found"}
    },
    deprecated=False
)
async def get_item(request, response):
    return response.json({"id": request.path_params.id})
```

### Custom Route Classes

```python
from nexios.routing import Route

class RateLimitedRoute(Route):
    def __init__(self, path, handler, **kwargs):
        super().__init__(path, handler, **kwargs)
        self.rate_limit = kwargs.get("rate_limit", 100)

    async def handle(self, request, response):
        # Check rate limit
        if await self.is_rate_limited(request):
            raise HTTPException(429, "Too many requests")
        return await super().handle(request, response)

@app.route("/limited", route_class=RateLimitedRoute, rate_limit=50)
async def limited_endpoint(request, response):
    return response.json({"message": "Rate limited endpoint"})
```

### URL Generation

```python
@app.get("/users/{user_id}/posts/{post_id}", name="user_post")
async def get_user_post(request, response):
    return response.json({})

# Generate URL
url = app.url_for(
    "user_post",
    user_id=123,
    post_id=456,
    query={"version": "1"}
)
# Result: /users/123/posts/456?version=1
```

## Best Practices

::: tip Route Organization
1. Group related routes using Routers
2. Use meaningful route names
3. Document routes with metadata
4. Keep route handlers focused
5. Use type hints for parameters
:::

### Route Structure

```python
# routes/users.py
from nexios import Router
from .models import User
from .schemas import UserCreate, UserUpdate
from nexios.openapi import Query
router = Router(prefix="/users", tags=["users"])

@router.get("/",parameters = [Query(name = "page"),Query(name = "limit")])
async def list_users(
    request,
    response
):
    """List users with pagination."""
    page = request.query_params.get("page")
    limit = request.query_params.get("limit")

    users = await User.paginate(page, limit)
    return response.json(users)

@router.post("/")
async def create_user(
    request,
    response,
):
    """Create a new user."""
    data = await request.json
    user = await User.create(**data)
    return response.json(user, status_code=201)

@router.get("/{user_id:int}")
async def get_user(request, response):
    """Get user by ID."""
    user = await User.get_or_404(
        request.path_params.user_id
    )
    return response.json(user)

@router.put("/{user_id:int}")
async def update_user(
    request,
    response,
    data: UserUpdate = Body()
):
    """Update user by ID."""
    user = await User.get_or_404(
        request.path_params.user_id
    )
    await user.update(**data.dict())
    return response.json(user)

@router.delete("/{user_id:int}")
async def delete_user(request, response):
    """Delete user by ID."""
    user = await User.get_or_404(
        request.path_params.user_id
    )
    await user.delete()
    return response.json(None, status_code=204)
```

### Error Handling

```python
from nexios.exceptions import HTTPException

@app.add_exception_handler(HTTPException)
async def http_exception_handler(request,response, exc):
    return response.json(
        {
            "error": exc.detail,
            "code": exc.status_code
        },
        status_code=exc.status_code
    )

@app.add_exception_handler(Exception)
async def generic_exception_handler(request,response, exc):
    return response.json(
        {
            "error": "Internal server error",
            "detail": str(exc) if app.debug else None
        },
        status_code=500
    )
```

## Testing Routes

::: tip Testing
Use the test client for easy route testing:
:::

```python
from nexios.testing import Client

async def test_get_user():
    client = Client(app)
    
    # Test successful request
    response = await client.get("/users/123")
    assert response.status_code == 200
    assert response.json()["id"] == 123
    
    # Test not found
    response = await client.get("/users/999")
    assert response.status_code == 404
    
    # Test create user
    response = await client.post(
        "/users",
        json={"name": "Test User"}
    )
    assert response.status_code == 201
```

## Performance Tips

::: warning Route Performance
1. Keep route handlers lightweight
2. Use async database operations
3. Implement caching where appropriate
4. Use connection pooling
5. Profile route performance
:::

```python
from nexios.cache import cached

@app.get("/expensive")
@cached(ttl=300)  # Cache for 5 minutes
async def expensive_operation(request, response):
    result = await compute_expensive_result()
    return response.json(result)
```

## More Information

- [API Reference](/api/routing)
- [Middleware Guide](/guide/middleware)
- [Authentication](/guide/authentication)
- [Database Integration](/guide/database)
- [WebSockets](/guide/websockets/)

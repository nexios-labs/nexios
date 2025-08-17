# Routing

Nexios provides a powerful and flexible routing system that supports path parameters, query parameters, and various HTTP methods. The routing system is designed to be intuitive, performant, and extensible.

::: tip Routing Fundamentals
Routing in Nexios follows these principles:

- **Declarative**: Routes are defined using decorators or the Routes class
- **Type-safe**: Path parameters are automatically converted to the correct type
- **Flexible**: Support for complex URL patterns and custom converters
- **Performant**: Fast route matching with optimized algorithms
- **Extensible**: Easy to add custom path converters and middleware
- **Modular**: Support for routers and route grouping
  :::

## Basic Routing

::: code-group

```python [Basic Routes]
from nexios import NexiosApp

app = NexiosApp()

@app.get("/")
async def index(request, response):
    return response.json({"message": "Hello"})

@app.post("/items")
async def create_item(request, response):
    data = await request.json
    return response.json(data, status_code=201)

@app.put("/items/{id}")
async def update_item(request, response):
    item_id = request.path_params.id
    data = await request.json
    return response.json({"id": item_id, **data})

@app.delete("/items/{id}")
async def delete_item(request, response):
    item_id = request.path_params.id
    return response.json(None, status_code=204)

# If a required path parameter is missing or invalid, Nexios will return a 422 error.
# For example, GET /items/abc (when id is expected as int) will return a validation error.

# If you define two routes with the same path and method, Nexios will raise a conflict error at startup.
```

```python [Multiple Methods]
@app.route("/items", methods=["GET", "POST"])
async def handle_items(request, response):
    if request.method == "GET":
        return response.json({"items": []})
    elif request.method == "POST":
        data = await request.json
        return response.json(data, status_code=201)

# If you send a request with an unsupported method, Nexios will return a 405 Method Not Allowed.
```

```python [Head/Options]
@app.head("/status")
async def status(request, response):
    response.header("X-API-Version", "1.0")
    return response.json(None)

@app.options("/items")
async def items_options(request, response):
    response.header("Allow", "GET, POST, PUT, DELETE")
    return response.json(None)

# If you forget to return a response, Nexios will raise an error indicating the handler did not return a response object.
```

:::

## The `Routes` Class

The `Routes` class is the fundamental building block of Nexios routing. It encapsulates all routing information for an API endpoint, including path handling, validation, OpenAPI documentation, and request processing.

```python
from nexios.routing import Routes

# Basic route creation
route = Routes(
    path="/users/{user_id:int}",
    handler=get_user_handler,
    methods=["GET"],
    name="get_user",
    summary="Get user by ID",
    description="Retrieves a user by their unique identifier"
)
```

## `Routes` Class Constructor

The `Routes` constructor is used to define a route within the Nexios application. It takes several parameters:

- **path**: A string that specifies the URL path pattern. It can include path parameters with type annotations, like `/users/{user_id:int}`.
- **handler**: An optional request handler function that processes incoming requests matching the route.
- **methods**: A list of HTTP methods (e.g., `["GET", "POST"]`) that the route accepts. If not specified, it defaults to `["GET"]`.
- **name**: An optional name for the route, used for URL generation.
- **summary**: A brief description of the endpoint, useful for documentation.
- **description**: A detailed explanation of the endpoint's functionality.
- **responses**: A dictionary that maps HTTP status codes to response schemas.
- **request_model**: An optional Pydantic model for validating and parsing request data.
- **middleware**: A list of middleware functions specific to the route.
- **tags**: A list of OpenAPI tags for categorizing the endpoint in documentation.
- **security**: A list of security requirements for accessing the route.
- **operation_id**: A unique identifier for the operation, useful for documentation and client generation.
- **deprecated**: A boolean indicating whether the route is deprecated.
- **parameters**: A list of additional OpenAPI parameters for the route.
- **exclude_from_schema**: A boolean indicating whether to exclude the route from OpenAPI documentation.
- **kwargs**: Additional metadata for the route.

```python
Routes(
    path: str,                                    # URL path pattern
    handler: Optional[HandlerType] = None,        # Request handler function
    methods: Optional[List[str]] = None,          # HTTP methods (default: ["GET"])
    name: Optional[str] = None,                   # Route name for URL generation
    summary: Optional[str] = None,                # Brief endpoint summary
    description: Optional[str] = None,            # Detailed endpoint description
    responses: Optional[Dict[int, Any]] = None,   # Response schemas by status code
    request_model: Optional[Type[BaseModel]] = None,  # Pydantic model for validation
    middleware: List[Any] = [],                   # Route-specific middleware
    tags: Optional[List[str]] = None,             # OpenAPI tags for grouping
    security: Optional[List[Dict[str, List[str]]]] = None,  # Security requirements
    operation_id: Optional[str] = None,           # Unique operation identifier
    deprecated: bool = False,                     # Mark as deprecated
    parameters: List[Parameter] = [],             # Additional OpenAPI parameters
    exclude_from_schema: bool = False,            # Hide from OpenAPI docs
    **kwargs: Dict[str, Any]                      # Additional metadata
)
```

## The `Router` Class

The `Router` class allows you to group related routes together and apply common configuration to all routes in the group.

```python
from nexios.routing import Router

# Create a router with prefix and common configuration
user_router = Router(
    prefix="/users",
    tags=["Users"],
    responses={401: {"description": "Unauthorized"}}
)

# Add routes to the router
@user_router.get("/")
async def list_users(request, response):
    return response.json({"users": []})

@user_router.post("/")
async def create_user(request, response):
    data = await request.json
    return response.json(data, status_code=201)

# Mount the router to the main app
app.mount_router(user_router)
```

### Router Class Constructor

```python
Router(
    prefix: Optional[str] = None,                 # URL prefix for all routes
    routes: Optional[List[Routes]] = None,        # Initial routes to add
    tags: Optional[List[str]] = None,             # Default tags for all routes
    exclude_from_schema: bool = False,            # Hide all routes from docs
    name: Optional[str] = None                    # Router name
)
```

::: tip HTTP Method Best Practices

- **GET**: For retrieving data (should be idempotent)
- **POST**: For creating new resources
- **PUT**: For replacing entire resources (idempotent)
- **PATCH**: For partial updates to resources
- **DELETE**: For removing resources
- **HEAD**: For metadata without body
- **OPTIONS**: For CORS preflight requests
  :::

## Advanced Route Registration

## Using `app.add_route()`

The `app.add_route()` method provides the most flexible way to register routes, allowing you to specify all route configuration options.

```python
from nexios import NexiosApp
from nexios.routing import Routes

app = NexiosApp()

# Method 1: Pass a Routes instance
async def get_user_handler(request, response):
    user_id = request.path_params.user_id
    return response.json({"id": user_id, "name": "John Doe"})

route = Routes(
    path="/users/{user_id:int}",
    handler=get_user_handler,
    methods=["GET"],
    name="get_user",
    summary="Get user by ID",
    description="Retrieves a user by their unique identifier",
    tags=["Users"],
    responses={
        200: UserResponse,
        404: ErrorResponse
    }
)

app.add_route(route)

# Method 2: Pass individual parameters
async def create_user_handler(request, response):
    data = await request.json
    return response.json(data, status_code=201)

app.add_route(
    path="/users",
    handler=create_user_handler,
    methods=["POST"],
    name="create_user",
    summary="Create new user",
    tags=["Users"],
    responses={
        201: UserResponse,
        400: ErrorResponse
    }
)
```

### `app.add_route()` Parameters

```python
app.add_route(
    route: Optional[Union[Routes, type[BaseRoute]]] = None,  # Routes instance
    path: Optional[str] = None,                              # URL path pattern
    methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
    handler: Optional[HandlerType] = None,                   # Handler function
    name: Optional[str] = None,                              # Route name
    summary: Optional[str] = None,                           # Brief summary
    description: Optional[str] = None,                       # Detailed description
    responses: Optional[Dict[int, Any]] = None,              # Response schemas
    request_model: Optional[Type[BaseModel]] = None,         # Request validation model
    middleware: List[Any] = [],                              # Route middleware
    tags: Optional[List[str]] = None,                        # OpenAPI tags
    security: Optional[List[Dict[str, List[str]]]] = None,   # Security requirements
    operation_id: Optional[str] = None,                      # Operation ID
    deprecated: bool = False,                                # Mark as deprecated
    parameters: List[Parameter] = [],                        # Additional parameters
    exclude_from_schema: bool = False,                       # Hide from docs
    **kwargs: Dict[str, Any]                                 # Additional metadata
)
```

::: tip When to Use `app.add_route()`

- **Dynamic Route Creation**: When routes need to be created programmatically
- **Complex Configuration**: When you need full control over route options
- **Route Factories**: When generating routes from data or configuration
- **Testing**: When you need to test route registration logic
- **Plugins**: When building plugins that register routes
  :::

## Path Parameters

## Parameter Types

Nexios provides several built-in path converters for validating and converting URL parameters:

::: code-group

```python [Basic Types]
@app.get("/users/{user_id:int}")
async def get_user(request, response):
    user_id = request.path_params.user_id  # Automatically converted to int
    return response.json({"id": user_id})

# If user_id is not an integer, Nexios will return a 422 error.

@app.get("/files/{filename:str}")
async def get_file(request, response):
    filename = request.path_params.filename
    return response.json({"file": filename})

@app.get("/items/{item_id:uuid}")
async def get_item(request, response):
    item_id = request.path_params.item_id  # UUID object
    return response.json({"id": str(item_id)})

# If item_id is not a valid UUID, Nexios will return a 422 error.
```

```python [Path and Slug]
@app.get("/static/{filepath:path}")
async def get_static_file(request, response):
    filepath = request.path_params.filepath  # Can contain slashes
    return response.json({"path": filepath})

@app.get("/posts/{slug:slug}")
async def get_post(request, response):
    slug = request.path_params.slug  # URL-friendly string
    return response.json({"slug": slug})

# If the slug does not match the expected pattern, Nexios will return a 422 error.
```

```python [Numeric Types]
@app.get("/products/{price:float}")
async def get_product(request, response):
    price = request.path_params.price  # Float value
    return response.json({"price": price})

@app.get("/orders/{order_id:int}")
async def get_order(request, response):
    order_id = request.path_params.order_id  # Integer value
    return response.json({"order_id": order_id})

# If price or order_id are not valid numbers, Nexios will return a 422 error.
```

:::

### Available Converters

| Converter | Type    | Pattern                                                                           | Description                  |
| --------- | ------- | --------------------------------------------------------------------------------- | ---------------------------- |
| `str`     | String  | `[^/]+`                                                                           | Any string without slashes   |
| `path`    | String  | `.*`                                                                              | Any string including slashes |
| `int`     | Integer | `[0-9]+`                                                                          | Positive integers            |
| `float`   | Float   | `[0-9]+(\.[0-9]+)?`                                                               | Positive floats              |
| `uuid`    | UUID    | `[0-9a-fA-F]{8}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{12}` | UUID format                  |
| `slug`    | String  | `[a-z0-9]+(?:-[a-z0-9]+)*`                                                        | URL-friendly strings         |

## Custom Path Converters

You can create and register custom path converters by subclassing the `Convertor` class:

```python
from nexios.converters import Convertor, register_url_convertor
import re

class EmailConvertor(Convertor[str]):
    regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    def convert(self, value: str) -> str:
        if not re.fullmatch(self.regex, value):
            raise ValueError(f"Invalid email format: {value}")
        return value

    def to_string(self, value: str) -> str:
        if not re.fullmatch(self.regex, value):
            raise ValueError(f"Invalid email format: {value}")
        return value

# Register the custom converter
register_url_convertor("email", EmailConvertor())

# Use the custom converter in routes
@app.get("/users/{email:email}")
async def get_user_by_email(request, response):
    email = request.path_params.email
    return response.json({"email": email})

# If your custom converter raises a ValueError, Nexios will return a 422 error with your message.
```

### Creating Custom Converters

To create a custom converter:

1. Subclass `Convertor` with the desired type:

```python
class MyConvertor(Convertor[YourType]):
    regex = "your-regex-pattern"
```

2. Implement the required methods:

   - `convert(self, value: str) -> YourType`: Converts string to your type
   - `to_string(self, value: YourType) -> str`: Converts your type to string

3. Register the converter:

```python
register_url_convertor("converter_name", MyConvertor())
```

### Example: Version Converter

```python
class VersionConvertor(Convertor[str]):
    regex = r"v[0-9]+(\.[0-9]+)*"

    def convert(self, value: str) -> str:
        if not re.fullmatch(self.regex, value):
            raise ValueError(f"Invalid version format: {value}")
        return value

    def to_string(self, value: str) -> str:
        if not re.fullmatch(self.regex, value):
            raise ValueError(f"Invalid version format: {value}")
        return value

register_url_convertor("version", VersionConvertor())

@app.get("/api/{version:version}/users")
async def get_users(request, response):
    version = request.path_params.version
    return response.json({"version": version})
```

::: warning Converter Registration
Custom converters must be registered before they can be used in routes. It's recommended to register them during application startup.
:::

::: tip Best Practices
When creating custom converters:

1. Use clear and efficient regex patterns
2. Validate input in both `convert` and `to_string` methods
3. Provide meaningful error messages
4. Consider performance implications
5. Test thoroughly with edge cases
   :::

## Router Organization

## Creating and Using Routers

Routers allow you to organize related routes and apply common configuration:

```python
from nexios.routing import Router

# Create routers for different API versions
v1_router = Router(prefix="/api/v1", tags=["API v1"])
v2_router = Router(prefix="/api/v2", tags=["API v2"])

# Add routes to v1 router
@v1_router.get("/users")
async def list_users_v1(request, response):
    return response.json({"version": "v1", "users": []})

@v1_router.post("/users")
async def create_user_v1(request, response):
    data = await request.json
    return response.json({"version": "v1", "user": data}, status_code=201)

# Add routes to v2 router
@v2_router.get("/users")
async def list_users_v2(request, response):
    return response.json({"version": "v2", "users": []})

@v2_router.post("/users")
async def create_user_v2(request, response):
    data = await request.json
    return response.json({"version": "v2", "user": data}, status_code=201)

# Mount routers to main app
app.mount_router(v1_router)
app.mount_router(v2_router)
```

## Nested Routers

You can create nested routers for complex API structures:

```python
# Create main API router
api_router = Router(prefix="/api", tags=["API"])

# Create version-specific routers
v1_router = Router(prefix="/v1", tags=["v1"])
v2_router = Router(prefix="/v2", tags=["v2"])

# Create resource-specific routers
users_router = Router(prefix="/users", tags=["Users"])
posts_router = Router(prefix="/posts", tags=["Posts"])

# Add routes to resource routers
@users_router.get("/")
async def list_users(request, response):
    return response.json({"users": []})

@users_router.get("/{user_id:int}")
async def get_user(request, response):
    user_id = request.path_params.user_id
    return response.json({"id": user_id})

@posts_router.get("/")
async def list_posts(request, response):
    return response.json({"posts": []})

@posts_router.get("/{post_id:int}")
async def get_post(request, response):
    post_id = request.path_params.post_id
    return response.json({"id": post_id})

# Mount resource routers to version routers
v1_router.mount_router(users_router)
v1_router.mount_router(posts_router)
v2_router.mount_router(users_router)
v2_router.mount_router(posts_router)

# Mount version routers to API router
api_router.mount_router(v1_router)
api_router.mount_router(v2_router)

# Mount API router to main app
app.mount_router(api_router)
```

This creates the following URL structure:

- `/api/v1/users/` - List users (v1)
- `/api/v1/users/{user_id}` - Get user (v1)
- `/api/v1/posts/` - List posts (v1)
- `/api/v1/posts/{post_id}` - Get post (v1)
- `/api/v2/users/` - List users (v2)
- `/api/v2/users/{user_id}` - Get user (v2)
- `/api/v2/posts/` - List posts (v2)
- `/api/v2/posts/{post_id}` - Get post (v2)

## Router with Middleware

You can apply middleware to all routes in a router:

```python
from nexios.middleware import CORSMiddleware

# Create router with middleware
admin_router = Router(
    prefix="/admin",
    tags=["Admin"],
    middleware=[CORSMiddleware()]
)

@admin_router.get("/dashboard")
async def admin_dashboard(request, response):
    return response.json({"dashboard": "data"})

@admin_router.get("/users")
async def admin_users(request, response):
    return response.json({"users": []})

# All routes in admin_router will have CORS middleware applied
app.mount_router(admin_router)

# If your middleware raises an exception, the request will be interrupted and a 500 error will be returned. Use try/except in middleware for graceful error handling.
```

## Route Metadata and Documentation

### Using Pydantic Models for Responses

Nexios provides excellent integration with Pydantic models for response documentation and validation. Using Pydantic models instead of dictionaries provides:

- **Type Safety**: Compile-time type checking
- **Automatic Documentation**: OpenAPI schemas are generated automatically
- **Validation**: Response data can be validated against the model
- **IDE Support**: Better autocomplete and error detection
- **Consistency**: Standardized response formats across your API

#### Basic Response Models

```python
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Basic response models
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    age: Optional[int] = None
    created_at: datetime
    is_active: bool = True

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    per_page: int

class ErrorResponse(BaseModel):
    error: str
    code: str
    details: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SuccessResponse(BaseModel):
    message: str
    data: Optional[dict] = None

# Use in routes
@app.get(
    "/users/{user_id:int}",
    responses={
        200: UserResponse,
        404: ErrorResponse
    }
)
async def get_user(request, response):
    user_id = request.path_params.user_id
    return response.json({
        "id": user_id,
        "name": "John Doe",
        "email": "john@example.com",
        "created_at": datetime.utcnow(),
        "is_active": True
    })

@app.get(
    "/users",
    responses={
        200: UserListResponse,
        400: ErrorResponse
    }
)
async def list_users(request, response):
    return response.json({
        "users": [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
        ],
        "total": 1,
        "page": 1,
        "per_page": 10
    })
```

#### Advanced Response Models

```python
from pydantic import BaseModel, Field, validator
from typing import Union, Literal

# Union types for different response scenarios
class UserCreatedResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    message: Literal["User created successfully"]

class UserUpdatedResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    message: Literal["User updated successfully"]

class UserDeletedResponse(BaseModel):
    message: Literal["User deleted successfully"]
    deleted_id: int

# Generic response wrapper
class ApiResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    meta: Optional[dict] = None

# Use union types for different status codes
@app.post(
    "/users",
    responses={
        201: UserCreatedResponse,
        400: ErrorResponse,
        409: ErrorResponse
    }
)
async def create_user(request, response):
    data = await request.json
    # ... create user logic
    return response.json({
        "id": 1,
        "name": data["name"],
        "email": data["email"],
        "message": "User created successfully"
    }, status_code=201)

@app.delete(
    "/users/{user_id:int}",
    responses={
        200: UserDeletedResponse,
        404: ErrorResponse
    }
)
async def delete_user(request, response):
    user_id = request.path_params.user_id
    # ... delete user logic
    return response.json({
        "message": "User deleted successfully",
        "deleted_id": user_id
    })
```

#### Response Model Inheritance

```python
# Base models for common fields
class BaseUser(BaseModel):
    id: int
    name: str
    email: EmailStr

class BaseResponse(BaseModel):
    success: bool
    message: str

# Inherit from base models
class UserDetailResponse(BaseUser):
    age: Optional[int] = None
    bio: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class UserSummaryResponse(BaseUser):
    is_active: bool

class ApiSuccessResponse(BaseResponse):
    data: Optional[dict] = None

class ApiErrorResponse(BaseResponse):
    error_code: str
    details: Optional[dict] = None

# Use inherited models
@app.get(
    "/users/{user_id:int}",
    responses={
        200: UserDetailResponse,
        404: ApiErrorResponse
    }
)
async def get_user_detail(request, response):
    # ... implementation
    pass

@app.get(
    "/users",
    responses={
        200: List[UserSummaryResponse],
        400: ApiErrorResponse
    }
)
async def list_users_summary(request, response):
    # ... implementation
    pass
```

#### Response Model with Computed Fields

```python
from pydantic import BaseModel, computed_field

class UserWithStats(BaseModel):
    id: int
    name: str
    email: EmailStr
    posts_count: int
    followers_count: int

    @computed_field
    @property
    def total_engagement(self) -> int:
        return self.posts_count + self.followers_count

    @computed_field
    @property
    def engagement_rate(self) -> float:
        return self.total_engagement / max(self.followers_count, 1)

@app.get(
    "/users/{user_id:int}/stats",
    responses={
        200: UserWithStats,
        404: ErrorResponse
    }
)
async def get_user_stats(request, response):
    user_id = request.path_params.user_id
    # ... fetch user stats
    return response.json({
        "id": user_id,
        "name": "John Doe",
        "email": "john@example.com",
        "posts_count": 25,
        "followers_count": 1000
        # total_engagement and engagement_rate are computed automatically
    })
```

## OpenAPI Integration

Nexios automatically generates OpenAPI documentation from your routes:

```python
from pydantic import BaseModel
from typing import Optional

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None

class ErrorResponse(BaseModel):
    error: str
    code: str
    details: Optional[dict] = None

@app.get(
    "/users/{user_id:int}",
    name="get_user",
    summary="Get user by ID",
    description="Retrieves a user by their unique identifier. Returns user details including profile information.",
    tags=["Users"],
    responses={
        200: UserResponse,
        404: ErrorResponse,
        500: ErrorResponse
    },
    deprecated=False
)
async def get_user(request, response):
    user_id = request.path_params.user_id
    return response.json({"id": user_id, "name": "John Doe", "email": "john@example.com"})
```

## Request Validation

You can use Pydantic models for request validation:

```python
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None

class ErrorResponse(BaseModel):
    error: str
    code: str
    details: Optional[dict] = None

@app.post(
    "/users",
    request_model=UserCreate,
    summary="Create new user",
    responses={
        201: UserResponse,
        400: ErrorResponse
    }
)
async def create_user(request, response):
    data = await request.json
    # Data is automatically validated against UserCreate model
    return response.json(data, status_code=201)

@app.patch(
    "/users/{user_id:int}",
    request_model=UserUpdate,
    summary="Update user",
    responses={
        200: UserResponse,
        404: ErrorResponse
    }
)
async def update_user(request, response):
    user_id = request.path_params.user_id
    data = await request.json
    # Data is automatically validated against UserUpdate model
    return response.json({"id": user_id, **data})
```

## Security Requirements

You can specify security requirements for routes:

```python
@app.get(
    "/admin/users",
    security=[{"BearerAuth": []}],
    tags=["Admin"],
    summary="List all users (Admin only)",
    responses={
        200: list[UserResponse],
        401: ErrorResponse,
        403: ErrorResponse
    }
)
async def admin_list_users(request, response):
    return response.json({"users": []})

@app.post(
    "/users/login",
    security=[],  # No security required
    tags=["Authentication"],
    summary="User login",
    responses={
        200: {"token": str},
        401: ErrorResponse
    }
)
async def login(request, response):
    return response.json({"token": "jwt_token"})
```

## URL Generation

## Using Route Names

You can generate URLs using route names:

```python
@app.get("/users/{user_id:int}", name="get_user")
async def get_user(request, response):
    user_id = request.path_params.user_id
    return response.json({"id": user_id})

@app.get("/posts/{post_id:int}", name="get_post")
async def get_post(request, response):
    post_id = request.path_params.post_id
    return response.json({"id": post_id})

# Generate URLs
user_url = app.url_for("get_user", user_id=123)
post_url = app.url_for("get_post", post_id=456)

print(user_url)  # /users/123
print(post_url)  # /posts/456
```

## URL Generation with Query Parameters

```python
from nexios.structs import URLPath

@app.get("/search", name="search")
async def search(request, response):
    query = request.query_params.get("q", "")
    return response.json({"query": query})

# Generate URL with query parameters
search_url = app.url_for("search", q="python", page=1)
print(search_url)  # /search?q=python&page=1

# You can also build URLs manually
url = URLPath("/users/123")
url = url.add_query_params(page=1, limit=10)
print(url)  # /users/123?page=1&limit=10
```

## Advanced Routing Patterns

## Route Factories

You can create routes programmatically:

```python
def create_crud_routes(resource_name: str, model_class):
    """Create CRUD routes for a resource"""

    routes = []

    # List route
    async def list_handler(request, response):
        items = await model_class.all()
        return response.json({f"{resource_name}": items})

    routes.append(Routes(
        path=f"/{resource_name}",
        handler=list_handler,
        methods=["GET"],
        name=f"list_{resource_name}",
        summary=f"List all {resource_name}",
        tags=[resource_name.title()],
        responses={
            200: List[model_class.ResponseModel],
            400: ErrorResponse
        }
    ))

    # Create route
    async def create_handler(request, response):
        data = await request.json
        item = await model_class.create(**data)
        return response.json(item, status_code=201)

    routes.append(Routes(
        path=f"/{resource_name}",
        handler=create_handler,
        methods=["POST"],
        name=f"create_{resource_name}",
        summary=f"Create new {resource_name}",
        tags=[resource_name.title()],
        responses={
            201: model_class.ResponseModel,
            400: ErrorResponse,
            409: ErrorResponse
        }
    ))

    # Get route
    async def get_handler(request, response):
        item_id = request.path_params.id
        item = await model_class.get(item_id)
        return response.json(item)

    routes.append(Routes(
        path=f"/{resource_name}/{{id:int}}",
        handler=get_handler,
        methods=["GET"],
        name=f"get_{resource_name}",
        summary=f"Get {resource_name} by ID",
        tags=[resource_name.title()],
        responses={
            200: model_class.ResponseModel,
            404: ErrorResponse
        }
    ))

    return routes

# Example model class with response model
class UserModel:
    class ResponseModel(BaseModel):
        id: int
        name: str
        email: str
        created_at: datetime

    @classmethod
    async def all(cls):
        # Implementation
        pass

    @classmethod
    async def create(cls, **data):
        # Implementation
        pass

    @classmethod
    async def get(cls, id: int):
        # Implementation
        pass

# Use the factory
user_routes = create_crud_routes("users", UserModel)
post_routes = create_crud_routes("posts", PostModel)

# Add all routes
for route in user_routes + post_routes:
    app.add_route(route)
```

## Conditional Routes

You can create routes conditionally based on configuration:

```python
# Only add admin routes in development
if app.config.debug:
    @app.get("/admin/debug", name="debug_info")
    async def debug_info(request, response):
        return response.json({
            "config": app.config.to_dict(),
            "routes": [r.raw_path for r in app.get_all_routes()]
        })

# Add feature flags
if app.config.get("enable_analytics"):
    @app.get("/analytics", name="analytics")
    async def analytics(request, response):
        return response.json({"analytics": "data"})
```

## Dynamic Route Registration

You can register routes dynamically:

```python
# Load routes from configuration
routes_config = [
    {
        "path": "/api/v1/users",
        "methods": ["GET"],
        "handler": "user_handlers.list_users",
        "name": "list_users"
    },
    {
        "path": "/api/v1/users/{user_id:int}",
        "methods": ["GET"],
        "handler": "user_handlers.get_user",
        "name": "get_user"
    }
]

# Register routes dynamically
for route_config in routes_config:
    # Import handler dynamically
    module_name, handler_name = route_config["handler"].rsplit(".", 1)
    module = __import__(module_name, fromlist=[handler_name])
    handler = getattr(module, handler_name)

    route = Routes(
        path=route_config["path"],
        handler=handler,
        methods=route_config["methods"],
        name=route_config["name"]
    )

    app.add_route(route)

# If a dynamically imported handler does not exist or fails to import, Nexios will raise an ImportError at startup.
```

## Route Testing and Debugging

## Getting All Routes

You can inspect all registered routes:

```python
# Get all routes
routes = app.get_all_routes()

for route in routes:
    print(f"Path: {route.raw_path}")
    print(f"Methods: {route.methods}")
    print(f"Name: {route.name}")
    print(f"Tags: {route.tags}")
    print("---")
```

## Route Matching

You can test route matching:

```python
# Test if a route matches a path
route = Routes("/users/{user_id:int}", handler=None, methods=["GET"])

# Test matching
match, params, allowed = route.match("/users/123", "GET")
if match:
    print(f"Matched! Params: {params}")  # {'user_id': 123}
    print(f"Method allowed: {allowed}")  # True

# Test non-matching
match, params, allowed = route.match("/users/abc", "GET")
print(f"Matched: {match}")  # None (invalid int)

match, params, allowed = route.match("/users/123", "POST")
print(f"Method allowed: {allowed}")  # False

# If a route does not match the path or method, Nexios will return a 404 or 405 error as appropriate.
```

## Route Debugging

Enable debug mode to see route information:

```python
from nexios import MakeConfig

config = MakeConfig(debug=True)
app = NexiosApp(config=config)

# In debug mode, you'll see detailed route information
# and better error messages for route matching issues

# In debug mode, route matching errors will include detailed information about why a route did not match.
```

## Performance Considerations

## Route Grouping with `Group`

The `Group` class in Nexios provides a powerful way to organize related routes and middleware under a common path prefix. It's particularly useful for:

- Grouping related routes under a common path prefix
- Applying middleware to a set of routes
- Mounting external ASGI applications with a path prefix
- Creating reusable route collections

### Basic Group Usage

```python
from nexios.routing import Group, Routes
from nexios import NexiosApp

app = NexiosApp()

# Create a group of routes
user_group = Group(
    path="/users",
    routes=[
        Routes(path="/", methods=["GET"], handler=list_users),
        Routes(path="/{user_id}", methods=["GET"], handler=get_user),
        Routes(path="/", methods=["POST"], handler=create_user),
    ]
)

app.add_route(user_group)
```

This creates the following endpoints:

- `GET /users/` - List all users
- `GET /users/{user_id}` - Get a specific user
- `POST /users/` - Create a new user

### Groups with Middleware

You can apply middleware to all routes within a group:

```python


async def auth_middleware(request, response,  next):
    if not request.user.is_authenticated:
        return response.json({"error": "Unauthorized"}, status_code=401)
    return await next()
user_group = Group(path="/users")
api_group = Group(
    path="/api",
    middleware=[auth_middleware],
    routes=[
        Routes(path="/dashboard", methods=["GET"], handler=get_dashboard),
        Routes(path="/profile", methods=["GET"], handler=get_profile),
    ]
)
```

### Mounting External ASGI Applications

Groups can be used to mount external ASGI applications:

```python
from fastapi import FastAPI
from nexios.routing import Group

fastapi_app = FastAPI()

@fastapi_app.get("/items")
async def read_items():
    return [{"item_id": "Foo"}]

# Mount the FastAPI app under /external
group = Group(path="/external", app=fastapi_app)
app.add_route(group)
```

### Nested Groups

Groups can be nested to create hierarchical route structures:

```python
api_v1 = Group(
    path="/v1",
    routes=[
        Routes(path="/status", methods=["GET"], handler=get_status)
    ]
)

auth_group = Group(
    path="/auth",
    middleware=[(auth_middleware, {}, {})],
    routes=[
        Routes(path="/login", methods=["POST"], handler=login),
        Routes(path="/register", methods=["POST"], handler=register),
    ]
)

# Nest the auth group under the API v1 group
api_v1.routes.append(auth_group)
app.add_route(api_v1)
```

This creates the following endpoints:

- `GET /v1/status`
- `POST /v1/auth/login`
- `POST /v1/auth/register`

### Group vs Router

While both `Group` and `Router` can be used to organize routes, they serve different purposes:

| Feature         | Group | Router |
| --------------- | ----- | ------ |
| Path prefixing  | ✅    | ✅     |
| Middleware      | ✅    | ❌     |
| Mount ASGI apps | ✅    | ❌     |
| Nested routing  | ✅    | ✅     |
| Route methods   | ❌    | ✅     |
| Standalone app  | ❌    | ✅     |

### Best Practices

1. **Use Groups for**:

   - Applying common middleware to a set of routes
   - Mounting external ASGI applications
   - Creating reusable route collections

2. **Use Routers for**:

   - Organizing related routes with a common prefix
   - Creating modular, self-contained route collections
   - Versioning APIs

3. **Naming**:

   - Use descriptive names that reflect the group's purpose
   - Prefix group names with their domain (e.g., `user_auth_group`, `admin_api_group`)

4. **Middleware**:
   - Apply middleware at the most specific level possible
   - Document any middleware applied to a group

### Complete Example

```python
from nexios import NexiosApp
from nexios.routing import Group, Routes
from nexios.middleware import Middleware

app = NexiosApp()

# Middleware
auth_middleware = Middleware(AuthenticationMiddleware, required=True)
logging_middleware = Middleware(LoggingMiddleware)

# API v1 Group
api_v1 = Group(
    path="/api/v1",
    middleware=[(logging_middleware, {}, {})],
    routes=[]
)

# Users Group
users_group = Group(
    path="/users",
    middleware=[(auth_middleware, {}, {})],
    routes=[
        Routes(path="/", methods=["GET"], handler=list_users),
        Routes(path="/{user_id}", methods=["GET"], handler=get_user),
        Routes(path="/", methods=["POST"], handler=create_user),
    ]
)

# Mount users group under API v1
api_v1.routes.append(users_group)

# Mount API v1 to the main app
app.add_route(api_v1)
```

This creates the following endpoints with their respective middleware:

- `GET /api/v1/users/` - Logging + Auth
- `GET /api/v1/users/{user_id}` - Logging + Auth
- `POST /api/v1/users/` - Logging + Auth

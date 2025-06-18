# Nexios Routing API Reference 

## Core Routing Components 

### `Routes` Class
```python
class Routes(
    path: str,
    handler: Optional[HandlerType] = None,
    methods: Optional[List[str]] = None,
    name: Optional[str] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    responses: Optional[Dict[int, Any]] = None,
    request_model: Optional[Type[BaseModel]] = None,
    middleware: List[Any] = [],
    tags: Optional[List[str]] = None,
    security: Optional[List[Dict[str, List[str]]]] = None,
    operation_id: Optional[str] = None,
    deprecated: bool = False,
    parameters: List[Parameter] = [],
    exclude_from_schema: bool = False,
    **kwargs: Dict[str, Any]
)
```

### `WebsocketRoutes` Class
```python
class WebsocketRoutes(
    path: str,
    handler: WsHandlerType,
    middleware: List[WsMiddlewareType] = []
)
```

## HTTP Router 

### `Router` Class
```python
class Router(
    prefix: Optional[str] = None,
    routes: Optional[List[Routes]] = None,
    tags: Optional[List[str]] = None,
    exclude_from_schema: bool = False
)
```

#### Key Methods:
- `add_route(route: Routes) -> None` 
- `add_middleware(middleware: MiddlewareType) -> None` 
- `mount_router(app: Router, path: Optional[str] = None) -> None` 
- `url_for(_name: str, **path_params: Any) -> URLPath` 
- `get_all_routes() -> List[Routes]` 

### HTTP Method Decorators
```python
@router.get(path: str, ...) 
@router.post(path: str, ...)
@router.put(path: str, ...)  
@router.patch(path: str, ...)
@router.delete(path: str, ...)
@router.options(path: str, ...)
@router.head(path: str, ...)
@router.route(path: str, methods: List[str], ...)
```

## WebSocket Router 

### `WSRouter` Class
```python
class WSRouter(
    prefix: Optional[str] = None,
    middleware: Optional[List[Any]] = [],
    routes: Optional[List[WebsocketRoutes]] = []
)
```

#### Key Methods:
- `add_ws_route(route: WebsocketRoutes) -> None` 
- `add_ws_middleware(middleware: ASGIApp) -> None` 
- `mount_router(app: WSRouter, path: Optional[str] = None) -> None` 
- `ws_route(path: str, handler: Optional[WsHandlerType] = None) -> Any` 

## Base Components 

### `BaseRouter` (Abstract)
```python
class BaseRouter(ABC):
    def __init__(self, prefix: Optional[str] = None)
```

### `RouteBuilder`
```python
class RouteBuilder:
    @staticmethod
    def create_pattern(path: str) -> RoutePattern
```

### Helper Functions
```python
async def request_response(func: Callable) -> ASGIApp
def websocket_session(func: Callable) -> ASGIApp
def replace_params(path: str, param_convertors: dict, path_params: dict) -> tuple
def compile_path(path: str) -> tuple
```

## Type Definitions 

```python
RouteType = Enum('REGEX', 'PATH', 'WILDCARD')
RoutePattern = dataclass(pattern, raw_path, param_names, route_type, convertor)
URLPath = dataclass(path, protocol)
RouteParam = dataclass
```

## Middleware Handling 

### Common Methods:
- `build_middleware_stack(app: ASGIApp) -> ASGIApp`
- `wrap_middleware(mdw: MiddlewareType) -> Middleware`

## Error Handling 

- Raises `NotFoundException` for 404 responses
- Raises `ValueError` for duplicate parameters
- Automatic 405 Method Not Allowed responses

## Path Parameter Handling 

Supports:
- `/users/{id}` - Basic string params
- `/files/{path:path}` - Path wildcards  
- `/items/{id:int}` - Typed parameters
- Complex regex patterns

# Router API Reference

The Router is a central component in Nexios for defining, organizing, and managing HTTP routes. It provides a rich set of methods and decorators for building RESTful APIs, grouping routes, applying middleware, and more.

## Creating a Router

```python
from nexios import Router

router = Router(prefix="/api/v1")  # Optional prefix for all routes
```

The `Router` class can be instantiated with an optional `prefix` argument, which is prepended to all route paths registered on this router.

## Adding Routes

### HTTP Method Decorators

You can define routes using HTTP method decorators. Each decorator registers a handler for a specific HTTP method and path.

#### `@router.get(path, ...)`
Registers a handler for HTTP GET requests.

```python
@router.get("/users")
async def list_users(request, response):
    users = await get_users()
    return response.json({"users": users})
```

#### `@router.post(path, ...)`
Registers a handler for HTTP POST requests.

```python
@router.post("/users")
async def create_user(request, response):
    data = await request.json()
    user = await create_user_in_db(data)
    return response.status(201).json({"user": user})
```

#### `@router.put(path, ...)`, `@router.patch(path, ...)`, `@router.delete(path, ...)`, etc.
Similarly, you can use `@router.put`, `@router.patch`, `@router.delete`, `@router.options`, and `@router.head` for other HTTP methods.

#### `@router.route(path, methods=[...], ...)`
Registers a handler for one or more HTTP methods.

```python
@router.route("/users", methods=["GET", "POST"])
async def users(request, response):
    if request.method == "GET":
        return response.json({"users": await get_users()})
    elif request.method == "POST":
        data = await request.json()
        user = await create_user_in_db(data)
        return response.status(201).json({"user": user})
```

### Path Parameters

You can define dynamic segments in your route paths using curly braces. Type converters are supported:

- `{id}`: string (default)
- `{id:int}`: integer
- `{slug:slug}`: slug
- `{path:path}`: path wildcard

Example:
```python
@router.get("/users/{id:int}")
async def get_user(request, response):
    user_id = request.path_params["id"]  # Already converted to int
    user = await get_user_by_id(user_id)
    if not user:
        return response.status(404).json({"error": "User not found"})
    return response.json({"user": user})
```

### Route Metadata

You can add metadata to routes for documentation and OpenAPI generation:

- `name`: Unique route name
- `summary`: Short summary for docs
- `description`: Detailed description
- `responses`: Response schemas by status code
- `tags`: List of tags for grouping
- `security`: Security requirements
- `deprecated`: Mark route as deprecated

Example:
```python
@router.get(
    "/users/{id}",
    name="get_user",
    summary="Get user by ID",
    description="Retrieves a user by their unique identifier.",
    responses={200: {"description": "User found"}, 404: {"description": "Not found"}},
    tags=["Users"],
    deprecated=False
)
async def get_user(request, response):
    ...
```

## Middleware

### Global Middleware

You can apply middleware to all routes in a router:

```python
@router.middleware
async def auth_middleware(request, response, next):
    if not request.headers.get("Authorization"):
        return response.status(401).json({"error": "Unauthorized"})
    return await next(request, response)
```

### Route-Specific Middleware

You can apply middleware to individual routes:

```python
@router.get("/admin", middleware=[admin_middleware])
async def admin_panel(request, response):
    ...
```

## Route Groups and Mounting

You can organize routes into groups using routers and mount them into the main application or other routers.

```python
api = Router(prefix="/api")

@api.get("/users")
async def list_users(request, response):
    ...

app.mount_router(api)
```

You can also mount routers at sub-paths:

```python
admin = Router(prefix="/admin")
app.mount_router(admin, path="/admin")
```

## Route Utilities

### `url_for(name, **params)`
Generates a URL for a named route, substituting path parameters.

```python
url = router.url_for("get_user", id=42)
```

### `get_all_routes()`
Returns a list of all registered routes.

```python
routes = router.get_all_routes()
for route in routes:
    print(route.path, route.methods)
```

### `add_route(route, ...)`
Manually add a `Routes` object to the router.

```python
from nexios.routing import Routes

route = Routes("/custom", handler=custom_handler, methods=["GET"])
router.add_route(route)
```

### `add_middleware(middleware)`
Add a middleware function to the router.

```python
router.add_middleware(logging_middleware)
```

### `mount_router(router, path=None)`
Mount another router and all its routes at a given path.

```python
api_v2 = Router(prefix="/v2")
router.mount_router(api_v2)
```

## Error Handling

You can define custom exception handlers for routes or routers:

```python
@router.exception_handler(404)
async def not_found(request, response, exc):
    return response.status(404).json({"error": "Not found"})
```

## Dependencies

You can use dependency injection for route handlers:

```python
from nexios.dependencies import Depends

async def get_current_user(request):
    ...

@router.get("/profile")
async def profile(request, response, user=Depends(get_current_user)):
    return response.json({"user": user})
```
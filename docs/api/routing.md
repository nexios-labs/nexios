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
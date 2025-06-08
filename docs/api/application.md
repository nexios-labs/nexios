# Nexios API Reference 

## Core Application 

### `NexiosApp` Class

The main application class that handles HTTP, WebSocket, and ASGI lifecycle events.

#### Initialization
```python
app = NexiosApp(
    config: Optional[MakeConfig] = DEFAULT_CONFIG,
    title: Optional[str] = None,
    version: Optional[str] = None,
    description: Optional[str] = None,
    middleware: List[Middleware] = [],
    server_error_handler: Optional[ServerErrHandlerType] = None,
    lifespan: Optional[lifespan_manager] = None,
    routes: Optional[List[Routes]] = None
)
```

## HTTP Routing 

### Route Decorators

#### `@app.get()`
```python
@app.get(
    path: str,
    handler: Optional[HandlerType] = None,
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

#### `@app.post()`
```python
@app.post(
    # Same parameters as get()
)
```

#### `@app.put()`
```python
@app.put(
    # Same parameters as get()
)
```

#### `@app.patch()`
```python
@app.patch(
    # Same parameters as get()
)
```

#### `@app.delete()`
```python
@app.delete(
    # Same parameters as get()
)
```

#### `@app.options()`
```python
@app.options(
    # Same parameters as get()
)
```

#### `@app.head()`
```python
@app.head(
    # Same parameters as get()
)
```

## WebSocket Routing 

### `@app.ws_route()`
```python
@app.ws_route(
    path: str,
    handler: Optional[WsHandlerType] = None
)
```

## Middleware 

### `app.add_middleware()`
```python
app.add_middleware(
    middleware: MiddlewareType
)
```

### `app.add_ws_middleware()`
```python
app.add_ws_middleware(
    middleware: ASGIApp
)
```

### `app.wrap_asgi()`
```python
app.wrap_asgi(
    middleware_cls: Callable[[ASGIApp], Any],
    **kwargs: Dict[str, Any]
)
```

## Lifecycle Events 

### `app.on_startup()`
```python
app.on_startup(
    handler: Callable[[], Awaitable[None]]
)
```

### `app.on_shutdown()`
```python
app.on_shutdown(
    handler: Callable[[], Awaitable[None]]
)
```

## Error Handling 

### `app.add_exception_handler()`
```python
app.add_exception_handler(
    exc_class_or_status_code: Union[Type[Exception], int],
    handler: Optional[ExceptionHandlerType] = None
)
```

## Routing Utility Methods 

### `app.url_for()`
```python
app.url_for(
    _name: str,
    **path_params: Dict[str, Any]
) -> URLPath
```

### `app.get_all_routes()`
```python
app.get_all_routes() -> List[Routes]
```

### `app.mount_router()`
```python
app.mount_router(
    router: Router,
    path: Optional[str] = None
)
```

### `app.mount_ws_router()`
```python
app.mount_ws_router(
    router: WSRouter
)
```

### `app.add_route()`
```python
app.add_route(
    route: Routes
)
```

### `app.add_ws_route()`
```python
app.add_ws_route(
    route: WebsocketRoutes
)
```

### `app.register()`

```python
app.register(
    ASGIAPPLICATION,
    "/mount-path"
)
```

## ASGI Implementation 

### `app.__call__()`
```python
async def __call__(
    scope: Scope,
    receive: Receive,
    send: Send
) -> None
```
# Day 5: Middleware in Nexios

## Understanding Middleware

Middleware in Nexios is a powerful feature that allows you to process requests and responses at different stages of the request lifecycle. There are two main ways to create middleware:

1. Function-based middleware
2. Class-based middleware (inheriting from `BaseMiddleware`)

## Function-based Middleware

The simplest way to create middleware is using functions:

```python
from nexios import NexiosApp
from nexios.http import Request, Response
from nexios.types import Middleware
import time

app = NexiosApp()

# Timing middleware
async def timing_middleware(
    request: Request,
    response: Response,
    call_next: Middleware
) -> Response:
    start_time = time.time()
    response = await call_next()
    process_time = time.time() - start_time
    
    response.header("X-Process-Time",str(process_time))
    return response

# Add middleware to app
app.add_middleware(timing_middleware)
```

## Class-based Middleware

For more complex middleware, Nexios provides a `BaseMiddleware` class that you can inherit from:

```python
from nexios import NexiosApp
from nexios.middleware import BaseMiddleware
from nexios.http import Request, Response
import time

class TimingMiddleware(BaseMiddleware):
    async def process_request(
        self,
        request: Request,
        response: Response,
        call_next: Callable[..., Awaitable[Response]]
    ) -> Response:
        # Process request before it reaches the route handler
        request.state.start_time = time.time()
        return await call_next()

    async def process_response(
        self,
        request: Request,
        response: Response
    ) -> Response:
        # Process response before it's sent to the client
        process_time = time.time() - request.state.start_time
        response.header("X-Process-Time" ,str(process_time))
        return response

# Use the middleware
app.add_middleware(TimingMiddleware())
```

## Built-in Middleware

Nexios comes with several built-in middleware classes:

1. `CORSMiddleware`: Handles Cross-Origin Resource Sharing
2. `CSRFMiddleware`: Protects against Cross-Site Request Forgery
3. `SecurityMiddleware`: Adds security headers
4. `SessionMiddleware`: Manages user sessions
5. `TemplateContextMiddleware`: Injects template context

Example of using built-in middleware:

```python
from nexios import NexiosApp
from nexios.middleware import CORSMiddleware, SecurityMiddleware

app = NexiosApp()

# Add CORS middleware
app.add_middleware(CORSMiddleware())

# Add security middleware with custom configuration
app.add_middleware(SecurityMiddleware(
    csp_enabled=True,
    hsts_enabled=True,
    xss_protection=True
))
```

## Global vs Route-specific Middleware

You can apply middleware globally or to specific routes:

```python
from nexios import NexiosApp, Router
from nexios.middleware import BaseMiddleware
from nexios.http import Request, Response

class AdminMiddleware(BaseMiddleware):
    async def process_request(
        self,
        request: Request,
        response: Response,
        call_next: Callable[..., Awaitable[Response]]
    ) -> Response:
        if not request.user.is_admin:
            return Response(
                content={"error": "Admin access required"},
                status_code=403
            )
        return await call_next()

# Admin router with middleware
admin_router = Router(prefix="/admin")
admin_router.add_middleware(AdminMiddleware())

@admin_router.get("/stats")
async def admin_stats():
    return {"stats": "admin only data"}

# Include router in main app
app.mount_router(admin_router)
```

## Advanced Middleware Features

### Route-specific Middleware

You can use the `use_for_route` decorator to apply middleware to specific routes:

```python
from nexios.middleware.utils import use_for_route

@use_for_route("/api/*")
class APIMiddleware(BaseMiddleware):
    async def process_request(
        self,
        request: Request,
        response: Response,
        call_next: Callable[..., Awaitable[Response]]
    ) -> Response:
        # Only runs for routes starting with /api/
        return await call_next()
```

### ASGI Middleware

For low-level ASGI middleware:

```python
from nexios import NexiosApp

app = NexiosApp()

# Wrap the entire application with ASGI middleware
app.wrap_asgi(YourASGIMiddleware, **kwargs)
```

## Best Practices

1. **Order Matters**: Middleware is executed in the order it's added. Add middleware in the correct order:
   ```python
   # Security middleware first
   app.add_middleware(SecurityMiddleware())
   # Then authentication
   app.add_middleware(AuthMiddleware())
   # Then application-specific middleware
   app.add_middleware(YourMiddleware())
   ```

2. **Error Handling**: Always handle exceptions in middleware:
   ```python
   class ErrorHandlingMiddleware(BaseMiddleware):
       async def process_request(
           self,
           request: Request,
           response: Response,
           call_next: Callable[..., Awaitable[Response]]
       ) -> Response:
           try:
               return await call_next()
           except Exception as e:
               return Response(
                   content={"error": str(e)},
                   status_code=500
               )
   ```

3. **Performance**: Keep middleware lightweight and efficient:
   ```python
   class CachingMiddleware(BaseMiddleware):
       def __init__(self, cache_duration: int = 300):
           self.cache = {}
           self.cache_duration = cache_duration
   ```

## Practice Exercise

Create these middleware components:

1. Request/Response Logger using `BaseMiddleware`
2. Cache Middleware with Redis support
3. Error Handler with custom error pages
4. Authentication Middleware with JWT
5. Response Transformer for API versioning

## Additional Resources
- [Middleware Guide](../../guide/middleware.md)
- [Error Handling](../../guide/error-handling.md)
- [Security Best Practices](../../guide/security.md)

## 🎯 Next Steps
Tomorrow in [Day 6: Environment Configuration](../day06/index.md), we'll explore:
- Using `.env` files
- CORS configuration
- JSON limits
- Development vs production settings
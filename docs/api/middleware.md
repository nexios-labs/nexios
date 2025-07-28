# Middleware API Reference

The Middleware API in Nexios provides a powerful way to intercept and modify requests and responses as they flow through your application. Middleware can be used for cross-cutting concerns like authentication, logging, error handling, and more.

## Base Middleware

The `BaseMiddleware` class is the foundation for creating custom middleware in Nexios.

```python
from nexios.middleware import BaseMiddleware
from nexios.http import Request, Response

class CustomMiddleware(BaseMiddleware):
    async def __call__(self, request: Request, response: Response, next):
        # Process request
        result = await next(request, response)
        # Process response
        return result
```

### Methods

#### `__call__(request: Request, response: Response, next) -> Any`

The main middleware method that processes requests and responses.

**Parameters:**

- `request` (Request): The incoming HTTP request
- `response` (Response): The HTTP response object
- `next`: The next middleware or route handler in the chain

**Returns:**

- Any: The processed response

**Example:**

```python
class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, request: Request, response: Response, next):
        start_time = time.time()

        # Process request
        print(f"Request started: {request.method} {request.url}")

        # Call next middleware/handler
        result = await next(request, response)

        # Process response
        duration = time.time() - start_time
        print(f"Request completed: {request.method} {request.url} in {duration:.2f}s")

        return result
```

## Built-in Middleware

### CORS Middleware

Handles Cross-Origin Resource Sharing (CORS) headers.

```python
from nexios.middleware import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=True,
    max_age=3600
)
```

**Parameters:**

- `allow_origins` (List[str]): List of allowed origins
- `allow_methods` (List[str]): List of allowed HTTP methods
- `allow_headers` (List[str]): List of allowed headers
- `allow_credentials` (bool): Whether to allow credentials
- `max_age` (int): Maximum age of preflight requests

### Rate Limiting Middleware

Protects your application from abuse by limiting request rates.

```python
from nexios.middleware import RateLimitMiddleware

app.add_middleware(
    RateLimitMiddleware,
    rate_limit=100,  # requests
    time_window=60,  # seconds
    key_func=lambda request: request.client.host
)
```

**Parameters:**

- `rate_limit` (int): Maximum number of requests allowed
- `time_window` (int): Time window in seconds
- `key_func` (Callable): Function to generate rate limit key

### Session Middleware

Manages user sessions.

```python
from nexios.middleware import SessionMiddleware

app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key",
    session_cookie="session",
    max_age=3600,
    secure=True,
    httponly=True
)
```

**Parameters:**

- `secret_key` (str): Secret key for session encryption
- `session_cookie` (str): Name of the session cookie
- `max_age` (int): Session lifetime in seconds
- `secure` (bool): Whether to use secure cookies
- `httponly` (bool): Whether to use HTTP-only cookies

## Creating Custom Middleware

### Authentication Middleware

```python
class AuthMiddleware(BaseMiddleware):
    async def __call__(self, request: Request, response: Response, next):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return response.status(401).json({"error": "Unauthorized"})

        try:
            user = await authenticate_user(auth_header)
            request.state.user = user
            return await next(request, response)
        except AuthenticationError:
            return response.status(401).json({"error": "Invalid credentials"})
```

### Error Handling Middleware

```python
class ErrorHandlingMiddleware(BaseMiddleware):
    async def __call__(self, request: Request, response: Response, next):
        try:
            return await next(request, response)
        except Exception as e:
            logger.error(f"Unhandled error: {str(e)}")
            return response.status(500).json({
                "error": "Internal Server Error",
                "detail": str(e) if settings.DEBUG else None
            })
```

### Request Logging Middleware

```python
class RequestLoggingMiddleware(BaseMiddleware):
    async def __call__(self, request: Request, response: Response, next):
        start_time = time.time()

        # Log request
        logger.info(
            f"Request started: {request.method} {request.url} "
            f"from {request.client.host}"
        )

        # Process request
        result = await next(request, response)

        # Log response
        duration = time.time() - start_time
        logger.info(
            f"Request completed: {request.method} {request.url} "
            f"in {duration:.2f}s with status {response.status_code}"
        )

        return result
```

## Middleware Order

The order of middleware is important. Here's a recommended order:

1. Error handling middleware
2. CORS middleware
3. Authentication middleware
4. Rate limiting middleware
5. Session middleware
6. Request logging middleware

```python
app = NexiosApp()

# Add middleware in the correct order
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=["*"])
app.add_middleware(AuthMiddleware)
app.add_middleware(RateLimitMiddleware, rate_limit=100, time_window=60)
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
app.add_middleware(RequestLoggingMiddleware)
```

## Best Practices

1. **Keep Middleware Focused**: Each middleware should do one thing well.

2. **Handle Errors Gracefully**: Always catch and handle exceptions in middleware.

3. **Use Type Hints**: Add type hints to middleware methods for better code clarity.

4. **Document Dependencies**: Clearly document any dependencies or requirements.

5. **Test Middleware**: Write unit tests for your middleware.

```python
async def test_auth_middleware():
    middleware = AuthMiddleware()
    request = Request(...)
    response = Response(...)

    # Test successful authentication
    result = await middleware(request, response, next_handler)
    assert result.status_code == 200

    # Test failed authentication
    request.headers = {}
    result = await middleware(request, response, next_handler)
    assert result.status_code == 401
```

6. **Monitor Performance**: Add timing and logging to track middleware performance.

```python
class PerformanceMonitoringMiddleware(BaseMiddleware):
    async def __call__(self, request: Request, response: Response, next):
        start_time = time.time()
        result = await next(request, response)
        duration = time.time() - start_time

        if duration > 1.0:  # Log slow requests
            logger.warning(
                f"Slow request: {request.method} {request.url} "
                f"took {duration:.2f}s"
            )

        return result
```

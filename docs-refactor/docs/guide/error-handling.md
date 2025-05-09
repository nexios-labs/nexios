

# Error Handling

Nexios provides a robust and flexible error handling system that allows you to manage exceptions gracefully and return appropriate responses to clients. This documentation covers all aspects of error handling in Nexios applications.


## HTTP Exceptions

Nexios includes built-in HTTP exceptions for common error scenarios:

```python
from nexios.exceptions import HTTPException, NotFoundException

@app.get("/users/{user_id}")
async def get_user(request, response):
    user = await find_user(request.path_params['user_id'])
    if not user:
        raise NotFoundException(detail="User not found")
```

### Built-in HTTP Exceptions

| Exception Class          | Status Code | Description                          |
|--------------------------|-------------|--------------------------------------|
| `HTTPException`          | Any         | Base class for all HTTP exceptions   |
| `BadRequestException`    | 400         | Invalid client request               |
| `UnauthorizedException`  | 401         | Authentication required              |
| `ForbiddenException`     | 403         | Authenticated but not authorized     |
| `NotFoundException`      | 404         | Resource not found                   |
| `MethodNotAllowed`       | 405         | HTTP method not allowed              |
| `ConflictException`      | 409         | Resource conflict                    |
| `InternalServerError`    | 500         | Generic server error                 |
| `NotImplementedError`    | 501         | Feature not implemented              |
| `ServiceUnavailable`     | 503         | Service temporarily unavailable      |

### Raising HTTP Exceptions

All HTTP exceptions accept these parameters:
- `status_code`: HTTP status code (required for base `HTTPException`)
- `detail`: Error message or details
- `headers`: Custom headers to include in the response

```python
raise HTTPException(
    status_code=400,
    detail="Invalid request parameters",
    headers={"X-Error-Code": "INVALID_PARAMS"}
)
```

## Custom Exception Classes

Create custom exceptions by subclassing `HTTPException`:

```python
from nexios.exceptions import HTTPException

class PaymentRequiredException(HTTPException):
    def __init__(self, detail: str = None):
        super().__init__(
            status_code=402,
            detail=detail or "Payment required",
            headers={"X-Payment-Required": "true"}
        )

@app.get("/premium-content")
async def get_premium_content(request, response):
    if not request.user.has_premium:
        raise PaymentRequiredException("Upgrade to premium to access this content")
```

## Exception Handlers

Register custom handlers for specific exception types:

### Basic Exception Handler

```python
from pydantic import ValidationError

async def validation_error_handler(request, response, exc):
    return response.json(
        {
            "error": "Validation Failed",
            "details": exc.errors(),
            "status": 422
        },
        status_code=422
    )

app.add_exception_handler(ValidationError, validation_error_handler)
```

### Class-Based Exception Handler

For more complex scenarios, use class-based handlers:

```python
class DatabaseErrorHandler:
    async def __call__(self, request, response, exc):
        logger.error(f"Database error: {str(exc)}")
        return response.json(
            {
                "error": "Database Error",
                "message": "Please try again later",
                "reference": str(uuid.uuid4())
            },
            status_code=503
        )

app.add_exception_handler(DatabaseError, DatabaseErrorHandler())
```

## Status Code Handlers

Handle exceptions by status code rather than exception type:

```python
async def handle_404(request, response, exc):
    return response.html(
        f"<h1>Not Found</h1><p>{exc.detail or 'Resource not found'}</p>",
        status_code=404
    )

app.add_exception_handler(404, handle_404)
```

## Debug Mode

Enable debug mode for detailed error responses during development:

```python
from nexios import MakeConfig

config = MakeConfig({"debug": True})
app = NexiosApp(config=config)
```

Debug features include:
- Full stack traces in responses
- Request details
- Interactive error pages
- Source code context

## Best Practices

### 1. Structured Error Responses

Maintain consistent error response formats:

```python
async def api_error_handler(request, response, exc):
    return response.json(
        {
            "error": {
                "code": exc.__class__.__name__,
                "message": str(exc.detail) if hasattr(exc, 'detail') else str(exc),
                "timestamp": datetime.now().isoformat(),
                "path": request.url.path
            }
        },
        status_code=getattr(exc, 'status_code', 500)
    )

app.add_exception_handler(Exception, api_error_handler)
```

### 2. Logging

Always log exceptions before handling them:

```python
async def logged_error_handler(request, response, exc):
    logger.error(
        "Error processing request",
        exc_info=exc,
        extra={
            "path": request.path,
            "method": request.method,
            "user": getattr(request, 'user', None)
        }
    )
    return response.json(...)
```

### 3. Security Considerations

- Never expose sensitive information in error responses
- Use custom error messages in production
- Implement rate limiting for error responses

### 4. Common Handler Patterns

**Validation Error Handler:**

```python
from pydantic import ValidationError

async def handle_validation_error(request, response, exc):
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"]
        })
    
    return response.json(
        {"validation_errors": errors},
        status_code=422
    )
```

**Database Error Handler:**

```python
async def handle_db_error(request, response, exc):
    if isinstance(exc, ConnectionError):
        return response.json(
            {"error": "Database unavailable"},
            status_code=503
        )
    return response.json(
        {"error": "Database operation failed"},
        status_code=500
    )
```

**Authentication Error Handler:**

```python
async def handle_auth_error(request, response, exc):
    return response.json(
        {
            "error": "Authentication failed",
            "www-authenticate": "Bearer"
        },
        status_code=401,
        headers={"WWW-Authenticate": "Bearer"}
    )
```

## Advanced Topics

### Exception Handler Chaining

Handlers can be chained by re-raising exceptions:

```python
async def log_and_reraise(request, response, exc):
    logger.error(f"Error occurred: {exc}")
    raise exc

app.add_exception_handler(Exception, log_and_reraise)
```

### Route-Specific Handlers

Handle exceptions within individual routes:

```python
@app.get("/risky-operation")
async def risky_operation(request, response):
    try:
        result = await perform_risky_operation()
        return response.json(result)
    except SpecificError as e:
        return response.json(
            {"error": "Operation failed", "details": str(e)},
            status_code=400
        )
```

### WebSocket Exception Handling

```python
@app.ws_route("/chat")
async def chat_handler(websocket):
    try:
        while True:
            data = await websocket.receive_json()
            # process message
    except ConnectionError:
        logger.info("Client disconnected")
    except ValueError as e:
        await websocket.send_json({"error": "Invalid message format"})
```

## Troubleshooting

**Common Issues:**

1. **Handler not being called:**
   - Verify the exception is raised (not caught elsewhere)
   - Check handler registration order
   - Confirm exception type matches exactly

2. **Debug mode not showing details:**
   - Ensure `debug=True` is set in config
   - Check no middleware is modifying responses
   - Verify no higher-priority handler is catching the exception

3. **Headers not being set:**
   - Ensure headers are set before returning the response
   - Check for conflicting header modifications
```

This documentation provides:
1. Comprehensive coverage of all error handling features
2. Clear examples for each concept
3. Best practices and patterns
4. Troubleshooting guidance
5. Consistent structure with existing docs

The content is organized to flow from basic to advanced topics, with clear section headers and practical examples throughout.
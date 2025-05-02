---
icon: triangle-exclamation
---

# Error Handling

## Error Handling and Exceptions

Robust error handling is critical for building reliable applications. Nexios provides a comprehensive exception system that helps you manage errors gracefully, provide clear feedback to users, and debug issues in development.

### Basic Concepts

Nexios's error handling system is built around these core components:

1. **HTTP Exceptions**: Standard exceptions representing HTTP error responses
2. **Exception Middleware**: Processes exceptions and converts them to appropriate responses
3. **Exception Handlers**: Custom functions that determine how specific exceptions are handled
4. **Debug Mode**: Enhanced error information during development

### HTTP Exceptions

The most common way to handle errors in Nexios is through HTTP exceptions:

```python
from nexios import get_application
from nexios.exceptions import HTTPException, NotFoundException

app = get_application()

@app.get("/users/{user_id}")
async def get_user(req, res):
    user_id = req.path_params.user_id
    user = await find_user(user_id)
    
    if not user:
        # Raise a 404 error
        raise NotFoundException(detail=f"User {user_id} not found")
    
    return res.json(user)

@app.get("/items/{item_id}")
async def get_item(req, res):
    item_id = req.path_params.item_id
    
    if not is_valid_id(item_id):
        # Custom 400 error
        raise HTTPException(
            status_code=400, 
            detail="Invalid item ID format",
            headers={"X-Error-Code": "INVALID_ID"}
        )
    
    # Continue processing...
```

#### Built-in HTTP Exceptions

Nexios provides several built-in exceptions for common HTTP error scenarios:

| Exception            | Status Code | Description                    |
| -------------------- | ----------- | ------------------------------ |
| `HTTPException`      | Any         | Base exception for HTTP errors |
| `NotFoundException`  | 404         | Resource not found             |
| `WebSocketException` | N/A         | WebSocket-specific errors      |

You can create your own exception classes by subclassing `HTTPException`:

```python
from nexios.exceptions import HTTPException

class ForbiddenException(HTTPException):
    def __init__(self, detail=None, headers=None):
        super().__init__(
            status_code=403,
            detail=detail or "You don't have permission to access this resource",
            headers=headers or {}
        )

# Later in your code
@app.get("/admin")
async def admin_panel(req, res):
    if not req.user.is_admin:
        raise ForbiddenException()
    # ...
```

### Exception Middleware

The `ExceptionMiddleware` is responsible for catching exceptions and converting them to appropriate HTTP responses:

```python
from nexios import get_application
from nexios.exception_handler import ExceptionMiddleware

app = get_application()

# The exception middleware is added automatically when creating the application,
# but you can add it explicitly if needed:
# app.add_middleware(ExceptionMiddleware())
```

#### Exception Handlers

You can add custom exception handlers to control how specific exceptions are handled:

```python
from nexios import get_application
from nexios.exceptions import HTTPException
from pydantic import ValidationError

app = get_application()

# Handler for validation errors
async def validation_error_handler(req, res, exc):
    return res.json(
        {
            "error": "Validation Error",
            "detail": exc.errors()
        },
        status_code=422
    )

# Handler for database connection errors
async def db_error_handler(req, res, exc):
    # Log the error
    logger.error(f"Database error: {exc}")
    
    # Return a user-friendly response
    return res.json(
        {
            "error": "Database Error",
            "message": "An error occurred while connecting to the database"
        },
        status_code=500
    )

# Register exception handlers
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(ConnectionError, db_error_handler)
```

#### Handling Status Codes

You can also register handlers for specific HTTP status codes:

```python
# Generic handler for all 404 errors
@app.add_exception_handler(404)
async def not_found_handler(req, res, exc):
    return res.html(
        f"<h1>Page Not Found</h1><p>The page {req.url} does not exist.</p>",
        status_code=404
    )

# Handler for 500 errors
@app.add_exception_handler(500)
async def server_error_handler(req, res, exc):
    # Log the error
    logger.error(f"Server error: {exc}")
    
    # Return a user-friendly error page
    return res.html(
        "<h1>Server Error</h1><p>Sorry, something went wrong on our end.</p>",
        status_code=500
    )
```

### Debug Mode

Nexios's error handling becomes more detailed in debug mode, providing rich error information to help developers identify and fix issues:

```python
from nexios import get_application, MakeConfig

# Enable debug mode
config = MakeConfig({
    "debug": True
})

app = get_application(config=config)
```

In debug mode:

1. **Detailed Error Pages**: HTML error pages with traceback information
2. **Preserved Exception Information**: Original exceptions

***

### icon: triangle-exclamation

## Exceptions

In Nexios, exception handling is designed to work asynchronously. When an error occurs during request processing, Nexios allows developers to catch and handle it using exception handlers.

An exception handler in Nexios is an **async function** that takes three parameters:

* `request`: The incoming HTTP request object.
* `response`: The HTTP response object used to send a formatted response.
* `exception`: The raised exception instance.

Additionally, developers can **create custom exceptions** by inheriting from `HttpException` and register them using `app.add_exception_handler()`.

***

**Default Exception Handling**

Nexios automatically catches unhandled exceptions and returns an appropriate HTTP response. However, for more control, you can define custom exception handlers.

**Example: Default Error Handling**

If a route raises an error and no handler is registered:

```python
@app.route("/error")
async def error_route(request, response):
    raise ValueError("An unexpected error occurred!")
```

**Response (default handling):**\
By default, Nexios returns a 500 Internal Server Error response for unhandled exceptions. However, if debug=True is set in the application configuration, Nexios provides a detailed error page for easier debugging, displaying stack traces and relevant request information.

***

**Custom Exception Handling**

You can define custom exception handlers for specific errors.

**Example: Handling a `ValueError`**

```python
async def handle_value_error(request, response, exception):
    response.json({"error": "Bad Request", "detail": str(exception)}, status_code = 500)

app.add_exception_handler(ValueError, handle_value_error)

@app.route("/custom-error")
async def custom_error(request, response):
    raise ValueError("Invalid input provided")
```

**Response (custom handler for ValueError):**

```json
{
  "error": "Bad Request",
  "detail": "Invalid input provided"
}
```

**Key Points:**

* The handler **captures ValueError** and responds with a `400 Bad Request` status.
* `app.add_exception_handler(ValueError, handle_value_error)` registers the handler globally.

***

**Creating Custom Exceptions**

To define custom exceptions, inherit from `HttpException`. This allows setting custom status codes and messages.

**Example: Creating a `CustomForbiddenException`**

```python
from nexios.exceptions import HttpException

class CustomForbiddenException(HttpException):
    def __init__(self, detail="You do not have permission to access this resource"):
        super().__init__(status_code=403, detail=detail)
```

**Using the custom exception in a route:**

```python
@app.route("/forbidden")
async def forbidden_route(request, response):
    raise CustomForbiddenException()

async def handle_forbidden_exception(request, response, exception):
    response.json({"error": "Forbidden", "detail": exception.detail}, status_Code = exception.status_Code)

app.add_exception_handler(CustomForbiddenException, handle_forbidden_exception)
```

**Now, when `/forbidden` is accessed, the response will be:**

```json
{
  "error": "Forbidden",
  "detail": "You do not have permission to access this resource"
}
```

***

**Handling Multiple Exceptions**\
You can register multiple exception handlers for different error types.

**Example: Handling Multiple Errors**

```python
async def handle_not_found(request, response, exception):
    response.json({"error": "Not Found", "detail": "The requested resource was not found"},status_code = 404)

async def handle_server_error(request, response, exception):
    response.json({"error": "Internal Server Error", "detail": "Something went wrong"},status_code = 500)

app.add_exception_handler(FileNotFoundError, handle_not_found)
app.add_exception_handler(Exception, handle_server_error)
```

📌 **Key Points:**

* `FileNotFoundError` returns a **404 Not Found** response.
* Generic `Exception` catches all **unhandled errors** and returns **500 Internal Server Error**.

***

**Catching Exceptions at the Route Level**

Instead of global handlers, you can handle exceptions inside a route using try-except.

**Example: Try-Except in Route**

```python
@app.route("/divide")
async def divide_numbers(request, response):
    try:
        num1 = int(request.query_params.get("num1", 10))
        num2 = int(request.query_params.get("num2", 0))
        result = num1 / num2
        response.json({"result": result})
    except ZeroDivisionError:
        response.status_code = 400
        response.json({"error": "Cannot divide by zero"})
```

**Accessing `/divide?num1=10&num2=0` returns:**

```json
{
  "error": "Cannot divide by zero"
}
```

**Key Points:**

* This method is **useful for route-specific exception handling**.
* It avoids unnecessary global handlers for simple errors.

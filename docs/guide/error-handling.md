

# Error Handling

Nexios provides a robust and flexible error handling system that allows you to manage exceptions gracefully and return appropriate responses to clients. This documentation covers all aspects of error handling in Nexios applications.


## HTTP Exceptions

Nexios includes built-in HTTP exceptions for common error scenarios:

```python{6}
from nexios.exceptions import HTTPException
@app.get("/users/{user_id}")
async def get_user(request, response):
    user = await find_user(request.path_params['user_id'])
    if not user:
        raise HTTPException(detail="User not found", status = 404)
    return response.json(user)
```


## Raising HTTP Exceptions
All HTTP exceptions accept these parameters:

- status_code: HTTP status code (required for base HTTPException)

- detail: Error message or details

- headers: Custom headers to include in the response

```python
raise HTTPException(
    status_code=400,
    detail="Invalid request parameters",
    headers={"X-Error-Code": "INVALID_PARAMS"}
)
```

## Custom Exception Classes

Nexios provides a way to create custom exception classes that extend the built-in HTTPException class. This allows you to define specific error handling behavior for specific types of errors.

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
    return response.json({"message": "Premium content available"})

```

## Exception Handlers

Nexios provides a way to register custom exception handlers for specific exception types or HTTP status codes. This allows you to define custom error handling behavior for specific errors.

```python
from nexios.exceptions import HTTPException

async def handle_payment_required_exception(request, response, exception):
    return response.json({"error": "Payment required"}, status=402)

app.add_exception_handler(PaymentRequiredException, handle_payment_required_exception)

@app.get("/premium-content")
async def get_premium_content(request, response):
    if not request.user.has_premium:
        raise PaymentRequiredException("Upgrade to premium to access this content")
    return response.json({"message": "Premium content available"})      
``` 

## Status Code Handlers
Handle exceptions by status code:

```python
from nexios.exceptions import HTTPException

async def handle_payment_required_exception(request, response, exception):
    return response.json({"error": "Payment required"}, status=402)

app.add_exception_handler(402, handle_payment_required_exception)

@app.get("/premium-content")
async def get_premium_content(request, response):
    if not request.user.has_premium:
        raise PaymentRequiredException("Upgrade to premium to access this content")
    return response.json({"message": "Premium content available"})      
```


In the provided example, we demonstrate how to create a custom exception handler for handling specific exceptions in a Nexios application. We define a custom exception handler `handle_payment_required_exception`, which returns a JSON response with an error message and a status code when a `PaymentRequiredException` is raised. This handler is registered with the application using `app.add_exception_handler()`. This approach allows for granular control over error responses, improving the user experience by providing clear feedback for specific scenarios, such as when a user tries to access premium content without a subscription.


## Debug Mode
Enable debug mode for detailed error responses:

```python

from nexios import MakeConfig

config = MakeConfig({"debug": True})
app = NexiosApp(config=config)
```

::: tip 🥹Tip

You can modify the app config simply as
app.config.debug = True
:::
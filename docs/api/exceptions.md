# Exception Handling API Reference

##  Core Components

### 1. HTTP Exceptions
```python
from nexios.exceptions import HTTPException

# Built-in exceptions
NotFoundException(status_code=404, detail="Not Found")  # 404 Error
ForbiddenException(status_code=403)  # 403 Error
# etc.

# Custom exception
class PaymentRequiredException(HTTPException):
    def __init__(self, detail="Payment required"):
        super().__init__(status_code=402, detail=detail)
```

### 2. Exception Handlers
```python
# Register handler for exception type
app.add_exception_handler(ValueError, handle_value_error)

# Register handler for status code
app.add_exception_handler(404, handle_not_found)

# Handler function signature
async def handler(req: Request, res: Response, exc: Exception) -> Response:
    return res.json({"error": str(exc)}, status_code=400)
```

## Common Patterns

### Basic Error Handling
```python
@app.get("/items/{id}")
async def get_item(req, res):
    item = await db.get_item(req.path_params.id)
    if not item:
        raise NotFoundException(detail="Item not found")
    return res.json(item)
```

### Custom Error Handler
```python
async def handle_validation_error(req, res, exc):
    return res.json(
        {"error": "Validation failed", "details": exc.errors()},
        status_code=422
    )

app.add_exception_handler(ValidationError, handle_validation_error)
```

### Route-Specific Handling
```python
@app.get("/divide")
async def divide(req, res):
    try:
        a = int(req.query_params.a)
        b = int(req.query_params.b)
        return res.json({"result": a / b})
    except ZeroDivisionError:
        return res.json({"error": "Division by zero"}, status_code=400)
```

## Configuration

### Debug Mode
```python
app = get_application(config={"debug": True})
```
- Shows detailed error pages with tracebacks
- Preserves original exception information

## Built-in Exceptions

| Exception Class       | Status Code | Typical Use Case               |
|-----------------------|-------------|---------------------------------|
| `HTTPException`       | Any         | Base class for HTTP exceptions  |

##  Best Practices

1. **Use specific exceptions** where possible (404 vs generic 400)
2. **Include useful details** in error responses
3. **Register global handlers** for common error types
4. **Use debug mode** in development, disable in production
5. **Log errors** before returning responses
6. **Keep error responses consistent** in format

##  Example Flow

```python
# Custom exception
class InsufficientFundsException(HTTPException):
    def __init__(self, balance: float):
        super().__init__(
            status_code=402,
            detail=f"Insufficient funds (balance: {balance})"
        )

# Handler
async def handle_insufficient_funds(req, res, exc):
    return res.json(
        {"error": "Payment failed", "detail": exc.detail},
        status_code=exc.status_code
    )

# Registration
app.add_exception_handler(InsufficientFundsException, handle_insufficient_funds)

# Usage in route
@app.post("/pay")
async def make_payment(req, res):
    user_balance = get_balance(req.user)
    if user_balance < req.amount:
        raise InsufficientFundsException(balance=user_balance)
    # Process payment...
```
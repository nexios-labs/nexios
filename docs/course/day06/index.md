# Day 6: Error Handling

Welcome to Day 6! Today we'll dive deep into error handling in Nexios, learning how to handle exceptions gracefully and provide meaningful error responses.

## Understanding Error Handling

Error handling is crucial for:
- Providing clear feedback to API consumers
- Maintaining security by not exposing sensitive information
- Logging and debugging issues
- Ensuring consistent error responses
- Graceful degradation of services

## Built-in Exception Types

Nexios provides several built-in exception types:

```python
from nexios.exceptions import (
    HTTPException,
    ValidationError,
    NotFoundException,
    AuthenticationError,
    PermissionError
)

# Basic HTTP exception
raise HTTPException(status_code=400, detail="Bad request")

# Not found exception
raise NotFoundException(detail="Resource not found")

# Authentication error
raise AuthenticationError(detail="Invalid credentials")

# Permission error
raise PermissionError(detail="Insufficient permissions")
```

## Global Exception Handlers

```python
from nexios import NexiosApp
from nexios.exceptions import HTTPException
from nexios.http import Request, Response

app = NexiosApp()

# Handle HTTP exceptions
@app.add_exception_handler(HTTPException)
async def http_exception_handler(request: Request, response: Response, exc: HTTPException):
    return response.json({
        "error": exc.detail,
        "status_code": exc.status_code
    }, status_code=exc.status_code)

# Handle validation errors
@app.add_exception_handler(ValidationError)
async def validation_exception_handler(request: Request, response: Response, exc: ValidationError):
    return response.json({
        "error": "Validation error",
        "details": exc.errors()
    }, status_code=422)

# Handle all other exceptions
@app.add_exception_handler(Exception)
async def generic_exception_handler(request: Request, response: Response, exc: Exception):
    # Log the error here
    return response.json({
        "error": "Internal server error",
        "detail": str(exc) if app.debug else None
    }, status_code=500)
```

## Custom Exception Types

```python
class APIError(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
        metadata: dict = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.metadata = metadata or {}

class BusinessLogicError(APIError):
    def __init__(self, detail: str, error_code: str = None):
        super().__init__(
            status_code=400,
            detail=detail,
            error_code=error_code
        )

class ResourceNotFoundError(APIError):
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            status_code=404,
            detail=f"{resource_type} with id {resource_id} not found",
            error_code="RESOURCE_NOT_FOUND",
            metadata={
                "resource_type": resource_type,
                "resource_id": resource_id
            }
        )

# Register handlers for custom exceptions
@app.add_exception_handler(APIError)
async def api_error_handler(request: Request, response: Response, exc: APIError):
    return response.json({
        "error": exc.detail,
        "error_code": exc.error_code,
        "metadata": exc.metadata,
        "status_code": exc.status_code
    }, status_code=exc.status_code)
```

## Error Handling in Routes

```python
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserNotFoundError(ResourceNotFoundError):
    def __init__(self, user_id: str):
        super().__init__("User", user_id)

@app.post("/users")
async def create_user(request: Request, response: Response):
    try:
        data = await request.json()
        user = UserCreate(**data)
        
        # Check if username exists
        if await check_username_exists(user.username):
            raise BusinessLogicError(
                detail="Username already taken",
                error_code="USERNAME_TAKEN"
            )
        
        # Create user
        created_user = await create_user_in_db(user)
        return response.json(created_user, status_code=201)
    
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=e.errors()
        )

@app.get("/users/{user_id}")
async def get_user(request: Request, response: Response, user_id: str):
    user = await find_user_by_id(user_id)
    if not user:
        raise UserNotFoundError(user_id)
    return response.json(user)
```

## Error Handling in Middleware

```python
from typing import Callable
import logging
import traceback

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    def __init__(self, app_name: str = "app"):
        self.app_name = app_name
    
    async def __call__(
        self,
        request: Request,
        response: Response,
        call_next: Callable
    ):
        try:
            return await call_next()
        
        except HTTPException as exc:
            # Log HTTP exceptions
            logger.warning(
                f"HTTP {exc.status_code} error in {self.app_name}: {exc.detail}"
            )
            raise
        
        except Exception as exc:
            # Log unexpected errors
            error_id = generate_error_id()
            logger.error(
                f"Unexpected error in {self.app_name} [{error_id}]: {str(exc)}\n"
                f"{''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))}"
            )
            
            if app.debug:
                raise
            
            return response.json({
                "error": "Internal server error",
                "error_id": error_id
            }, status_code=500)

# Add error handling middleware
app.add_middleware(ErrorHandlingMiddleware("my-api"))
```

## Database Error Handling

```python
from sqlalchemy.exc import IntegrityError, OperationalError
from databases.core import DatabaseError

# Database exception handler
@app.add_exception_handler(IntegrityError)
async def handle_db_integrity_error(request: Request, response: Response, exc: IntegrityError):
    error_message = str(exc)
    if "unique constraint" in error_message.lower():
        return response.json({
            "error": "Resource already exists",
            "detail": "A resource with these unique fields already exists"
        }, status_code=409)
    return response.json({
        "error": "Database integrity error",
        "detail": "The operation could not be completed"
    }, status_code=400)

@app.add_exception_handler(OperationalError)
async def handle_db_operational_error(request: Request, response: Response, exc: OperationalError):
    logger.error(f"Database operational error: {str(exc)}")
    return response.json({
        "error": "Database error",
        "detail": "A database error occurred"
    }, status_code=503)

@app.add_exception_handler(DatabaseError)
async def handle_database_error(request: Request, response: Response, exc: DatabaseError):
    logger.error(f"Database error: {str(exc)}")
    return response.json({
        "error": "Database error",
        "detail": "A database error occurred"
    }, status_code=503)
```

## Error Response Structure

```python
from datetime import datetime
from typing import Optional, Any, Dict

class ErrorResponse(BaseModel):
    status_code: int
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
    path: str
    method: str
    metadata: Dict[str, Any] = {}

class ErrorHandlerMiddleware:
    async def __call__(
        self,
        request: Request,
        response: Response,
        call_next: Callable
    ):
        try:
            return await call_next()
        except Exception as exc:
            status_code = getattr(exc, "status_code", 500)
            error_code = getattr(exc, "error_code", None)
            metadata = getattr(exc, "metadata", {})
            
            error_response = ErrorResponse(
                status_code=status_code,
                error=exc.__class__.__name__,
                detail=str(exc),
                error_code=error_code,
                path=request.url.path,
                method=request.method,
                metadata=metadata
            )
            
            return response.json(
                error_response.dict(),
                status_code=status_code
            )
```

## Exercises

1. **Custom Error Registry**:
   Create a system to manage and register custom errors:
   ```python
   class ErrorRegistry:
       def __init__(self):
           self.errors = {}
       
       def register(self, error_code: str, status_code: int, message_template: str):
           self.errors[error_code] = {
               "status_code": status_code,
               "message_template": message_template
           }
       
       def create_error(self, error_code: str, **kwargs):
           if error_code not in self.errors:
               raise ValueError(f"Unknown error code: {error_code}")
           
           error_info = self.errors[error_code]
           message = error_info["message_template"].format(**kwargs)
           
           return APIError(
               status_code=error_info["status_code"],
               detail=message,
               error_code=error_code,
               metadata=kwargs
           )

   # Usage
   error_registry = ErrorRegistry()
   error_registry.register(
       "USER_NOT_FOUND",
       404,
       "User with id {user_id} not found"
   )
   
   # Raise error
   raise error_registry.create_error("USER_NOT_FOUND", user_id="123")
   ```

2. **Error Monitoring System**:
   Implement error tracking and monitoring:
   ```python
   class ErrorMonitor:
       def __init__(self):
           self.errors = []
       
       def record_error(self, error: dict):
           self.errors.append({
               **error,
               "timestamp": datetime.utcnow()
           })
       
       def get_error_stats(self, minutes: int = 5):
           cutoff = datetime.utcnow() - timedelta(minutes=minutes)
           recent_errors = [
               e for e in self.errors
               if e["timestamp"] > cutoff
           ]
           
           return {
               "total": len(recent_errors),
               "by_status": Counter(e["status_code"] for e in recent_errors),
               "by_path": Counter(e["path"] for e in recent_errors)
           }

   error_monitor = ErrorMonitor()
   ```

3. **Rate Limit Error Handler**:
   Create a specialized rate limit error handler:
   ```python
   class RateLimitExceeded(APIError):
       def __init__(
           self,
           limit: int,
           reset_in: int,
           scope: str = "global"
       ):
           super().__init__(
               status_code=429,
               detail="Rate limit exceeded",
               error_code="RATE_LIMIT_EXCEEDED",
               metadata={
                   "limit": limit,
                   "reset_in": reset_in,
                   "scope": scope
               }
           )

   @app.add_exception_handler(RateLimitExceeded)
   async def handle_rate_limit(request: Request, response: Response, exc: RateLimitExceeded):
       response.headers.update({
           "X-RateLimit-Limit": str(exc.metadata["limit"]),
           "X-RateLimit-Reset": str(exc.metadata["reset_in"]),
           "Retry-After": str(exc.metadata["reset_in"])
       })
       
       return response.json({
           "error": "Rate limit exceeded",
           "detail": f"Please try again in {exc.metadata['reset_in']} seconds",
           "scope": exc.metadata["scope"]
       }, status_code=429)
   ```

## Mini-Project: Error Handling System

Create a comprehensive error handling system:

```python
from nexios import NexiosApp
from nexios.http import Request, Response
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging
import json
import traceback
import uuid
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Error severity levels
class ErrorSeverity(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

# Base error response model
class ErrorDetail(BaseModel):
    message: str
    code: str
    severity: ErrorSeverity
    timestamp: datetime = datetime.utcnow()
    trace_id: str = str(uuid.uuid4())
    metadata: Dict[str, Any] = {}

# Custom error base class
class AppError(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        metadata: Dict[str, Any] = None
    ):
        self.message = message
        self.code = code
        self.severity = severity
        self.metadata = metadata or {}
        super().__init__(message)

# Error monitoring
class ErrorMonitor:
    def __init__(self):
        self.errors: List[Dict] = []
        self.alert_threshold = 10  # Alert if more than 10 errors in 5 minutes
    
    def record_error(self, error: ErrorDetail):
        self.errors.append(error.dict())
        self._check_alert_threshold()
    
    def _check_alert_threshold(self):
        recent_errors = [
            e for e in self.errors
            if datetime.fromisoformat(e["timestamp"]) > datetime.utcnow() - timedelta(minutes=5)
        ]
        
        if len(recent_errors) > self.alert_threshold:
            self._send_alert(recent_errors)
    
    def _send_alert(self, errors: List[Dict]):
        # In production, send to monitoring service
        logger.critical(
            f"Error threshold exceeded! {len(errors)} errors in last 5 minutes"
        )

# Error handler middleware
class ErrorHandlerMiddleware:
    def __init__(self):
        self.monitor = ErrorMonitor()
    
    async def __call__(
        self,
        request: Request,
        response: Response,
        call_next: Callable
    ):
        try:
            return await call_next()
        
        except AppError as exc:
            error_detail = ErrorDetail(
                message=exc.message,
                code=exc.code,
                severity=exc.severity,
                metadata=exc.metadata
            )
            
            # Record error
            self.monitor.record_error(error_detail)
            
            # Log error
            log_method = getattr(logger, exc.severity.value)
            log_method(
                f"Application error: {exc.message}",
                extra={
                    "trace_id": error_detail.trace_id,
                    "code": exc.code,
                    "metadata": exc.metadata
                }
            )
            
            return response.json(
                error_detail.dict(),
                status_code=self._get_status_code(exc.severity)
            )
        
        except Exception as exc:
            trace_id = str(uuid.uuid4())
            
            error_detail = ErrorDetail(
                message="Internal server error",
                code="INTERNAL_ERROR",
                severity=ErrorSeverity.CRITICAL,
                trace_id=trace_id,
                metadata={
                    "error_type": exc.__class__.__name__,
                    "error_detail": str(exc)
                }
            )
            
            # Record error
            self.monitor.record_error(error_detail)
            
            # Log error with stack trace
            logger.error(
                f"Unexpected error: {str(exc)}",
                extra={
                    "trace_id": trace_id,
                    "traceback": traceback.format_exc()
                }
            )
            
            return response.json(
                error_detail.dict(),
                status_code=500
            )
    
    def _get_status_code(self, severity: ErrorSeverity) -> int:
        return {
            ErrorSeverity.DEBUG: 400,
            ErrorSeverity.INFO: 400,
            ErrorSeverity.WARNING: 400,
            ErrorSeverity.ERROR: 500,
            ErrorSeverity.CRITICAL: 500
        }[severity]

# Application setup
app = NexiosApp()
app.add_middleware(ErrorHandlerMiddleware())

# Custom error types
class ValidationError(AppError):
    def __init__(self, message: str, field: str):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            severity=ErrorSeverity.WARNING,
            metadata={"field": field}
        )

class ResourceNotFound(AppError):
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with id {resource_id} not found",
            code="RESOURCE_NOT_FOUND",
            severity=ErrorSeverity.INFO,
            metadata={
                "resource_type": resource_type,
                "resource_id": resource_id
            }
        )

class DatabaseError(AppError):
    def __init__(self, operation: str, detail: str):
        super().__init__(
            message=f"Database error during {operation}",
            code="DATABASE_ERROR",
            severity=ErrorSeverity.CRITICAL,
            metadata={
                "operation": operation,
                "detail": detail
            }
        )

# Example routes
@app.post("/users")
async def create_user(request: Request, response: Response):
    try:
        data = await request.json()
    except json.JSONDecodeError:
        raise ValidationError("Invalid JSON", field="request_body")
    
    if "username" not in data:
        raise ValidationError("Username is required", field="username")
    
    if len(data["username"]) < 3:
        raise ValidationError(
            "Username must be at least 3 characters",
            field="username"
        )
    
    # Simulate database error
    if data["username"] == "error":
        raise DatabaseError(
            operation="create_user",
            detail="Unique constraint violation"
        )
    
    return response.json({"id": "123", **data}, status_code=201)

@app.get("/users/{user_id}")
async def get_user(request: Request, response: Response, user_id: str):
    if user_id == "missing":
        raise ResourceNotFound("User", user_id)
    
    return response.json({"id": user_id, "username": "test"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
```

## Key Concepts Learned

- Exception handling basics
- Custom exception types
- Global exception handlers
- Error middleware
- Database error handling
- Error response structure
- Error monitoring and logging
- Rate limit handling
- Error severity levels
- Trace IDs for debugging

## Additional Resources

- [Nexios Error Handling Documentation](https://nexios.dev/guide/errors)
- [Python Exception Handling](https://docs.python.org/3/tutorial/errors.html)
- [REST API Error Handling Best Practices](https://www.rfc-editor.org/rfc/rfc7807)
- [Logging Best Practices](https://docs.python.org/3/howto/logging.html)

## Homework

1. Implement a comprehensive error handling system:
   - Custom exception hierarchy
   - Error registry
   - Error monitoring
   - Logging system
   - Alert system

2. Create specialized error handlers:
   - Authentication errors
   - Validation errors
   - Database errors
   - Rate limit errors
   - File handling errors

3. Build an error reporting dashboard:
   - Error statistics
   - Error trends
   - Error details
   - Search and filtering

## Next Steps

Tomorrow, we'll explore database integration in [Day 7: Database Integration](../day07/index.md). 
# 🚀 Day 16: Error Handling

## Exception Handling

Implementing comprehensive exception handling:

```python
from nexios import get_application
from nexios.exceptions import (
    HTTPException,
    ValidationError,
    DatabaseError,
    AuthenticationError,
    AuthorizationError
)
from nexios.http import Request, Response
from typing import Any, Dict, Optional
import traceback
import logging

app = get_application()
logger = logging.getLogger(__name__)

class APIError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        code: str = "internal_error",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}
        super().__init__(message)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
) -> Response:
    # Log the error
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True
    )
    
    # Convert to API error
    if isinstance(exc, APIError):
        return Response(
            content={
                "error": exc.message,
                "code": exc.code,
                "details": exc.details
            },
            status_code=exc.status_code
        )
    
    # Handle HTTP exceptions
    if isinstance(exc, HTTPException):
        return Response(
            content={
                "error": str(exc),
                "code": "http_error",
                "status": exc.status_code
            },
            status_code=exc.status_code
        )
    
    # Handle validation errors
    if isinstance(exc, ValidationError):
        return Response(
            content={
                "error": "Validation error",
                "code": "validation_error",
                "details": exc.errors()
            },
            status_code=422
        )
    
    # Handle database errors
    if isinstance(exc, DatabaseError):
        return Response(
            content={
                "error": "Database error",
                "code": "database_error"
            },
            status_code=500
        )
    
    # Handle auth errors
    if isinstance(exc, AuthenticationError):
        return Response(
            content={
                "error": "Authentication required",
                "code": "auth_required"
            },
            status_code=401
        )
    
    if isinstance(exc, AuthorizationError):
        return Response(
            content={
                "error": "Access denied",
                "code": "access_denied"
            },
            status_code=403
        )
    
    # Generic error response
    return Response(
        content={
            "error": "Internal server error",
            "code": "internal_error"
        },
        status_code=500
    )

# Custom error handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(
    request: Request,
    exc: ValidationError
) -> Response:
    return Response(
        content={
            "error": "Validation error",
            "code": "validation_error",
            "fields": [
                {
                    "field": error["loc"][-1],
                    "message": error["msg"],
                    "type": error["type"]
                }
                for error in exc.errors()
            ]
        },
        status_code=422
    )
```

## Error Responses

Standardizing error responses:

```python
from enum import Enum
from pydantic import BaseModel
from typing import Optional, Any, List

class ErrorCode(str, Enum):
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    RATE_LIMITED = "rate_limited"
    INTERNAL_ERROR = "internal_error"

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str
    code: str
    context: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    error: str
    code: ErrorCode
    details: Optional[List[ErrorDetail]] = None
    request_id: Optional[str] = None

# Error response middleware
@app.middleware("http")
async def error_response_middleware(
    request: Request,
    call_next
) -> Response:
    try:
        return await call_next(request)
    except Exception as exc:
        if isinstance(exc, HTTPException):
            return Response(
                content=ErrorResponse(
                    error=str(exc),
                    code=ErrorCode.INTERNAL_ERROR,
                    request_id=request.id
                ).dict(),
                status_code=exc.status_code
            )
        
        # Log unexpected errors
        logger.exception(
            "Unexpected error",
            extra={
                "request_id": request.id,
                "path": request.url.path
            }
        )
        
        return Response(
            content=ErrorResponse(
                error="Internal server error",
                code=ErrorCode.INTERNAL_ERROR,
                request_id=request.id
            ).dict(),
            status_code=500
        )

# Example usage
@app.get("/items/{item_id}")
async def get_item(item_id: str):
    item = await find_item(item_id)
    
    if not item:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error=f"Item {item_id} not found",
                code=ErrorCode.NOT_FOUND,
                details=[
                    ErrorDetail(
                        field="item_id",
                        message="Item not found",
                        code="invalid_id"
                    )
                ]
            ).dict()
        )
    
    return item
```

## Logging

Implementing structured logging:

```python
import logging
import json
from datetime import datetime
from typing import Any, Dict
import sys

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        # Add exception info
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(
                    *record.exc_info
                )
            }
        
        return json.dumps(log_data)

# Configure logging
def setup_logging():
    logger = logging.getLogger("nexios")
    logger.setLevel(logging.INFO)
    
    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(JSONFormatter())
    logger.addHandler(console)
    
    # File handler
    file_handler = logging.FileHandler("app.log")
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    return logger

# Initialize logger
logger = setup_logging()

# Logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Generate request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Log request
    logger.info(
        "Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host
        }
    )
    
    try:
        response = await call_next(request)
        
        # Log response
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration": time.time() - start_time
            }
        )
        
        return response
    
    except Exception as e:
        # Log error
        logger.error(
            "Request failed",
            extra={
                "request_id": request_id,
                "error": str(e),
                "duration": time.time() - start_time
            },
            exc_info=True
        )
        raise
```

## Monitoring

Setting up application monitoring:

```python
from nexios.monitoring import (
    Monitor,
    Metric,
    Counter,
    Gauge,
    Histogram
)
from prometheus_client import (
    CollectorRegistry,
    generate_latest
)

# Initialize monitoring
monitor = Monitor()

# Define metrics
http_requests = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"]
)

request_duration = Histogram(
    "request_duration_seconds",
    "Request duration in seconds",
    ["method", "path"]
)

active_connections = Gauge(
    "active_connections",
    "Number of active connections"
)

# Monitoring middleware
@app.middleware("http")
async def monitoring_middleware(request: Request, call_next):
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        # Record metrics
        http_requests.labels(
            method=request.method,
            path=request.url.path,
            status=response.status_code
        ).inc()
        
        request_duration.labels(
            method=request.method,
            path=request.url.path
        ).observe(time.time() - start_time)
        
        return response
    
    except Exception:
        http_requests.labels(
            method=request.method,
            path=request.url.path,
            status=500
        ).inc()
        raise

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    # Check critical services
    db_healthy = await check_database()
    cache_healthy = await check_cache()
    queue_healthy = await check_queue()
    
    status = (
        "healthy"
        if all([db_healthy, cache_healthy, queue_healthy])
        else "unhealthy"
    )
    
    return {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "up" if db_healthy else "down",
            "cache": "up" if cache_healthy else "down",
            "queue": "up" if queue_healthy else "down"
        }
    }
```

## 📝 Practice Exercise

1. Implement error handling:
   - Custom exceptions
   - Error middleware
   - Validation errors
   - Database errors

2. Set up logging:
   - Structured logging
   - Log rotation
   - Error tracking
   - Performance logging

3. Add monitoring:
   - Health checks
   - Metrics collection
   - Performance tracking
   - Alerting system

## 📚 Additional Resources
- [Error Handling Guide](https://nexios.dev/guide/errors)
- [Logging Best Practices](https://nexios.dev/guide/logging)
- [Monitoring Guide](https://nexios.dev/guide/monitoring)
- [Prometheus Integration](https://nexios.dev/guide/prometheus)

## 🎯 Next Steps
Tomorrow in [Day 17: Advanced Middleware](../day17/index.md), we'll explore:
- Custom middleware
- Middleware chains
- Global middleware
- Context management
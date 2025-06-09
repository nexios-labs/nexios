# 🚀 Day 17: Advanced Middleware

## Custom Middleware

Creating custom middleware components:

```python
from nexios import get_application
from nexios.http import Request, Response
from nexios.middleware import Middleware
from typing import Callable, Optional
import time
import uuid

app = get_application()

# Timing middleware
class TimingMiddleware(Middleware):
    async def __call__(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        start_time = time.time()
        
        response = await call_next(request)
        
        # Add timing header
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        
        return response

# Request ID middleware
class RequestIDMiddleware(Middleware):
    def __init__(self, header_name: str = "X-Request-ID"):
        self.header_name = header_name
    
    async def __call__(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # Get or generate request ID
        request_id = request.headers.get(
            self.header_name,
            str(uuid.uuid4())
        )
        
        # Add to request state
        request.state.request_id = request_id
        
        response = await call_next(request)
        
        # Add to response headers
        response.headers[self.header_name] = request_id
        
        return response

# Rate limiting middleware
class RateLimitMiddleware(Middleware):
    def __init__(
        self,
        requests_per_minute: int = 60,
        block_duration: int = 60
    ):
        self.limit = requests_per_minute
        self.duration = block_duration
        self.requests = {}
    
    async def __call__(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old records
        self.clean_old_requests(current_time)
        
        # Check rate limit
        if self.is_rate_limited(client_ip, current_time):
            return Response(
                content={"error": "Rate limit exceeded"},
                status_code=429
            )
        
        # Record request
        self.record_request(client_ip, current_time)
        
        return await call_next(request)
    
    def clean_old_requests(self, current_time: float):
        cutoff = current_time - self.duration
        self.requests = {
            ip: times for ip, times in self.requests.items()
            if any(t > cutoff for t in times)
        }
    
    def is_rate_limited(self, ip: str, current_time: float) -> bool:
        if ip not in self.requests:
            return False
        
        recent_requests = [
            t for t in self.requests[ip]
            if t > current_time - self.duration
        ]
        
        return len(recent_requests) >= self.limit
    
    def record_request(self, ip: str, time: float):
        if ip not in self.requests:
            self.requests[ip] = []
        self.requests[ip].append(time)

# Add middleware to app
app.add_middleware(TimingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=30)
```

## Middleware Chains

Managing middleware execution order:

```python
from nexios.middleware import MiddlewareChain
from typing import List, Type

class MiddlewareManager:
    def __init__(self):
        self.chains: Dict[str, MiddlewareChain] = {}
    
    def create_chain(
        self,
        name: str,
        middlewares: List[Type[Middleware]]
    ):
        chain = MiddlewareChain()
        
        for middleware in middlewares:
            chain.add(middleware)
        
        self.chains[name] = chain
    
    def get_chain(self, name: str) -> Optional[MiddlewareChain]:
        return self.chains.get(name)

# Initialize manager
middleware_manager = MiddlewareManager()

# Create middleware chains
middleware_manager.create_chain(
    "api",
    [
        TimingMiddleware,
        RequestIDMiddleware,
        RateLimitMiddleware
    ]
)

middleware_manager.create_chain(
    "web",
    [
        TimingMiddleware,
        RequestIDMiddleware
    ]
)

# Apply middleware chain to router
api_router = Router(prefix="/api")
api_chain = middleware_manager.get_chain("api")
api_router.middleware = api_chain

web_router = Router(prefix="/web")
web_chain = middleware_manager.get_chain("web")
web_router.middleware = web_chain

# Include routers
app.include_router(api_router)
app.include_router(web_router)
```

## Global Middleware

Implementing application-wide middleware:

```python
from nexios.security import SecurityHeaders
from nexios.cors import CORSMiddleware
from nexios.compression import CompressionMiddleware

# Security headers middleware
class SecurityHeadersMiddleware(Middleware):
    def __init__(self, **options):
        self.headers = SecurityHeaders(**options)
    
    async def __call__(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        response = await call_next(request)
        
        # Add security headers
        headers = self.headers.get_headers()
        response.headers.update(headers)
        
        return response

# Add global middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_middleware(
    SecurityHeadersMiddleware,
    xss_protection=True,
    content_type_options=True,
    frame_options="DENY",
    hsts=True
)

app.add_middleware(
    CompressionMiddleware,
    minimum_size=1000,
    compression_level=6
)

# Order-specific middleware
@app.middleware("http", order=1)
async def first_middleware(request: Request, call_next):
    # Executes first
    return await call_next(request)

@app.middleware("http", order=2)
async def second_middleware(request: Request, call_next):
    # Executes second
    return await call_next(request)
```

## Context Management

Managing request context in middleware:

```python
from contextvars import ContextVar
from typing import Optional, Any

# Context variables
request_id: ContextVar[str] = ContextVar("request_id")
current_user: ContextVar[Optional[dict]] = ContextVar(
    "current_user",
    default=None
)
trace_id: ContextVar[str] = ContextVar("trace_id")

class ContextMiddleware(Middleware):
    async def __call__(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # Set context variables
        request_id.set(str(uuid.uuid4()))
        trace_id.set(
            request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        )
        
        try:
            return await call_next(request)
        finally:
            # Clean up context
            request_id.set(None)
            trace_id.set(None)

# Context manager for database transactions
class TransactionContext:
    def __init__(self, db):
        self.db = db
    
    async def __aenter__(self):
        self.transaction = await self.db.transaction()
        return self.transaction
    
    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is None:
            await self.transaction.commit()
        else:
            await self.transaction.rollback()

# Transaction middleware
class TransactionMiddleware(Middleware):
    def __init__(self, db):
        self.db = db
    
    async def __call__(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        async with TransactionContext(self.db):
            return await call_next(request)

# Context-aware logging
class LogContext:
    def __init__(self):
        self.request_id = request_id.get()
        self.trace_id = trace_id.get()
        self.user = current_user.get()
    
    def get_context(self) -> dict:
        return {
            "request_id": self.request_id,
            "trace_id": self.trace_id,
            "user_id": self.user.get("id") if self.user else None
        }

# Logging middleware with context
class ContextualLoggingMiddleware(Middleware):
    def __init__(self, logger):
        self.logger = logger
    
    async def __call__(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        context = LogContext()
        
        self.logger.info(
            "Request started",
            extra={
                **context.get_context(),
                "method": request.method,
                "path": request.url.path
            }
        )
        
        try:
            response = await call_next(request)
            
            self.logger.info(
                "Request completed",
                extra={
                    **context.get_context(),
                    "status_code": response.status_code
                }
            )
            
            return response
        
        except Exception as e:
            self.logger.error(
                "Request failed",
                extra={
                    **context.get_context(),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
```

## 📝 Practice Exercise

1. Create custom middleware:
   - Authentication
   - Caching
   - Request validation
   - Response transformation

2. Implement middleware chains:
   - Route-specific chains
   - Conditional middleware
   - Dynamic chain building
   - Chain ordering

3. Build context management:
   - Request tracking
   - User context
   - Resource cleanup
   - Error handling

## 📚 Additional Resources
- [Middleware Guide](https://nexios.dev/guide/middleware)
- [Context Management](https://nexios.dev/guide/context)
- [Security Headers](https://nexios.dev/guide/security)
- [CORS Configuration](https://nexios.dev/guide/cors)

## 🎯 Next Steps
Tomorrow in [Day 18: Advanced Routing](../day18/index.md), we'll explore:
- Route groups
- Dynamic routes
- Route dependencies
- URL generation 
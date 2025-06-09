# Day 5: Middleware in Nexios


## Custom Middleware

Creating your own middleware:

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
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Authentication middleware
async def auth_middleware(
    request: Request,
    response: Response,
    call_next: Middleware
) -> Response:
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return Response(
            content={"error": "API key required"},
            status_code=401
        )
    
    if not is_valid_api_key(api_key):
        return Response(
            content={"error": "Invalid API key"},
            status_code=403
        )
    
    return await call_next()

# Add middleware to app
app.add_middleware(timing_middleware)
app.add_middleware(auth_middleware)
```

## Global vs Route-specific Middleware

You can apply middleware globally or to specific routes:

```python
from nexios import NexiosApp, Router
from nexios.http import Request, Response
from nexios.types import Middleware
from typing import Callable

app = NexiosApp()

# Route-specific middleware
async def admin_only(
    request: Request,
    response: Response,
    call_next: Middleware
) -> Response:
    if not request.user.is_admin:
        return Response(
            content={"error": "Admin access required"},
            status_code=403
        )
    return await call_next()

# Admin router with middleware
admin_router = Router(prefix="/admin")
admin_router.add_middleware(admin_only)

@admin_router.get("/stats")
async def admin_stats():
    return {"stats": "admin only data"}

# Include router in main app
app.mount_router(admin_router)

# Regular routes (no admin middleware)
@app.get("/public")
async def public_route():
    return {"message": "Public data"}
```

## Middleware Classes

For more complex middleware, use classes:

```python
from nexios import NexiosApp
from nexios.http import Request, Response
from nexios.types import Middleware
from typing import Optional

class RateLimiter:
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
        response: Response,
        call_next: Middleware
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
        
        return await call_next()
    
    def clean_old_requests(self, current_time: float) -> None:
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
    
    def record_request(self, ip: str, time: float) -> None:
        if ip not in self.requests:
            self.requests[ip] = []
        self.requests[ip].append(time)

# Use the rate limiter
app.add_middleware(RateLimiter(requests_per_minute=30))
```

## Practice Exercise

Create these middleware components:

1. Request/Response Logger
2. Cache Middleware
3. Error Handler
4. Authentication Middleware
5. Response Transformer

## Additional Resources
- [Middleware Guide](../../guide/middleware.md)

- [Error Handling](../../guide/error-handling.md)

## 🎯 Next Steps
Tomorrow in [Day 6: Environment Configuration](../day06/index.md), we'll explore:
- Using `.env` files
- CORS configuration
- JSON limits
- Development vs production settings
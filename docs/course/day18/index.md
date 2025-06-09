# Day 18: Custom Decorators

## Learning Objectives
- Understand decorator patterns in Nexios
- Create custom route decorators
- Implement middleware decorators
- Build utility decorators

## Basic Decorator Pattern

Creating simple decorators in Nexios:

```python
from nexios import NexiosApp
from nexios.http import Request, Response
from functools import wraps
from typing import Callable, Any
import time

app = NexiosApp()

def timing_decorator(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start_time
        
        # Add timing header to response
        if isinstance(result, Response):
            result.headers["X-Response-Time"] = f"{duration:.4f}s"
        return result
    return wrapper

@app.get("/timed")
@timing_decorator
async def timed_endpoint(request: Request):
    return {"message": "This response is timed"}
```

## Route Decorators

Creating decorators for route handling:

```python
from nexios.http import Request, Response
from nexios.exceptions import HTTPException
import json

def validate_json(*required_fields: str):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs) -> Any:
            try:
                data = await request.json
                # Check required fields
                missing = [field for field in required_fields 
                          if field not in data]
                if missing:
                    return Response(
                        content={"error": f"Missing fields: {missing}"},
                        status_code=400
                    )
                # Add validated data to request
                request.state.validated_data = data
                return await func(request, *args, **kwargs)
            except json.JSONDecodeError:
                return Response(
                    content={"error": "Invalid JSON"},
                    status_code=400
                )
        return wrapper
    return decorator

@app.post("/users")
@validate_json("username", "email")
async def create_user(request: Request):
    data = request.state.validated_data
    return {"message": "User created", "data": data}
```

## Middleware Decorators

Creating reusable middleware decorators:

```python
from nexios.http import Request, Response
from nexios.middleware import Middleware
from typing import Optional

def rate_limit(requests: int, window: int = 60):
    def decorator(func: Callable) -> Callable:
        # Store request counts
        counters = {}
        
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs) -> Any:
            # Get client IP
            client_ip = request.client.host
            now = time.time()
            
            # Clean old entries
            counters[client_ip] = [
                ts for ts in counters.get(client_ip, [])
                if now - ts < window
            ]
            
            # Check rate limit
            if len(counters[client_ip]) >= requests:
                return Response(
                    content={"error": "Rate limit exceeded"},
                    status_code=429
                )
            
            # Add new request timestamp
            counters[client_ip].append(now)
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

@app.get("/limited")
@rate_limit(requests=5, window=60)
async def limited_endpoint(request: Request):
    return {"message": "Rate limited endpoint"}
```

## Advanced Patterns

Combining multiple decorators and middleware:

```python
from nexios.auth import auth
from nexios.cache import cache
from typing import List

def roles_required(roles: List[str]):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs) -> Any:
            user = request.user
            if not any(role in user.roles for role in roles):
                return Response(
                    content={"error": "Insufficient permissions"},
                    status_code=403
                )
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

def cache_response(ttl: int = 300):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs) -> Any:
            # Generate cache key
            cache_key = f"{request.method}:{request.url.path}"
            
            # Try to get from cache
            if cached := await cache.get(cache_key):
                return Response(
                    content=cached,
                    headers={"X-Cache": "HIT"}
                )
            
            # Get fresh response
            response = await func(request, *args, **kwargs)
            
            # Cache the response
            if isinstance(response, Response):
                await cache.set(
                    cache_key,
                    response.body,
                    ttl=ttl
                )
            
            return response
        return wrapper
    return decorator

@app.get("/admin/stats")
@auth(["jwt"])
@roles_required(["admin"])
@cache_response(ttl=60)
async def admin_stats(request: Request):
    stats = await generate_stats()
    return {"stats": stats}
```

## 📝 Practice Exercise

1. Create utility decorators:
   - Request validation
   - Response transformation
   - Error handling
   - Performance monitoring

2. Build authentication decorators:
   - Role-based access control
   - API key validation
   - Rate limiting
   - Token refresh

3. Implement caching decorators:
   - Response caching
   - Query result caching
   - Cache invalidation
   - Cache dependencies

## 📚 Additional Resources
- [Python Decorators](https://docs.python.org/3/glossary.html#term-decorator)
- [Nexios Middleware](../../guide/middleware.md)
- [Authentication](../../guide/authentication.md)
- [Caching](../../guide/caching.md)

## 🎯 Next Steps
Tomorrow in [Day 19: Dependency Injection](../day19/index.md), we'll explore:
- Service containers
- Dependency management
- Lifecycle hooks
- Testing with DI
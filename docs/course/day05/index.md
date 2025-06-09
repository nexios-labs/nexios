# Day 5: Basic Middleware

Welcome to Day 5! Today we'll explore middleware in Nexios, learning how to intercept and modify requests and responses.

## Understanding Middleware

Middleware are functions that run before or after your request handlers, allowing you to:
- Modify requests and responses
- Perform authentication
- Log requests
- Handle errors
- Add custom headers
- And more!

## Basic Middleware Structure

```python
from nexios import NexiosApp
from nexios.http import Request, Response
from typing import Callable
import time

app = NexiosApp()

async def timing_middleware(request: Request, response: Response, call_next: Callable):
    # Before the request
    start_time = time.time()
    
    # Call the next middleware or route handler
    response = await call_next()
    
    # After the request
    duration = time.time() - start_time
    response.headers["X-Process-Time"] = f"{duration:.4f} seconds"
    
    return response

# Add middleware to the application
app.add_middleware(timing_middleware)
```

## Common Middleware Patterns

### 1. Authentication Middleware

```python
from nexios.exceptions import HTTPException

async def auth_middleware(request: Request, response: Response, call_next: Callable):
    auth_token = request.headers.get("Authorization")
    
    if not auth_token:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    
    # Validate token (simplified example)
    if not auth_token.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid token format"
        )
    
    # Add user info to request state
    request.state.user = {"id": 1, "username": "example"}
    
    return await call_next()

# Add to specific routes using route middleware
@app.get("/protected", middleware=[auth_middleware])
async def protected_route(request: Request, response: Response):
    user = request.state.user
    return response.json({
        "message": f"Hello, {user['username']}!"
    })
```

### 2. CORS Middleware

```python
async def cors_middleware(request: Request, response: Response, call_next: Callable):
    # Handle preflight requests
    if request.method == "OPTIONS":
        response.headers.update({
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "86400",  # 24 hours
        })
        return response
    
    # Handle actual requests
    response = await call_next()
    
    response.headers.update({
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true",
    })
    
    return response

app.add_middleware(cors_middleware)
```

### 3. Logging Middleware

```python
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def logging_middleware(request: Request, response: Response, call_next: Callable):
    # Log request
    timestamp = datetime.now().isoformat()
    logger.info(f"[{timestamp}] {request.method} {request.url.path}")
    
    try:
        response = await call_next()
        # Log response
        logger.info(f"[{timestamp}] {response.status_code}")
        return response
    except Exception as e:
        # Log error
        logger.error(f"[{timestamp}] Error: {str(e)}")
        raise

app.add_middleware(logging_middleware)
```

## Middleware Classes

You can also create middleware using classes:

```python
class RateLimitMiddleware:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = {}
    
    async def __call__(self, request: Request, response: Response, call_next: Callable):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old requests
        self.requests = {
            ip: times for ip, times in self.requests.items()
            if current_time - times[-1] < 60
        }
        
        # Check rate limit
        if client_ip in self.requests:
            times = self.requests[client_ip]
            if len(times) >= self.requests_per_minute:
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests"
                )
            times.append(current_time)
        else:
            self.requests[client_ip] = [current_time]
        
        return await call_next()

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware(requests_per_minute=30))
```

## Middleware Order

The order of middleware is important. They are executed in the order they are added:

```python
async def middleware1(request: Request, response: Response, call_next: Callable):
    print("Before middleware1")
    response = await call_next()
    print("After middleware1")
    return response

async def middleware2(request: Request, response: Response, call_next: Callable):
    print("Before middleware2")
    response = await call_next()
    print("After middleware2")
    return response

app.add_middleware(middleware1)  # Executes first
app.add_middleware(middleware2)  # Executes second

# Output for a request:
# Before middleware1
# Before middleware2
# [Route handler executes]
# After middleware2
# After middleware1
```

## Error Handling in Middleware

```python
async def error_handling_middleware(request: Request, response: Response, call_next: Callable):
    try:
        return await call_next()
    except HTTPException as e:
        # Handle HTTP exceptions
        return response.json({
            "error": e.detail
        }, status_code=e.status_code)
    except Exception as e:
        # Handle unexpected errors
        return response.json({
            "error": "Internal server error",
            "detail": str(e) if app.debug else None
        }, status_code=500)

app.add_middleware(error_handling_middleware)
```

## Exercises

1. **Request Validation Middleware**:
   Create middleware that validates request data against Pydantic models:
   ```python
   from pydantic import BaseModel, ValidationError
   
   class UserCreate(BaseModel):
       username: str
       email: str
       password: str
   
   async def validation_middleware(request: Request, response: Response, call_next: Callable):
       if hasattr(request.route, "request_model"):
           try:
               data = await request.json()
               validated_data = request.route.request_model(**data)
               request.validated_data = validated_data
           except ValidationError as e:
               return response.json({
                   "error": "Validation error",
                   "details": e.errors()
               }, status_code=422)
       
       return await call_next()
   ```

2. **Caching Middleware**:
   Implement a simple caching system:
   ```python
   from functools import lru_cache
   
   class CacheMiddleware:
       def __init__(self):
           self.cache = {}
       
       async def __call__(self, request: Request, response: Response, call_next: Callable):
           if request.method != "GET":
               return await call_next()
           
           cache_key = request.url.path
           
           if cache_key in self.cache:
               return response.json(self.cache[cache_key])
           
           response = await call_next()
           
           if response.status_code == 200:
               self.cache[cache_key] = response.body
           
           return response
   ```

3. **Security Headers Middleware**:
   Add security headers to responses:
   ```python
   async def security_headers_middleware(request: Request, response: Response, call_next: Callable):
       response = await call_next()
       
       response.headers.update({
           "X-Content-Type-Options": "nosniff",
           "X-Frame-Options": "DENY",
           "X-XSS-Protection": "1; mode=block",
           "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
           "Content-Security-Policy": "default-src 'self'"
       })
       
       return response
   ```

## Mini-Project: API Gateway Middleware

Create a simple API gateway with middleware for authentication, rate limiting, and logging:

```python
from nexios import NexiosApp
from nexios.http import Request, Response
from typing import Callable, Dict, List
import time
import jwt
import logging
from datetime import datetime, timedelta

app = NexiosApp()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simulated API keys database
API_KEYS = {
    "test-key": {
        "client": "test-client",
        "rate_limit": 60  # requests per minute
    }
}

class APIGatewayMiddleware:
    def __init__(self):
        self.requests: Dict[str, List[float]] = {}
    
    async def __call__(self, request: Request, response: Response, call_next: Callable):
        # 1. Authentication
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key not in API_KEYS:
            return response.json({
                "error": "Invalid API key"
            }, status_code=401)
        
        client = API_KEYS[api_key]["client"]
        rate_limit = API_KEYS[api_key]["rate_limit"]
        
        # 2. Rate Limiting
        current_time = time.time()
        if client in self.requests:
            # Remove requests older than 1 minute
            self.requests[client] = [
                t for t in self.requests[client]
                if current_time - t < 60
            ]
            
            if len(self.requests[client]) >= rate_limit:
                return response.json({
                    "error": "Rate limit exceeded"
                }, status_code=429)
            
            self.requests[client].append(current_time)
        else:
            self.requests[client] = [current_time]
        
        # 3. Request Logging
        logger.info(f"[{datetime.now().isoformat()}] Client: {client} Path: {request.url.path}")
        
        try:
            # 4. Process Request
            start_time = time.time()
            response = await call_next()
            duration = time.time() - start_time
            
            # 5. Response Headers
            response.headers.update({
                "X-API-Client": client,
                "X-Process-Time": f"{duration:.4f}s",
                "X-Rate-Limit-Remaining": str(rate_limit - len(self.requests[client]))
            })
            
            # 6. Response Logging
            logger.info(f"[{datetime.now().isoformat()}] Client: {client} Status: {response.status_code}")
            
            return response
        except Exception as e:
            # 7. Error Logging
            logger.error(f"[{datetime.now().isoformat()}] Client: {client} Error: {str(e)}")
            raise

# Add the gateway middleware
app.add_middleware(APIGatewayMiddleware())

# Test routes
@app.get("/api/test")
async def test_route(request: Request, response: Response):
    return response.json({
        "message": "Hello from the API!",
        "client": API_KEYS[request.headers["X-API-Key"]]["client"]
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000, reload=True)
```

## Key Concepts Learned

- Middleware basics and structure
- Request/response modification
- Authentication middleware
- CORS handling
- Logging and monitoring
- Rate limiting
- Error handling
- Middleware ordering
- Class-based middleware
- Request validation

## Additional Resources

- [Nexios Middleware Documentation](https://nexios.dev/guide/middleware)
- [Security Best Practices](https://nexios.dev/guide/security)
- [Error Handling Guide](https://nexios.dev/guide/errors)
- [Authentication Examples](https://nexios.dev/examples/auth)

## Homework

1. Create a comprehensive authentication middleware:
   - JWT token validation
   - Role-based access control
   - Session management
   - Rate limiting per user

2. Implement advanced caching middleware:
   - Redis integration
   - Cache invalidation
   - Cache headers
   - Conditional requests

3. Build monitoring middleware:
   - Request timing
   - Error tracking
   - Performance metrics
   - Health checks

## Next Steps

Tomorrow, we'll explore error handling in detail in [Day 6: Error Handling](../day06/index.md). 
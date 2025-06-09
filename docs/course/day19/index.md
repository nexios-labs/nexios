# Day 19: Dependency Injection in Nexios

Dependency injection is a design pattern that helps manage dependencies between components in your application. Nexios provides a straightforward dependency injection system that makes it easy to write clean, maintainable code.

## Core Concepts

### Basic Dependencies

The most fundamental form of dependency injection in Nexios uses the `Depend()` function to mark parameters that should be injected:

```python
from nexios import NexiosApp, Depend

app = NexiosApp()

def get_settings():
    return {"debug": True, "version": "1.0.0"}

@app.get("/config")
async def show_config(request, response, settings: dict = Depend(get_settings)):
    return settings
```

### Resource Management with Yield

For dependencies that need cleanup (like database connections), use `yield`:

```python
async def get_db_session():
    session = Session()
    try:
        yield session
    finally:
        await session.close()

@app.post("/items")
async def create_item(request, response, session = Depend(get_db_session)):
    await session.add(Item(...))
    return {"status": "created"}
```

### Sub-Dependencies

Dependencies can depend on other dependencies:

```python
async def get_db_config():
    return {"host": "localhost", "port": 5432}

async def get_db_connection(config: dict = Depend(get_db_config)):
    return Database(**config)

@app.get("/users")
async def list_users(request, response, db = Depend(get_db_connection)):
    return await db.query("SELECT * FROM users")
```

### Class-Based Dependencies

You can use classes as dependencies through their `__call__` method:

```python
def get_token():
  ...
class AuthService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    async def __call__(self, token: str = Depend(get_token)):
        return await self.verify_token(token)

auth = AuthService(secret_key="my-secret")

@app.get("/protected")
async def protected_route(request, response, user = Depend(auth)):
    return {"message": f"Welcome {user.name}"}
```

### Context-Aware Dependencies

Dependencies can access request context:

```python
async def get_user_agent(request, response):
    return request.headers.get("User-Agent")

@app.get("/ua")
async def show_ua(request, response, ua: str = Depend(get_user_agent)):
    return {"user_agent": ua}
```

## Practice Exercise: Building an Authentication System

Let's build a simple authentication system using dependency injection:

```python
from nexios import NexiosApp, Depend
from nexios.exceptions import HTTPException

app = NexiosApp()

# Simulated user database
users = {
    "token123": {"id": 1, "name": "John Doe"}
}

async def get_current_user(request, response):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(401, "Not authenticated")
    
    user = users.get(token)
    if not user:
        raise HTTPException(401, "Invalid token")
    
    return user

@app.get("/me")
async def get_profile(request, response, user = Depend(get_current_user)):
    return {"user": user}

@app.get("/admin")
async def admin_only(request, response, user = Depend(get_current_user)):
    if user["id"] != 1:  # Simple admin check
        raise HTTPException(403, "Not authorized")
    return {"message": "Welcome admin!"}
```

## Best Practices

1. **Resource Management**: Always use `yield` for dependencies that need cleanup
2. **Error Handling**: Raise appropriate exceptions in dependencies
3. **Keep Dependencies Focused**: Each dependency should have a single responsibility
4. **Use Type Hints**: They improve code readability and IDE support
5. **Document Dependencies**: Especially when they're shared across multiple handlers

## Summary

- Nexios's dependency injection system is simple but powerful
- Use `Depend()` to mark parameters for injection
- Dependencies can be functions or classes with `__call__`
- Use `yield` for proper resource management
- Dependencies can access request context and other dependencies
- Dependencies are great for code reuse and separation of concerns

## Exercise

Create a logging system using dependency injection that:
1. Logs request details
2. Tracks request timing
3. Handles different log levels based on configuration

```python
from nexios import NexiosApp, Depend
import time
import logging

app = NexiosApp()

class LoggerService:
    def __init__(self):
        self.logger = logging.getLogger("nexios")
        self.logger.setLevel(logging.INFO)
    
    async def __call__(self, request, response):
        start_time = time.time()
        log_data = {
            "method": request.method,
            "path": request.url.path,
            "start_time": start_time
        }
        return self.logger, log_data

logger_service = LoggerService()

@app.get("/hello")
async def hello(
    request, 
    response,
    log_info = Depend(logger_service)
):
    logger, log_data = log_info
    logger.info(f"Processing request to {log_data['path']}")
    
    # Simulate some work
    time.sleep(0.1)
    
    # Log completion
    duration = time.time() - log_data["start_time"]
    logger.info(f"Request completed in {duration:.2f}s")
    
    return {"message": "Hello World!"}
```

This exercise demonstrates:
- Class-based dependencies
- Request context access
- Resource tracking
- Practical logging implementation
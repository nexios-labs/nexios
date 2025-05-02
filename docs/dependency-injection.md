---
icon: syringe
---

# Dependency Injection

## Introduction to Dependency Injection in Nexios

Dependency Injection (DI) is a design pattern that helps manage dependencies between components in your application. Nexios provides a lightweight yet powerful dependency injection system that allows you to:

* Decouple your route handlers from their dependencies
* Easily inject both synchronous and asynchronous dependencies
* Write more testable and maintainable code
* Manage shared resources efficiently

## Core Components

### The Depend Class

The `Depend` class is the main building block of Nexios' dependency injection system. It declares dependencies that should be injected into your route handlers.

```python
from nexios import Depend

async def get_current_user():
    # ... logic to get current user
    return user

@app.get("/profile")
async def profile(request, response, current_user=Depend(get_current_user)):
    return {"user": current_user}
```

### The inject\_dependencies Decorator

Under the hood, the `inject_dependencies` decorator manages the injection of dependencies into your route handlers. While you typically don't need to use this decorator directly (as it's automatically applied to route handlers), understanding how it works can be helpful:

```python
from nexios import inject_dependencies

@inject_dependencies
async def my_handler(request, response, dependency=Depend(some_provider)):
    # The dependency will be automatically injected
    pass
```

## Usage Examples

### Basic Usage with Synchronous Dependencies

Here's a simple example demonstrating dependency injection with synchronous dependencies:

```python
from nexios import Depend

def get_settings():
    return {"api_version": "1.0", "environment": "production"}

@app.get("/api/info")
async def api_info(request, response, settings=Depend(get_settings)):
    return settings
```

### Working with Async Dependencies

Nexios seamlessly handles both synchronous and asynchronous dependencies:

```python
from nexios import Depend

async def get_db_connection():
    # Simulating async database connection
    return await create_db_connection()

@app.get("/users")
async def list_users(
    request, 
    response, 
    db=Depend(get_db_connection)
):
    return await db.query("SELECT * FROM users")
```

### Error Handling

Nexios provides clear error handling for dependency injection failures:

```python
from nexios import Depend

# This will raise a ValueError since no provider is specified
@app.get("/bad-route")
async def bad_route(request, response, settings=Depend()):
    return settings

# Proper error handling in a dependency provider
def get_config():
    try:
        return load_config()
    except FileNotFoundError:
        raise ValueError("Configuration file not found")

@app.get("/config")
async def get_app_config(
    request, 
    response, 
    config=Depend(get_config)
):
    return config
```

## Best Practices and Patterns

1. **Keep Dependencies Focused**
   * Each dependency provider should have a single responsibility
   * Avoid complex logic in dependency providers
2. **Reuse Dependencies**
   * Create common dependencies that can be shared across multiple handlers
   * Use dependency providers to abstract common functionality
3. **Handle Errors Gracefully**
   * Implement proper error handling in dependency providers
   * Use appropriate HTTP status codes when dependency injection fails
4. **Type Hints**
   * Use type hints with your dependencies to improve code clarity
   * Leverage IDE support for better development experience
5. **Testing**
   * Create mock dependencies for testing
   * Test dependency providers in isolation

Example of applying these practices:

```python
from typing import Dict, Optional
from nexios import Depend

async def get_db_pool():
    # Single responsibility: managing database connections
    return await create_db_pool()

class CurrentUser:
    def __init__(self, username: str, role: str):
        self.username = username
        self.role = role

async def get_current_user(
    request,
    db=Depend(get_db_pool)
) -> Optional[CurrentUser]:
    # Proper error handling and type hints
    try:
        user_data = await db.fetch_user(request.headers["authorization"])
        return CurrentUser(**user_data)
    except KeyError:
        return None
    except DatabaseError as e:
        raise HTTPException(500, "Database error")

@app.get("/admin")
async def admin_panel(
    request, 
    response,
    current_user: CurrentUser = Depend(get_current_user)
):
    if not current_user or current_user.role != "admin":
        raise HTTPException(403, "Forbidden")
    return {"message": "Welcome to admin panel"}
```

## Common Use Cases

* Authentication and authorization
* Database connections
* Configuration management
* Logging and monitoring
* External service clients
* Request-scoped resources

## Performance Considerations

The Nexios dependency injection system is designed to be lightweight and efficient. Dependencies are resolved only when needed and results can be cached when appropriate. However, keep these points in mind:

* Avoid expensive operations in dependency providers unless necessary
* Consider caching results for frequently used dependencies
* Be mindful of the number of dependencies in a single route handler

## Integration with Other Features

Dependency injection works seamlessly with other Nexios features:

* OpenAPI documentation
* Middleware
* WebSockets
* Authentication system
* Testing utilities

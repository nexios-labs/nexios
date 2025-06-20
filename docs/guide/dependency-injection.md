# Dependency Injection in Nexios

Nexios provides a powerful yet intuitive dependency injection system that helps you write clean, maintainable code. The dependency injection system allows you to separate concerns, improve testability, and create reusable components.

::: tip Dependency Injection Fundamentals
Dependency injection in Nexios provides:
- **Automatic Resolution**: Dependencies are automatically resolved and injected
- **Async Support**: Full support for async dependencies and resource management
- **Scoped Dependencies**: Different scopes for different use cases
- **Type Safety**: Type hints provide better IDE support and error detection
- **Testability**: Easy to mock dependencies for testing
- **Resource Management**: Automatic cleanup with `yield` dependencies
- **Performance**: Dependencies are cached and reused efficiently
:::

::: tip Dependency Injection Best Practices
1. **Single Responsibility**: Each dependency should have one clear purpose
2. **Interface Segregation**: Dependencies should expose only what's needed
3. **Dependency Inversion**: Depend on abstractions, not concretions
4. **Resource Management**: Use `yield` for resources that need cleanup
5. **Error Handling**: Handle dependency errors gracefully
6. **Documentation**: Document what each dependency provides
7. **Testing**: Design dependencies to be easily testable
8. **Performance**: Avoid expensive operations in dependencies
:::

::: tip Common Dependency Patterns
- **Database Connections**: Reusable database connections with automatic cleanup
- **Authentication**: User authentication and authorization
- **Configuration**: Application settings and environment variables
- **External Services**: HTTP clients, cache connections, etc.
- **Validation**: Request validation and sanitization
- **Logging**: Structured logging with context
- **Caching**: Cache connections and utilities
:::

::: tip Dependency Scopes
- **Request Scope**: New instance for each request (default)
- **Application Scope**: Single instance for the entire application
- **Session Scope**: Instance per user session
- **Custom Scopes**: Define your own scoping rules
:::

## 👓Simple Dependencies

The most basic form of dependency injection in Nexios:

```python
from nexios import NexiosApp
from nexios.dependencies import Depend

app = NexiosApp()

def get_settings():
    return {"debug": True, "version": "1.0.0"}

@app.get("/config")
async def show_config(request, response, settings: dict = Depend(get_settings)):
    return settings
```

- Use `Depend()` to mark parameters as dependencies
- Dependencies can be any callable (function, method, etc.)
- Injected automatically before your route handler executes

## Sub-Dependencies

Dependencies can depend on other dependencies:

```python
async def get_db_config():
    return {"host": "localhost", "port": 5432}

async def get_db_connection(config: dict = Depend(get_db_config)):
    return Database(**config)

@app.get("/users")
async def list_users(req, res, db: Database = Depend(get_db_connection)):
    return await db.query("SELECT * FROM users")
```


## Using Yield (Resource Management)

For resources that need cleanup, use `yield`:

```python
async def get_db_session():
    session = Session()
    try:
        yield session
    finally:
        await session.close()

@app.post("/items")
async def create_item(req, res, session = Depend(get_db_session)):
    await session.add(Item(...))
    return {"status": "created"}
```


## Using Classes as Dependencies

Classes can act as dependencies through their `__call__` method:

```python
class AuthService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    async def __call__(self, token: str = Header(...)):
        return await self.verify_token(token)

auth = AuthService(secret_key="my-secret")

@app.get("/protected")
async def protected_route(req, res, user = Depend(auth)):
    return {"message": f"Welcome {user.name}"}
```

Advantages:
- Can maintain state between requests
- Configuration happens at initialization
- Clean interface through `__call__`

## Context-Aware Dependencies

Dependencies can access request context:

```python
async def get_user_agent(request, response):
    return request.headers.get("User-Agent")

@app.get("/ua")
async def show_ua(request, response , ua: str = Depend(get_user_agent)):
    return {"user_agent": ua}
```

::: tip  💡Tip
The `request` parameter is drived from the same name in the route handler.
:::

##  Async Dependencies

Full support for async dependencies:

```python
async def fetch_remote_data():
    async with httpx.AsyncClient() as client:
        return await client.get("https://api.example.com/data")

@app.get("/remote")
async def get_remote(req, res, data = Depend(fetch_remote_data)):
    return data.json()
```

Nexios' dependency injection system gives you the power to build well-architected applications while keeping your code clean and maintainable.
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

## Deep Context-Aware Dependency Injection

Nexios supports a powerful context propagation system that lets you access request-scoped data anywhere in your dependency tree—even in deeply nested dependencies.

### What is Context?

The `Context` object is automatically created for each request and carries information about the current request and its environment. By default, it includes:
- `request`: The current `Request` object
- `user`: The authenticated user (if available)

You can extend the `Context` class to add more fields as needed for your application.

### How to Use Context in Handlers and Dependencies

#### 1. With Type Annotation
You can declare a `context: Context = None` parameter in your handler or dependency. Nexios will inject the current context automatically:

```python
from nexios.dependencies import Context

@app.get("/context-demo")
async def context_demo(req, res, context: Context = None):
    return {"path": context.request.url.path}
```

#### 2. With Default Value (No Type Annotation Needed)
You can also use `context=Context()` as a parameter. Nexios will recognize this and inject the current context automatically:

```python
@app.get("/auto-context")
async def auto_context_demo(req, res, context=Context()):
    return {"path": context.request.url.path}
```

This works for both handlers and dependencies, and even for deeply nested dependencies:

```python
async def get_user(context=Context()):
    # context is injected automatically
    return {"user": "alice", "path": context.request.url.path}

@app.get("/user-path")
async def user_path(req, res, user=Depend(get_user)):
    return user
```

#### 3. Accessing Context Anywhere
If you need to access the context outside of a function parameter, you can use the `current_context` variable:

```python
from nexios.dependencies import current_context

def some_function():
    ctx = current_context.get()
    print(ctx.request.url.path)
```

### Advanced: Deeply Nested Context Example

```python
async def dep_a(context=Context()):
    return f"A: {context.request.url.path}"

async def dep_b(a=Depend(dep_a), context=Context()):
    return f"B: {a}, {context.request.url.path}"

@app.get("/deep-context")
async def deep_context(req, res, b=Depend(dep_b)):
    return {"result": b}
```

In this example, both `dep_a` and `dep_b` receive the same context object, even though they are nested.

### Why Use Context?
- **Consistency:** All dependencies and handlers can access the same request-scoped data.
- **Flexibility:** Add custom fields to the context for your app's needs.
- **No Boilerplate:** No need to manually pass context through every function.
- **Async-Safe:** Works seamlessly with async code and deeply nested dependencies.

---

Nexios' dependency injection system gives you the power to build well-architected applications while keeping your code clean and maintainable.
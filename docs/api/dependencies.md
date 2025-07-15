# Dependencies API Reference

The Dependencies API in Nexios provides a powerful dependency injection system that allows you to manage and inject dependencies into your route handlers. This system helps in creating more maintainable, testable, and modular code.

## Basic Usage

The `Depend` class is used to declare dependencies in route handlers.

```python
from nexios import Depend
from nexios.http import Request, Response

async def get_current_user(request: Request) -> User:
    # Implementation to get current user
    pass

@app.get("/profile")
async def profile(
    request: Request,
    response: Response,
    user: User = Depend(get_current_user)
):
    return response.json({"user": user.dict()})
```

## Dependency Types

### Function Dependencies

The most common type of dependency is a function that returns a value.

```python
async def get_db():
    db = Database()
    await db.connect()
    return db

@app.get("/items")
async def list_items(
    request: Request,
    response: Response,
    db = Depend(get_db)
):
    items = await db.query("SELECT * FROM items")
    return response.json({"items": items})
```

### Class Dependencies

You can also use classes as dependencies.

```python
class Database:
    def __init__(self):
        self.connection = None
        
    async def connect(self):
        self.connection = await create_connection()
        
    async def query(self, query: str):
        return await self.connection.execute(query)

@app.get("/items")
async def list_items(
    request: Request,
    response: Response,
    db: Database = Depend(Database)
):
    items = await db.query("SELECT * FROM items")
    return response.json({"items": items})
```

### Parameter Dependencies

Dependencies can depend on other dependencies.

```python
async def get_db():
    return Database()

async def get_user_service(db = Depend(get_db)):
    return UserService(db)

@app.get("/users")
async def list_users(
    request: Request,
    response: Response,
    user_service = Depend(get_user_service)
):
    users = await user_service.get_all()
    return response.json({"users": users})
```

## Dependency Scopes

### Request Scope

Dependencies can be scoped to the request lifecycle.

```python
async def get_request_id():
    return str(uuid.uuid4())

@app.get("/items")
async def list_items(
    request: Request,
    response: Response,
    request_id: str = Depend(get_request_id)
):
    return response.json({"request_id": request_id})
```

### Application Scope

Dependencies can be shared across requests.

```python
class Config:
    def __init__(self):
        self.settings = load_settings()

config = Config()

@app.get("/settings")
async def get_settings(
    request: Request,
    response: Response,
    settings: Config = Depend(lambda: config)
):
    return response.json({"settings": settings.settings})
```

## Context-Aware Dependency Injection

Nexios provides a powerful, context-aware dependency injection system that allows you to access request-scoped data (and more) anywhere in your dependency tree, even in deeply nested dependencies.

### What is Context?

The `Context` object in Nexios is a special class that carries information about the current request and its environment. It is automatically created for each incoming request and is available throughout the entire dependency resolution process.

By default, the `Context` includes:
- `request`: The current `Request` object
- `user`: The authenticated user (if available)


You can extend the `Context` class to include more fields as needed for your application.

### How to Use Context in Handlers and Dependencies

#### 1. Type Annotation (Classic)
You can declare a `context: Context = None` parameter in your handler or dependency. Nexios will automatically inject the current context:

```python
from nexios.dependencies import Context

@app.get("/context-demo")
async def context_demo(req: Request, res: Response, context: Context = None):
    return {"path": context.request.url.path, "trace_id": context.trace_id}
```

#### 2. Default Value (No Type Annotation Needed)
You can also use `context=Context()` as a parameter. Nexios will recognize this and inject the current context automatically:

```python
@app.get("/auto-context")
async def auto_context_demo(req: Request, res: Response, context=Context()):
    return {"path": context.request.url.path}
```

This works for both handlers and dependencies, and even for deeply nested dependencies:

```python
async def get_user(context=Context()):
    # context is injected automatically
    return {"user": "alice", "path": context.request.url.path}

@app.get("/user-path")
async def user_path(req: Request, res: Response, user=Depend(get_user)):
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

### Advanced: Customizing Context
You can subclass or extend the `Context` class to add more fields or methods relevant to your application:

```python
class MyContext(Context):
    def __init__(self, request=None, user=None, my_custom_field=None, **kwargs):
        super().__init__(request=request, user=user, **kwargs)
        self.my_custom_field = my_custom_field
```

Then, you can configure Nexios to use your custom context class if needed.

### Why Use Context?
- **Consistency:** All dependencies and handlers can access the same request-scoped data.
- **Flexibility:** Add custom fields to the context for your app's needs.
- **No Boilerplate:** No need to manually pass context through every function.
- **Async-Safe:** Works seamlessly with async code and deeply nested dependencies.

### Example: Deeply Nested Context

```python
async def dep_a(context=Context()):
    return f"A: {context.request.url.path}"

async def dep_b(a=Depend(dep_a), context=Context()):
    return f"B: {a}, {context.request.url.path}"

@app.get("/deep-context")
async def deep_context(req: Request, res: Response, b=Depend(dep_b)):
    return {"result": b}
```

In this example, both `dep_a` and `dep_b` receive the same context object, even though they are nested.

## Dependency Validation

### Type Validation

Dependencies can validate their return types.

```python
from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    id: int
    username: str
    email: str

async def get_current_user() -> User:
    # Implementation
    pass

@app.get("/profile")
async def profile(
    request: Request,
    response: Response,
    user: User = Depend(get_current_user)
):
    return response.json({"user": user.dict()})
```

### Error Handling

Dependencies can handle errors gracefully.

```python
async def get_current_user():
    try:
        # Implementation
        return user
    except Exception as e:
        raise HTTPException(401, "Invalid credentials")

@app.get("/profile")
async def profile(
    request: Request,
    response: Response,
    user = Depend(get_current_user)
):
    return response.json({"user": user.dict()})
```

## Advanced Usage

### Caching Dependencies

Dependencies can be cached for better performance.

```python
from functools import lru_cache

@lru_cache()
async def get_cached_data():
    # Expensive operation
    return data

@app.get("/data")
async def get_data(
    request: Request,
    response: Response,
    data = Depend(get_cached_data)
):
    return response.json({"data": data})
```

### Async Dependencies

Dependencies can be asynchronous.

```python
async def get_async_data():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.example.com/data") as response:
            return await response.json()

@app.get("/external-data")
async def get_external_data(
    request: Request,
    response: Response,
    data = Depend(get_async_data)
):
    return response.json({"data": data})
```

### Dependency Overrides

Dependencies can be overridden for testing.

```python
async def get_test_db():
    return TestDatabase()

# In tests
app.dependency_overrides[get_db] = get_test_db
```

### Generator and Async Generator Dependencies

Nexios supports both synchronous and asynchronous generator dependencies for resource management. Use `yield` in your dependency to provide a resource and run cleanup code after the request:

```python
# Synchronous generator dependency
def get_resource():
    resource = acquire()
    try:
        yield resource
    finally:
        release(resource)

# Async generator dependency
async def get_async_resource():
    resource = await acquire_async()
    try:
        yield resource
    finally:
        await release_async(resource)

@app.get("/resource")
async def use_resource(request, response, r=Depend(get_resource)):
    ...

@app.get("/async-resource")
async def use_async_resource(request, response, r=Depend(get_async_resource)):
    ...
```

- Cleanup code in the `finally` block is always executed after the request, even if an exception occurs.
- Both sync and async generator dependencies are supported.

## Best Practices

1. **Keep Dependencies Focused**: Each dependency should have a single responsibility.

2. **Use Type Hints**: Always use type hints for better code clarity and IDE support.

3. **Handle Errors**: Properly handle and propagate errors in dependencies.

4. **Document Dependencies**: Document the purpose and requirements of each dependency.

5. **Test Dependencies**: Write unit tests for your dependencies.

```python
async def test_get_current_user():
    user = await get_current_user()
    assert isinstance(user, User)
    assert user.id is not None
```

6. **Use Dependency Injection**: Use dependency injection to make your code more testable.

```python
class UserService:
    def __init__(self, db: Database):
        self.db = db
        
    async def get_user(self, user_id: int) -> User:
        return await self.db.query(f"SELECT * FROM users WHERE id = {user_id}")

# In route
@app.get("/users/{user_id}")
async def get_user(
    request: Request,
    response: Response,
    user_id: int,
    user_service: UserService = Depend(lambda: UserService(get_db()))
):
    user = await user_service.get_user(user_id)
    return response.json({"user": user.dict()})
```

7. **Use Pydantic Models**: Use Pydantic models for dependency validation.

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

@app.post("/users")
async def create_user(
    request: Request,
    response: Response,
    user_data: UserCreate = Depend(lambda: UserCreate(**request.json()))
):
    user = await create_user_in_db(user_data)
    return response.status(201).json({"user": user.dict()})
``` 

## App-level and Router-level Dependencies

You can apply dependencies to all routes in the app or in a router by passing a `dependencies` argument:

- **App-level**: `NexiosApp(dependencies=[...])` applies to every route in the app.
- **Router-level**: `Router(dependencies=[...])` applies to every route in that router.

### Example: App-level
```python
from nexios import NexiosApp, Depend

def global_dep():
    return "global-value"

app = NexiosApp(dependencies=[Depend(global_dep)])
```

### Example: Router-level
```python
from nexios import Router, Depend

def router_dep():
    return "router-value"

router = Router(prefix="/api", dependencies=[Depend(router_dep)])
```

These dependencies are resolved before any route-specific dependencies. 
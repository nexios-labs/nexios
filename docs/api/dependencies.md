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
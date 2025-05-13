# Dependency Injection in Nexios

Nexios provides a powerful yet intuitive dependency injection system that helps you write clean, maintainable code. Let's explore its capabilities.

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
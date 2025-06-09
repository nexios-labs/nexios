# Documentation Style Guide

This guide provides comprehensive documentation standards and examples for the Nexios framework.

## Writing Style

### General Guidelines

1. Use clear, concise language
2. Write in present tense
3. Use active voice
4. Be consistent with terminology
5. Include practical examples
6. Explain complex concepts simply
7. Use proper formatting
8. Keep documentation up-to-date

### Code Examples

Always include working code examples:

::: code-group
```python [Basic]
from nexios import NexiosApp

app = NexiosApp()

@app.get("/")
async def hello(request, response):
    return response.json({
        "message": "Hello, World!"
    })
```

```python [With Types]
from nexios import NexiosApp
from pydantic import BaseModel
from typing import Optional

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

app = NexiosApp()

@app.post("/items")
async def create_item(request, response):
    item = Item(**await request.json())
    return response.json(item.dict())
```

```python [With Error Handling]
from nexios import NexiosApp
from nexios.exceptions import HTTPException

app = NexiosApp()

@app.get("/items/{item_id:int}")
async def get_item(request, response):
    item_id = request.path_params.item_id
    if item_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Item ID must be positive"
        )
    return response.json({"id": item_id})
```
:::

## Formatting

### Headers

Use proper header hierarchy:

```markdown
# Main Title (H1)
## Section (H2)
### Subsection (H3)
#### Detail (H4)
##### Minor Detail (H5)
###### Very Minor Detail (H6)
```

### Lists

Use appropriate list types:

```markdown
1. First step
2. Second step
3. Third step

- Unordered item
- Another item
  - Nested item
  - Another nested item
- Final item

* Alternative bullet
* Another bullet
```

### Code Blocks

Use language-specific syntax highlighting:

````markdown
```python
from nexios import NexiosApp

app = NexiosApp()
```

```javascript
fetch('/api/items')
  .then(response => response.json())
  .then(data => console.log(data));
```

```bash
pip install nexios
```
````

### Tables

Use tables for structured data:

```markdown
| Method | Path | Description |
|--------|------|-------------|
| GET | /users | List users |
| POST | /users | Create user |
| GET | /users/{id} | Get user |
| PUT | /users/{id} | Update user |
| DELETE | /users/{id} | Delete user |
```

## VitePress Features

### Custom Containers

Use containers for special content:

::: tip Best Practice
Use tip containers for best practices and recommendations.
:::

::: warning Important
Use warning containers for important information that requires attention.
:::

::: danger Critical
Use danger containers for critical warnings or security-related information.
:::

::: details Implementation Details
Use details containers for additional implementation details that can be expanded.
```python
from nexios.security import SecurityMiddleware

app.add_middleware(SecurityMiddleware())
```
:::

### Code Groups

Use code groups for alternative implementations:

::: code-group
```python [Class Based]
from nexios import NexiosApp

class UserAPI:
    def __init__(self, app: NexiosApp):
        self.app = app
        
    @app.get("/users")
    async def list_users(self, request, response):
        return response.json([])
```

```python [Function Based]
from nexios import NexiosApp

app = NexiosApp()

@app.get("/users")
async def list_users(request, response):
    return response.json([])
```
:::

### Links

Use proper linking:

```markdown
[Internal Link](/guide/getting-started)
[External Link](https://example.com)
[API Reference](/api/routing#parameters)
```

## API Documentation

### Endpoint Documentation

Document API endpoints consistently:

```python
@app.post(
    "/users",
    tags=["users"],
    summary="Create user",
    description="Create a new user account",
    responses={
        201: {"description": "User created"},
        400: {"description": "Invalid input"},
        409: {"description": "User exists"}
    }
)
async def create_user(request, response):
    """
    Create a new user.
    
    Request body:
    - username: str
    - email: str
    - password: str
    
    Returns:
    - 201: Created user object
    - 400: Validation error
    - 409: Username taken
    """
    pass
```

### Type Documentation

Document types and models clearly:

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class User(BaseModel):
    """
    User model.
    
    Attributes:
        id (int): Unique user ID
        username (str): Unique username
        email (str): User's email address
        is_active (bool): Account status
        created_at (datetime): Account creation time
    """
    id: int = Field(..., description="Unique user ID")
    username: str = Field(..., description="Unique username")
    email: str = Field(..., description="Email address")
    is_active: bool = Field(True, description="Account status")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
```

## Examples

### Configuration Examples

Show different configuration options:

::: code-group
```python [Basic Config]
from nexios import NexiosApp, MakeConfig

config = MakeConfig(
    debug=True,
    secret_key="your-secret-key"
)

app = NexiosApp(config=config)
```

```python [Production Config]
from nexios import NexiosApp, MakeConfig

config = MakeConfig(
    debug=False,
    secret_key="${SECRET_KEY}",
    allowed_hosts=["api.example.com"],
    database_url="${DATABASE_URL}",
    cors_enabled=True,
    cors_origins=["https://example.com"],
    rate_limit=100,
    rate_limit_window=60
)

app = NexiosApp(config=config)
```

```python [Development Config]
from nexios import NexiosApp, MakeConfig

config = MakeConfig(
    debug=True,
    reload=True,
    database_url="sqlite:///dev.db",
    cors_enabled=True,
    cors_origins=["*"],
    logging_level="DEBUG"
)

app = NexiosApp(config=config)
```
:::

### Error Handling Examples

Show error handling patterns:

::: code-group
```python [Basic Errors]
from nexios.exceptions import HTTPException

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return response.json({
        "error": exc.detail
    }, status_code=exc.status_code)
```

```python [Custom Errors]
class APIError(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        code: str = None
    ):
        super().__init__(status_code, detail)
        self.code = code

@app.exception_handler(APIError)
async def api_error_handler(request, exc):
    return response.json({
        "error": exc.detail,
        "code": exc.code
    }, status_code=exc.status_code)
```

```python [Database Errors]
from sqlalchemy.exc import IntegrityError

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc):
    return response.json({
        "error": "Database error",
        "detail": str(exc.orig)
    }, status_code=409)
```
:::

## Best Practices

### Documentation Structure

Organize documentation logically:

1. Introduction
   - Overview
   - Quick start
   - Installation
2. Core Concepts
   - Basic usage
   - Configuration
   - Architecture
3. Guides
   - Tutorials
   - How-to guides
   - Examples
4. API Reference
   - Endpoints
   - Models
   - Utilities
5. Advanced Topics
   - Best practices
   - Performance
   - Security
6. Troubleshooting
   - Common issues
   - FAQ
   - Support

### Code Examples

Follow these guidelines for code examples:

1. Keep examples focused
2. Include imports
3. Use meaningful names
4. Add comments
5. Show error handling
6. Include type hints
7. Follow PEP 8
8. Test examples
9. Update regularly
10. Show best practices

### Versioning

Document version-specific features:

::: warning Version Compatibility
This feature requires Nexios 2.0 or later.
:::

```python
# Nexios 1.x
app.add_middleware(AuthMiddleware())

# Nexios 2.x
app.add_middleware(
    AuthenticationMiddleware(
        backend=JWTAuthBackend()
    )
)
```

## Common Patterns

### Authentication Examples

Show authentication patterns:

::: code-group
```python [JWT Auth]
from nexios.auth import JWTAuth

auth = JWTAuth(secret_key="your-secret-key")

@app.post("/login")
async def login(request, response):
    data = await request.json()
    user = await authenticate_user(
        data["username"],
        data["password"]
    )
    token = auth.create_token({"sub": user.id})
    return response.json({"token": token})
```

```python [Session Auth]
from nexios.auth import SessionAuth

auth = SessionAuth(secret_key="your-secret-key")

@app.post("/login")
async def login(request, response):
    data = await request.json()
    user = await authenticate_user(
        data["username"],
        data["password"]
    )
    request.session["user_id"] = user.id
    return response.json({"message": "Logged in"})
```
:::

### Database Examples

Show database patterns:

::: code-group
```python [SQLAlchemy]
from nexios.db import Database
from sqlalchemy import select

db = Database("postgresql://user:pass@localhost/db")

@app.get("/users")
async def list_users(request, response):
    async with db.session() as session:
        result = await session.execute(
            select(User).order_by(User.id)
        )
        users = result.scalars().all()
        return response.json(users)
```

```python [MongoDB]
from nexios.db import MongoDB

db = MongoDB("mongodb://localhost")

@app.get("/users")
async def list_users(request, response):
    users = await db.users.find().to_list(100)
    return response.json(users)
```
:::

## More Information

- [VitePress Guide](https://vitepress.dev/)
- [Markdown Guide](https://www.markdownguide.org/)
- [API Documentation Best Practices](https://swagger.io/resources/articles/best-practices-in-api-documentation/)

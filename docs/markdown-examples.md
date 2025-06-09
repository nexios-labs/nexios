# Documentation Style Guide

This guide demonstrates how to write documentation for Nexios using VitePress's markdown extensions.

## Code Examples

### Syntax Highlighting

VitePress provides syntax highlighting with line numbers, line highlighting, and focus:

::: code-group
```python{4-6} [Basic Route]
from nexios import NexiosApp

app = NexiosApp()
@app.get("/")
async def index(request, response):
    return response.json({"message": "Hello World"})

if __name__ == "__main__":
    app.run()
```

```python{3,7} [With Middleware]
from nexios import NexiosApp
from nexios.middleware import CORSMiddleware
app = NexiosApp(
    title="My API",
    version="1.0.0"
)
app.add_middleware(CORSMiddleware())
```

```python{3-5} [With Config]
from nexios import NexiosApp, Config

config = Config(
    debug=True,
    cors_enabled=True
)
app = NexiosApp(config=config)
```
:::

### Multi-language Examples

::: code-group
```python [Python]
@app.get("/users/{id}")
async def get_user(request, response):
    user_id = request.path_params.id
    return response.json({"id": user_id})
```

```javascript [JavaScript]
// Client-side fetch
async function getUser(id) {
  const response = await fetch(`/users/${id}`);
  return response.json();
}
```

```typescript [TypeScript]
// Type-safe client
interface User {
  id: number;
  name: string;
}

async function getUser(id: number): Promise<User> {
  const response = await fetch(`/users/${id}`);
  return response.json();
}
```
:::

## Documentation Components

### Warning Boxes

Use warning boxes to highlight important information:

::: warning Version Requirements
Nexios requires Python 3.9 or higher for async features.
:::

::: danger Security Notice
Never expose debug mode in production environments.
:::

::: tip Performance
Use connection pooling for database connections in production.
:::

::: info Note
All Nexios routes are async by default.
:::

### Details Blocks

Use details blocks for additional information:

::: details Advanced Configuration
```python
app = NexiosApp(
    config=Config(
        debug=False,
        cors_enabled=True,
        allowed_hosts=["api.example.com"],
        max_upload_size=10_000_000,
        rate_limit={
            "max_requests": 100,
            "timeframe": 60
        }
    )
)
```
:::

::: details Database Setup
```python
from nexios.db import Database
from sqlalchemy.ext.asyncio import create_async_engine

# Create engine with connection pooling
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    pool_size=20,
    max_overflow=30
)

# Initialize database
db = Database(engine)

# Register with app
app.state.db = db
```
:::

### Tables

Use tables for comparing options:

| Feature | Basic | Pro | Enterprise |
|---------|-------|-----|------------|
| Routes | ✓ | ✓ | ✓ |
| WebSockets | ✓ | ✓ | ✓ |
| Rate Limiting | | ✓ | ✓ |
| Load Balancing | | | ✓ |
| Priority Support | | | ✓ |

### Diagrams

Use Mermaid diagrams for visualizations:

```mermaid
sequenceDiagram
    Client->>+Server: HTTP Request
    Server->>+Middleware: Process Request
    Middleware->>+Route Handler: Handle Request
    Route Handler->>+Database: Query Data
    Database-->>-Route Handler: Return Data
    Route Handler-->>-Middleware: Return Response
    Middleware-->>-Server: Process Response
    Server-->>-Client: HTTP Response
```

### API Documentation

Document API endpoints clearly:

#### `GET /users/{id}`

**Parameters:**
- `id` (integer, required): The user ID

**Response:**
```json
{
  "id": 123,
  "username": "john_doe",
  "email": "john@example.com"
}
```

**Example:**
```python
@app.get("/users/{id:int}")
async def get_user(request, response):
    """Get user by ID.
    
    Args:
        request: The request object
        response: The response object
        
    Returns:
        JSON response with user data
        
    Raises:
        HTTPException: If user not found
    """
    user_id = request.path_params.id
    user = await db.fetch_one(
        "SELECT * FROM users WHERE id = :id",
        {"id": user_id}
    )
    if not user:
        raise HTTPException(404, "User not found")
    return response.json(dict(user))
```

## Best Practices

1. Always include type hints
2. Document exceptions and error cases
3. Provide working examples
4. Use clear and consistent naming
5. Include performance considerations
6. Document security implications

::: tip Writing Style
- Use active voice
- Be concise but complete
- Include practical examples
- Highlight important warnings
- Link to related topics
:::

## More Resources

- [API Reference](/api/)
- [Examples](/examples/)
- [Tutorials](/tutorials/)
- [Contributing Guide](/contributing/)

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

### Why Use Dependency Injection?

In traditional application development, components often create and manage their dependencies directly. This tight coupling makes code harder to test, maintain, and refactor. With dependency injection:

1. **Separation of Concerns**: Each component focuses on its core functionality while dependencies are provided externally
2. **Testability**: Dependencies can be easily mocked or replaced during testing
3. **Reusability**: Dependencies can be shared across multiple components
4. **Flexibility**: Implementation details can be changed without modifying dependent components

## How Dependency Injection Works in Nexios

The Nexios DI system automatically resolves and injects dependencies into your route handlers. Here's a visual representation of how it works:

```
┌─────────────────────┐
│ Dependency Provider │
│  (Function/Class)   │
└─────────┬───────────┘
          │
          │ provides
          │
          ▼
┌─────────────────────┐     injects    ┌─────────────────────┐
│  Depend(provider)   │────────────────▶  Route Handler      │
└─────────────────────┘                └─────────────────────┘
```

When a request is received, Nexios:
1. Identifies dependencies in the route handler signature
2. Resolves each dependency by calling its provider function
3. Passes resolved dependencies as arguments to the route handler
4. Handles the request with all dependencies properly injected

## Core Components

### The Depend Class

The `Depend` class is the main building block of Nexios' dependency injection system. It declares dependencies that should be injected into your route handlers.

```python
from nexios import Depend, get_application

app = get_application()

async def get_current_user():
    # Extract token from request header
  
    return User

@app.get("/profile")
async def profile(request, response, current_user=Depend(get_current_user)):
    if not current_user:
        response.status_code = 401
        return {"error": "Authentication required"}
    return {"user": current_user}
```

In this example:
- `get_current_user` is a dependency provider function
- `Depend(get_current_user)` creates a dependency instance
- When `/profile` is accessed, Nexios automatically calls `get_current_user` and injects the result

### The inject_dependencies Decorator

Under the hood, the `inject_dependencies` decorator manages the injection of dependencies into your route handlers. While you typically don't need to use this decorator directly (as it's automatically applied to route handlers), understanding how it works can be helpful:

```python
from nexios import inject_dependencies, Depend

def some_provider():
    return "dependency value"

@inject_dependencies
async def my_handler(request, response, dependency=Depend(some_provider)):
    # The dependency will be automatically injected
    print(dependency)  # Outputs: "dependency value"
    return {"result": dependency}
```

## Basic Usage Examples

### Synchronous Dependencies

Here's a simple example demonstrating dependency injection with synchronous dependencies:

```python
from nexios import get_application, Depend

app = get_application()

def get_settings():
    """Provider function that returns application settings"""
    return {
        "api_version": "1.0",
        "environment": "production",
        "debug": False,
        "allowed_origins": ["https://example.com"]
    }

@app.get("/api/info")
async def api_info(request, response, settings=Depend(get_settings)):
    """Route handler that uses the settings dependency"""
    return {
        "status": "online",
        "version": settings["api_version"],
        "environment": settings["environment"]
    }
```

### Asynchronous Dependencies

Nexios seamlessly handles both synchronous and asynchronous dependencies:

```python
import asyncio
from nexios import get_application, Depend

app = get_application()

async def get_db_connection():
    """Async provider function that establishes a database connection"""
    # Simulating async database connection with a delay
    await asyncio.sleep(0.1)
    
    # In a real app, you'd use a real database connection library
    class DBConnection:
        async def query(self, sql):
            # Simulate a query execution
            await asyncio.sleep(0.05)
            if sql == "SELECT * FROM users":
                return [
                    {"id": 1, "name": "John Doe"},
                    {"id": 2, "name": "Jane Smith"}
                ]
            return []
    
    return DBConnection()

@app.get("/users")
async def list_users(
    request, 
    response, 
    db=Depend(get_db_connection)
):
    """Route handler that uses the database connection dependency"""
    users = await db.query("SELECT * FROM users")
    return {"users": users}
```

### Dependencies with Parameters

You can customize dependency behavior by passing parameters to provider functions:

```python
from nexios import get_application, Depend, HTTPException

app = get_application()

def require_permission(permission_name: str):
    """Factory function that creates a permission-checking dependency provider"""
    async def check_permission(request):
        # Get the user role from request (from a header, token, etc.)
        user_role = request.headers.get("X-Role", "guest")
        
        # Simple permission system (in real apps, use a proper permission system)
        role_permissions = {
            "admin": ["read", "write", "delete"],
            "editor": ["read", "write"],
            "user": ["read"],
            "guest": []
        }
        
        # Check if the role has the required permission
        if permission_name in role_permissions.get(user_role, []):
            return True
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied: {permission_name} required"
        )
    
    return check_permission

@app.get("/documents")
async def list_documents(
    request, 
    response, 
    can_read=Depend(require_permission("read"))
):
    """Route that requires read permission"""
    # If we get here, the user has read permission
    return {"documents": ["doc1.pdf", "doc2.pdf"]}

@app.post("/documents")
async def create_document(
    request, 
    response, 
    can_write=Depend(require_permission("write"))
):
    """Route that requires write permission"""
    # If we get here, the user has write permission
    return {"status": "Document created"}
```

## Dependency Chaining and Nesting

Nexios supports dependency chains where one dependency depends on another:

```python
from nexios import get_application, Depend, HTTPException

app = get_application()

async def get_db():
    """Database connection provider"""
    # In a real app, create an actual database connection
    return {"connection": "database_connection"}

async def get_current_user(request, db=Depend(get_db)):
    """User provider that depends on the database connection"""
    auth_token = request.headers.get("Authorization")
    if not auth_token:
        return None
    
    # In a real app, you would verify the token and query the database
    if auth_token == "valid-token":
        # Simulate user retrieval using the db dependency
        return {"id": 1, "username": "johndoe", "role": "admin"}
    return None

async def get_current_active_user(current_user=Depend(get_current_user)):
    """Ensures the user is authenticated"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return current_user

@app.get("/me")
async def read_users_me(
    request, 
    response, 
    current_user=Depend(get_current_active_user)
):
    """Route that requires an authenticated user"""
    return current_user
```

In this example:
1. `get_current_user` depends on `get_db`
2. `get_current_active_user` depends on `get_current_user`
3. The route handler depends on `get_current_active_user`

Nexios automatically resolves this chain of dependencies.

## Real-World Examples

### Authentication System

Here's a complete JWT authentication system using Nexios dependency injection:

```python
import jwt
from datetime import datetime, timedelta
from nexios import get_application, Depend, HTTPException
from nexios.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = get_application()

# Configuration
JWT_SECRET = "your-secret-key"  # In production, use a secure secret
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = 30  # minutes

# Simulated user database
USERS_DB = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "john@example.com",
        "hashed_password": "fakehashedsecret",  # In production, use proper password hashing
        "disabled": False,
    }
}

# OAuth2 token handling
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    # In production, use a proper password verification function
    return plain_password + "notreallyhashed" == hashed_password

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return user_dict
    return None

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_

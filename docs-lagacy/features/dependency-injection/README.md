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
* Automatically resolve nested dependency chains
* Handle parameter binding with intelligent resolution
* Integrate seamlessly with testing frameworks

### Why Use Dependency Injection?

In traditional application development, components often create and manage their dependencies directly. This tight coupling makes code harder to test, maintain, and refactor. With dependency injection:

1. **Separation of Concerns**: Each component focuses on its core functionality while dependencies are provided externally
2. **Testability**: Dependencies can be easily mocked or replaced during testing
3. **Reusability**: Dependencies can be shared across multiple components
4. **Flexibility**: Implementation details can be changed without modifying dependent components

## How Dependency Injection Works in Nexios

The Nexios DI system automatically resolves and injects dependencies into your route handlers, supporting both direct and nested dependency patterns. Here's a visual representation of how it works:

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
2. Analyzes each dependency's requirements, including nested dependencies
3. Resolves the dependency tree by calling provider functions in the correct order
4. Automatically handles both synchronous and asynchronous dependencies
5. Passes resolved dependencies as arguments to the route handler
6. Handles the request with all dependencies properly injected

> **Note:** This is a simplified workflow. In advanced scenarios, Nexios also handles parameter binding, dependency scope management, and optimized resolution paths for nested dependencies. These features are covered in detail in later sections.

## Core Components

### The Depend Class

The `Depend` class is the main building block of Nexios' dependency injection system. It serves as a marker for dependencies that should be injected into your route handlers.

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

Under the hood, the `Depend` class has a simple yet powerful implementation:

```python
class Depend:
    def __init__(self, dependency: Optional[Callable[..., Any]] = None):
        self.dependency = dependency
```

The `Depend` class:
1. Takes an optional callable as its constructor parameter
2. Stores this callable as the dependency provider
3. Acts as a marker in parameter default values for the dependency injection system
4. Contains no complex logic itself, delegating the resolution process to the `inject_dependencies` decorator

### The inject_dependencies Decorator

Under the hood, the `inject_dependencies` decorator manages the injection of dependencies into your route handlers. While you typically don't need to use this decorator directly (as it's automatically applied to route handlers), understanding how it works provides valuable insights into Nexios' dependency resolution mechanism:

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

The `inject_dependencies` decorator:

1. **Analyzes function parameters**: Uses Python's introspection to identify parameters with `Depend` instances as default values
2. **Handles parameter binding**: Preserves explicitly provided arguments while injecting dependencies for missing ones
3. **Resolves dependencies in order**: Processes each parameter in sequence, handling nested dependencies as needed
4. **Supports both sync and async providers**: Automatically awaits async dependencies and directly calls sync dependencies
5. **Provides error handling**: Raises meaningful errors when dependencies cannot be resolved
6. **Preserves function metadata**: Maintains the original function's signature, docstring, and other attributes

Here's a simplified explanation of how the decorator works internally:

1. It examines each parameter of the decorated function
2. For parameters with a `Depend` default value, it:
   - Retrieves the provider function from the `Depend` instance
   - Determines the provider's parameter requirements
   - Resolves any nested dependencies
   - Calls the provider function with resolved dependencies
   - Injects the result into the decorated function's arguments
3. For parameters that were explicitly provided, it uses the provided values
4. Finally, it calls the original function with all parameters resolved

If a dependency provider is missing, the system raises a clear error message indicating which parameter could not be resolved.

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
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depend(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(USERS_DB, username=username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: dict = Depend(get_current_user)):
    if current_user.get("disabled"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depend()):
    user = authenticate_user(USERS_DB, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_data = {"sub": user["username"]}
    access_token = create_access_token(data=token_data)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: dict = Depend(get_current_active_user)):
    return current_user
```

## Advanced Features

Nexios' dependency injection system includes several advanced features that enable powerful, flexible, and maintainable application architectures. This section explores these features in depth to help you leverage the full capabilities of the DI system.

### Nested Dependencies

One of the most powerful features of Nexios' dependency injection system is its ability to automatically resolve nested dependencies - dependencies that themselves have dependencies.

#### How Dependency Chains Are Resolved

When a route handler requires a dependency that itself depends on other dependencies, Nexios builds and resolves the entire dependency tree:

```python
from nexios import get_application, Depend

app = get_application()

# Root dependency
async def get_config():
    return {
        "database_url": "postgresql://user:password@localhost/db",
        "api_keys": {"service1": "key1", "service2": "key2"}
    }

# Level 1 dependency (depends on config)
async def get_db_connection(config=Depend(get_config)):
    # Use config to establish a database connection
    connection_string = config["database_url"]
    # In a real app, you'd connect to the actual database here
    return {"connection": f"Connected to {connection_string}"}

# Level 2 dependency (depends on db_connection)
async def get_user_repository(db=Depend(get_db_connection)):
    # A repository that uses the database connection
    return {
        "find_by_id": lambda user_id: {"id": user_id, "name": "Test User"},
        "db": db
    }

# Route handler (depends on user_repository)
@app.get("/users/{user_id}")
async def get_user(
    user_id: str,
    request,
    response,
    user_repo=Depend(get_user_repository)
):
    user = user_repo["find_by_id"](user_id)
    return user
```

In this example, when a request to `/users/123` is processed:

1. Nexios detects that the route handler depends on `user_repo`
2. It identifies that `get_user_repository` (which provides `user_repo`) depends on `db`
3. It discovers that `get_db_connection` (which provides `db`) depends on `config`
4. It calls `get_config()` first to resolve the root dependency
5. With the config available, it calls `get_db_connection(config=...)` to resolve the database connection
6. With the database connection available, it calls `get_user_repository(db=...)` to resolve the repository
7. Finally, it calls the route handler with all dependencies resolved

This hierarchical resolution ensures that dependencies are satisfied in the correct order, regardless of how deeply nested they are.

#### Handling Mixed Sync/Async Dependencies

Nexios intelligently handles both synchronous and asynchronous dependencies in the same dependency tree:

```python
from nexios import get_application, Depend

app = get_application()

# Synchronous dependency
def get_settings():
    return {"timeout": 30, "retry_count": 3}

# Asynchronous dependency that depends on a sync dependency
async def get_http_client(settings=Depend(get_settings)):
    # In a real app, configure and return an actual HTTP client
    return {
        "timeout": settings["timeout"],
        "async_get": lambda url: f"Response from {url}"
    }

# Synchronous dependency that depends on an async dependency
def get_service_api(http_client=Depend(get_http_client)):
    # The system automatically awaits the async dependencies
    # before passing them to synchronous dependencies
    return {
        "client": http_client,
        "get_data": lambda: http_client["async_get"]("/api/data")
    }

@app.get("/external-data")
async def fetch_external_data(
    request,
    response,
    service=Depend(get_service_api)
):
    data = await service["get_data"]()
    return {"data": data}
```

The dependency injection system:

1. Automatically detects whether a dependency provider is a coroutine function (async)
2. Awaits async dependencies before passing their results to other dependencies
3. Properly handles chains that mix sync and async providers
4. Ensures that the entire dependency tree is resolved correctly, regardless of the sync/async mix

#### Best Practices for Complex Dependency Trees

When working with complex dependency trees, consider these best practices:

1. **Keep the dependency tree as shallow as possible**
   - Flatter trees are easier to understand and maintain
   - Aim for a maximum depth of 3-4 levels when practical

2. **Design dependencies with single responsibility**
   - Each dependency should do one thing well
   - Avoid creating "god" dependencies that provide too many services

3. **Consider using a dependency container for complex applications**
   - For very large applications, organize dependencies by feature or module
   - Use composition to manage dependencies within each module

4. **Avoid circular dependencies**
   - Circular dependencies (A depends on B, B depends on C, C depends on A) will cause errors
   - Refactor your design to break circular dependencies when they occur

5. **Document dependencies thoroughly**
   - Comment each dependency provider to explain what it provides and requires
   - Create a dependency graph for complex applications to visualize relationships

6. **Use factory patterns for configurable dependencies**
   - Factory functions allow for more flexible dependency configuration
   - They help reduce the need for deeply nested dependencies

### Parameter Resolution

Nexios employs an intelligent parameter resolution system to determine how dependencies should be injected into functions.

#### Parameter Detection and Binding

The DI system analyzes function signatures to identify parameters that should be injected:

```python
from nexios import get_application, Depend

app = get_application()

async def get_user_agent(request):
    """Extracts and returns the User-Agent header"""
    return request.headers.get("User-Agent", "Unknown")

@app.get("/browser")
async def browser_info(
    request,          # Regular parameter, provided by the framework
    response,         # Regular parameter, provided by the framework
    user_agent=Depend(get_user_agent),  # Dependency parameter
    query_param=None  # Optional regular parameter
):
    """Shows browser information based on User-Agent"""
    return {
        "user_agent": user_agent,
        "query_param": query_param
    }
```

When this route is called, Nexios:

1. Recognizes `request` and `response` as regular parameters and provides them directly
2. Identifies `user_agent` as a dependency parameter because its default value is a `Depend` instance
3. Notices that `query_param` is a regular parameter with a default value of `None`
4. Resolves the `user_agent` dependency by calling the `get_user_agent` function, passing the `request` parameter
5. Leaves `query_param` as `None` since no value was provided (or uses a provided value if one exists)

This selective parameter binding ensures that dependencies are only injected where needed, while preserving regular parameter behavior.

#### Priority Rules for Parameter Resolution

When resolving parameters, Nexios follows these priority rules:

1. **Explicitly provided arguments always take precedence**
   - If a value is explicitly passed for a parameter, it's used regardless of any dependency annotation

2. **Path parameters, query parameters, and body parameters are bound next**
   - These are handled by the routing system before dependency injection

3. **Dependencies are resolved for parameters with `Depend` instances as default values**
   - This happens after the basic parameter binding

4. **Regular default values are used for any remaining parameters**
   - These are the default values specified in the function signature

This priority system ensures intuitive behavior in all scenarios.

#### Optional vs Required Dependencies

Dependencies can be either required or optional:

```python
from typing import Optional
from nexios import get_application, Depend, HTTPException

app = get_application()

async def get_admin_token(request):
    """Get the admin token from headers, error if missing"""
    token = request.headers.get("X-Admin-Token")
    if not token:
        raise HTTPException(status_code=401, detail="Admin token required")
    return token

async def get_analytics_token(request):
    """Get the analytics token from headers, return None if missing"""
    return request.headers.get("X-Analytics-Token")

@app.get("/admin/dashboard")
async def admin_dashboard(
    request,
    response,
    admin_token=Depend(get_admin_token),           # Required dependency
    analytics_token=Depend(get_analytics_token)    # Optional dependency
):
    """Admin dashboard endpoint (requires admin token)"""
    data = {"admin": True}
    
    # Only add analytics if token was provided
    if analytics_token:
        data["analytics_enabled"] = True
    
    return data
```

In this example:

1. `get_admin_token` is a required dependency - it raises an exception if the token is missing
2. `get_analytics_token` is an optional dependency - it returns `None` if the token is missing

By controlling how the dependency provider handles missing values, you can create both required and optional dependencies without changing the injection mechanism itself.

#### Error Handling in Complex Scenarios

Nexios provides helpful error messages when dependency resolution fails:

```python
from nexios import get_application, Depend

app = get_application()

# Missing dependency provider
@app.get("/broken")
async def broken_route(
    request,
    response,
    missing_dependency=Depend(None)  # Will cause an error
):
    return {"status": "This will never work"}
```

When this route is accessed, Nexios raises a clear error:

```
ValueError: Dependency for parameter 'missing_dependency' has no provider
```

This helps quickly identify and fix dependency configuration issues.

For more controlled error handling, you can use exception handling within dependency providers:

```python
from nexios import get_application, Depend, HTTPException

app = get_application()

async def get_database():
    try:
        # Attempt to connect to the database
        # If it fails, provide a helpful error message
        raise ConnectionError("Database connection failed")
    except ConnectionError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@app.get("/data")
async def get_data(
    request,
    response,
    db=Depend(get_database)
):
    # This will only execute if the database connection succeeds
    return {"data": "Some data from database"}
```

This pattern allows for graceful error handling throughout your dependency tree.

## Testing with Dependencies

One of the major benefits of dependency injection is improved testability. Nexios' DI system is designed to make testing straightforward, allowing you to easily mock dependencies and test components in isolation.

### Unit Testing

Unit testing focuses on testing individual components in isolation. With dependency injection, you can easily replace real dependencies with mocks or stubs.

#### Mocking Dependencies

Here's how to unit test a route handler by mocking its dependencies:

```python
import pytest
from nexios import get_application, Depend
from nexios.testing import TestClient

# The dependency we'll mock
async def get_user_service():
    # In a real app, this might connect to a database
    # and provide methods to interact with user data
    return {
        "get_user": lambda user_id: {"id": user_id, "name": f"User {user_id}"},
        "is_admin": lambda user_id: user_id == "admin"
    }

# Create the app with a route that uses the dependency
app = get_application()

@app.get("/users/{user_id}")
async def get_user(user_id: str, request, response, user_service=Depend(get_user_service)):
    user = user_service["get_user"](user_id)
    is_admin = user_service["is_admin"](user_id)
    return {**user, "is_admin": is_admin}

# Now, let's write a test that mocks the dependency
@pytest.fixture
def test_client():
    # Create a TestClient instance
    client = TestClient(app)
    return client

@pytest.fixture
def mock_user_service():
    # Create a mock version of the user service
    return {
        "get_user": lambda user_id: {"id": user_id, "name": "Test User"},
        "is_admin": lambda user_id: True  # Make everyone an admin in tests
    }

def test_get_user(test_client, monkeypatch, mock_user_service):
    # Monkeypatch the dependency to return our mock
    monkeypatch.setattr("__main__.get_user_service", lambda: mock_user_service)
    
    # Make the request
    response = test_client.get("/users/123")
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "123"
    assert data["name"] == "Test User"
    assert data["is_admin"] == True
```

This test replaces the real `get_user_service` dependency with a mock that returns predetermined values, allowing us to test the route handler's behavior in isolation.

#### Testing Async Dependencies

When testing async dependencies, you need to ensure your mocks also handle asynchronous behavior properly:

```python
import pytest
from nexios import get_application, Depend
from nexios.testing import TestClient

# Async dependency
async def get_database():
    # In a real app, this would be an async database client
    class AsyncDB:
        async def get_items(self):
            return [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
    
    return AsyncDB()

app = get_application()

@app.get("/items")
async def list_items(request, response, db=Depend(get_database)):
    items = await db.get_items()
    return {"items": items}

# Test with async mock
@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_async_db():
    class MockAsyncDB:
        async def get_items(self):
            return [{"id": 999, "name": "Test Item"}]
    
    return MockAsyncDB()

async def mock_get_database():
    # This is an async function that returns our mock
    return mock_async_db()

def test_list_items(test_client, monkeypatch, mock_async_db):
    # Replace the real dependency with our async mock
    monkeypatch.setattr("__main__.get_database", mock_get_database)
    
    # Test the endpoint
    response = test_client.get("/items")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == 999
    assert data["items"][0]["name"] == "Test Item"
```

Notice that our mock dependency is also an async function that returns an object with async methods, mirroring the structure of the real dependency.

### Integration Testing

While unit testing focuses on testing components in isolation, integration testing examines how components work together. For dependency injection, this often means testing with real dependencies or testing entire dependency chains.

#### Testing Dependency Chains

Here's how to test a dependency chain:

```python
import pytest
from nexios import get_application, Depend
from nexios.testing import TestClient

# Create a dependency chain
def get_config():
    return {"api_key": "test_key", "base_url": "https://api.example.com"}

async def get_api_client(config=Depend(get_config)):
    class APIClient:
        def __init__(self, api_key, base_url):
            self.api_key = api_key
            self.base_url = base_url
        
        async def get_data(self):
            # In real app, would make HTTP request
            return {"status": "success", "data": ["item1", "item2"]}
    
    return APIClient(config["api_key"], config["base_url"])

app = get_application()

@app.get("/api-data")
async def get_api_data(request, response, client=Depend(get_api_client)):
    data = await client.get_data()
    return data

# Test with custom config but real dependency chain
@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def test_config():
    return {"api_key": "integration_test_key", "base_url": "https://test.example.com"}

def test_api_data_integration(test_client, monkeypatch, test_config):
    # Only override the config, but use the real API client dependency
    monkeypatch.setattr("__main__.get_config", lambda: test_config)
    
    response = test_client.get("/api-data")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
```

This integration test replaces only the top-level config dependency but allows the rest of the dependency chain to function normally, testing how the components work together.

#### Real-World Testing Scenarios

For more complex applications, you may want to use a mix of real and mocked dependencies:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from nexios import get_application, Depend
from nexios.testing import TestClient

# Create an app with complex dependencies
app = get_application()

async def get_db():
    # Normally connects to real database
    return "real_db_connection"

async def get_cache():
    # Normally connects to Redis or similar
    return "real_cache_connection"

async def get_user_repository(db=Depend(get_db), cache=Depend(get_cache)):
    # A repository that uses both DB and cache
    return {"db": db, "cache": cache}

@app.get("/users")
async def list_users(
    request, 
    response, 
    repo=Depend(get_user_repository)
):
    # In real app, would query database
    return {"users": []}

# Complex test setup
def test_with_mixed_dependencies(monkeypatch):
    # Create mocks
    mock_db = MagicMock()
    mock_db.query = AsyncMock(return_value=[{"id": 1, "name": "User 1"}])
    
    # Use real cache but mock DB
    async def mock_get_db():
        return mock_db
    
    monkeypatch.setattr("__main__.get_db", mock_get_db)
    
    # Create test client
    client = TestClient(app)
    
    # Test the endpoint
    response = client.get("/users")
    
    # Verify the response and that the mock was used
    assert response.status_code == 200
    mock_db.query.assert_called_once()
```

This approach lets you use real dependencies where appropriate while mocking complex or external services.

### Performance Testing Considerations

When testing applications with dependency injection, it's important to consider performance:

1. **Measure Dependency Resolution Time**

```python
import time
from nexios import get_application, Depend

app = get_application()

# Create a complex dependency tree
def get_service_1():
    return "service1"

def get_service_2(s1=Depend(get_service_1)):
    return f"{s1}_service2"

def get_service_3(s2=Depend(get_service_2)):
    return f"{s2}_service3"

@app.get("/performance-test")
async def perf_test(
    request, 
    response, 
    s3=Depend(get_service_3)
):
    return {"result": s3}

# Test function
def test_dependency_resolution_performance():
    from nexios.testing import TestClient
    
    client = TestClient(app)
    
    # Warm-up call
    client.get("/performance-test")
    
    # Performance measurement
    start_time = time.time()
    num_requests = 100
    
    for _ in range(num_requests):
        client.get("/performance-test")
    
    duration = time.time() - start_time
    avg_time = duration / num_requests
    
    print(f"Average request time: {avg_time:.6f} seconds")
    
    # Establish some baseline for acceptable performance
    assert avg_time < 0.01, "Dependency resolution is too slow"
```

2. **Test with Realistic Dependency Trees**

- Don't only test with simple dependencies; include the full depth of your actual application
- Test with both sync and async dependencies to ensure performance is acceptable in both cases
- Profile memory usage to detect any leaks in long-running applications

3. **Consider Resource Initialization**

- When testing performance, account for one-time initialization of resources
- For accurate measurements, separate dependency resolution time from resource initialization time

4. **Load Testing with Dependencies**

```python
import asyncio
import time
from nexios import get_application, Depend
from nexios.testing import TestClient

app = get_application()

async def get_expensive_resource():
    await asyncio.sleep(0.01)  # Simulate resource acquisition
    return "expensive_resource"

@app.get("/api")
async def api_endpoint(
    request, 
    response, 
    resource=Depend(get_expensive_resource)
):
    return {"resource": resource}

async def test_concurrent_load():
    client = TestClient(app)
    
    async def make_request():
        response = client.get("/api")
        return response.status_code
    
    # Create many concurrent requests
    start_time = time.time()
    tasks = [make_request() for _ in range(100)]
    results = await asyncio.gather(*tasks)
    duration = time.time() - start_time
    
    # Check results
    assert all(result == 200 for result in results)
    print(f"Completed 100 concurrent requests in {duration:.2f} seconds")
```

By considering these performance testing strategies, you can ensure that your dependency injection system performs well under real-world conditions.

## Best Practices and Patterns

Building on the practices covered in the Advanced Features section, here are additional best practices and patterns for effective dependency injection:

### Organizing Dependencies by Domain

For larger applications, consider organizing dependencies by domain or feature:

```python
# Authentication-related dependencies
async def get_auth_service():
    return AuthService()

async def get_permission_checker(auth_service=Depend(get_auth_service)):
    return PermissionChecker(auth_service)

# Database-related dependencies
async def get_database_pool():
    return DatabasePool()

async def get_user_repository(db_pool=Depend(get_database_pool)):
    return UserRepository(db_pool)

# API client dependencies
async def get_http_client():
    return HTTPClient()

async def get_external_api(http_client=Depend(get_http_client)):
    return ExternalAPI(http_client)
```

This organization makes dependencies easier to locate, understand, and maintain as your application grows.

### Dependency Lifetime Management

Consider the lifetime of your dependencies carefully:

```python
# Singleton dependency (created once and reused)
_config_instance = None

def get_config():
    global _config_instance
    if _config_instance is None:
        _config_instance = load_config()
    return _config_instance

# Per-request dependency (created for each request)
async def get_request_id(request):
    return request.headers.get("X-Request-ID", str(uuid.uuid4()))
```

Choose the appropriate lifetime based on:
- Resource consumption
- Thread safety
- State isolation requirements

### Encapsulating Complex Initialization

Use dependency providers to encapsulate complex initialization logic:

```python
async def get_database():
    # Complex initialization with connection pooling, retry logic, etc.
    connection_params = get_connection_params()
    pool = await create_connection_pool(
        min_connections=5,
        max_connections=20,
        **connection_params
    )
    
    # Setup event handlers
    pool.on_connection_lost(handle_connection_lost)
    
    # Return the fully configured pool
    return pool
```

This approach keeps your route handlers clean while encapsulating initialization complexity in the dependency providers.

## Common Use Cases

Let's explore some common use cases for dependency injection in Nexios applications:

### Multi-Tenant Applications

For applications serving multiple tenants or organizations:

```python
from nexios import get_application, Depend, HTTPException

app = get_application()

async def get_tenant_id(request):
    """Extract the tenant ID from request headers or JWT token"""
    # In a real application, you might extract this from a JWT token
    tenant_id = request.headers.get("X-Tenant-ID")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID required")
    return tenant_id

async def get_tenant_db(tenant_id=Depend(get_tenant_id)):
    """Get a database connection for a specific tenant"""
    # In a real application, this might use separate database instances or schemas
    connection_string = f"postgresql://user:pass@localhost/{tenant_id}_db"
    return {"connection": connection_string, "tenant_id": tenant_id}

@app.get("/tenant/items")
async def list_tenant_items(
    request,
    response,
    db=Depend(get_tenant_db)
):
    """List items for the current tenant"""
    # In a real application, this would query the tenant's database
    return {
        "tenant_id": db["tenant_id"],
        "items": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
    }
```

### Feature Flags and Configuration

For managing feature flags and configuration:

```python
from nexios import get_application, Depend

app = get_application()

def get_feature_flags():
    """Retrieve application feature flags"""
    # In a real application, this might load from a database or remote config service
    return {
        "enable_new_ui": True,
        "enable_beta_features": False,
        "max_items_per_page": 100
    }

@app.get("/products")
async def list_products(
    request,
    response,
    feature_flags=Depend(get_feature_flags)
):
    """List products with conditional features based on feature flags"""
    products = [{"id": 1, "name": "Product 1"}, {"id": 2, "name": "Product 2"}]
    
    # Apply feature flag conditional logic
    if feature_flags["enable_beta_features"]:
        # Add beta features to the response
        for product in products:
            product["beta_info"] = {"rating": 4.5, "reviews": 10}
    
    return {
        "products": products,
        "ui_version": "new" if feature_flags["enable_new_ui"] else "classic"
    }
```

### Authentication and Authorization Services

For comprehensive auth services:

```python
from nexios import get_application, Depend, HTTPException

app = get_application()

# Auth service dependencies
async def get_auth_provider():
    """Provides authentication methods"""
    return {
        "verify_token": lambda token: {"user_id": "123", "role": "admin"} if token == "valid-token" else None,
        "create_token": lambda user_id: f"token-for-{user_id}"
    }

async def get_permission_service(auth_provider=Depend(get_auth_provider)):
    """Provides permissions checking"""
    role_permissions = {
        "admin": ["read", "write", "delete"],
        "editor": ["read", "write"],
        "viewer": ["read"]
    }
    
    def check_permission(user_role, permission):
        return permission in role_permissions.get(user_role, [])
    
    return {
        "check_permission": check_permission
    }

async def get_current_user(
    request,
    auth_provider=Depend(get_auth_provider)
):
    """Get the current authenticated user"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = auth_provider["verify_token"](token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

async def require_permission(
    permission_name: str,
    current_user=Depend(get_current_user),
    permission_service=Depend(get_permission_service)
):
    """Factory for creating permission-based dependencies"""
    if not permission_service["check_permission"](current_user["role"], permission_name):
        raise HTTPException(status_code=403, detail=f"Permission denied: {permission_name} required")
    return True

@app.delete("/items/{item_id}")
async def delete_item(
    item_id: str,
    request,
    response,
    current_user=Depend(get_current_user),
    can_delete=Depend(lambda: require_permission("delete"))
):
    """Delete an item (requires delete permission)"""
    return {"message": f"Item {item_id} deleted by user {current_user['user_id']}"}
```

## Performance Considerations

When using dependency injection at scale, keep these performance considerations in mind:

### Caching Expensive Dependencies

Cache dependencies that are expensive to create:

```python
import functools
from nexios import get_application, Depend

app = get_application()

# Cache the expensive operation with functools.lru_cache
@functools.lru_cache(maxsize=1)
def get_expensive_settings():
    # Simulate an expensive operation (e.g., loading a large configuration file)
    print("Loading expensive settings (this should happen only once)")
    return {"setting1": "value1", "setting2": "value2"}

@app.get("/api/settings")
async def get_settings(
    request,
    response,
    settings=Depend(get_expensive_settings)
):
    return settings
```

### Lazy Initialization

For dependencies that aren't always needed, consider lazy initialization:

```python
from nexios import get_application, Depend

app = get_application()

class LazyServiceClient:
    def __init__(self, config):
        self.config = config
        self._client = None
    
    @property
    def client(self):
        # Initialize the client only when accessed
        if self._client is None:
            print("Initializing service client (lazy)")
            self._client = {"connection": f"Connected to {self.config['service_url']}"}
        return self._client

def get_config():
    return {"service_url": "https://api.example.com"}

def get_service_client(config=Depend(get_config)):
    return LazyServiceClient(config)

@app.get("/service/status")
async def get_service_status(
    request,
    response,
    service=Depend(get_service_client)
):
    # The client is only initialized here when actually accessed
    client = service.client
    return {"status": "connected", "service": client["connection"]}
```

### Optimize Dependency Chains

For frequently used routes, optimize dependency chains:

```python
from nexios import get_application, Depend

app = get_application()

# Separate low-level dependencies
def get_config():
    return {"db_url": "postgresql://localhost/db"}

def get_redis_config():
    return {"redis_url": "redis://localhost:6379"}

async def get_db(config=Depend(get_config)):
    return {"connection": f"DB connected to {config['db_url']}"}

async def get_redis(redis_config=Depend(get_redis_config)):
    return {"connection": f"Redis connected to {redis_config['redis_url']}"}

# For high-traffic routes, combine dependencies to reduce resolution overhead
async def get_services():
    """Pre-combined services for high-traffic routes"""
    config = get_config()
    redis_config = get_redis_config()
    
    db = {"connection": f"DB connected to {config['db_url']}"}
    redis = {"connection": f"Redis connected to {redis_config['redis_url']}"}
    
    return {
        "db": db,
        "redis": redis
    }

# High-traffic route uses the optimized dependency
@app.get("/dashboard")
async def dashboard(
    request,
    response,
    services=Depend(get_services)
):
    """High-traffic dashboard route"""
    return {
        "db_status": services["db"]["connection"],
        "cache_status": services["redis"]["connection"]
    }

# Less frequent route uses individual dependencies
@app.get("/admin/db-status")
async def db_status(
    request,
    response,
    db=Depend(get_db)
):
    """Less frequent admin route"""
    return {"db_status": db["connection"]}

## Integration with Other Features

Nexios' dependency injection system integrates seamlessly with other framework features, allowing for powerful combinations.

### Working with Middleware

You can use middleware with dependencies to create powerful request processing pipelines:

```python
from nexios import get_application, Depend

app = get_application()

# Dependency provider
async def get_logger():
    class Logger:
        def log(self, message):
            print(f"LOG: {message}")
    return Logger()

# Middleware that uses a dependency
async def logging_middleware(request, response, next, logger=Depend(get_logger)):
    logger.log(f"Request received: {request.method} {request.url.path}")
    result = await next()
    logger.log(f"Response sent: {response.status_code}")
    return result

# Add the middleware
app.use(logging_middleware)

@app.get("/hello")
async def hello(request, response):
    return {"message": "Hello, world!"}
```

This example demonstrates how dependencies can be used in middleware, not just route handlers.

### WebSocket Integration

Dependencies can also be used with WebSocket handlers:

```python
from nexios import get_application, Depend
from nexios.websockets import WebSocket

app = get_application()

async def get_user_store():
    """Provides a simple user store for WebSocket connections"""
    return {"active_users": {}}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    user_id: str,
    user_store=Depend(get_user_store)
):
    await websocket.accept()
    
    # Store the connection
    user_store["active_users"][user_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except Exception:
        # Clean up on disconnect
        if user_id in user_store["active_users"]:
            del user_store["active_users"][user_id]
```

### Event System Integration

Dependencies work well with Nexios' event system:

```python
from nexios import get_application, Depend

app = get_application()

async def get_database_pool():
    """Create a database connection pool"""
    return {"connection": "pool"}

@app.on_startup
async def initialize_database(db_pool=Depend(get_database_pool)):
    """Initialize the database on startup"""
    print(f"Database initialized: {db_pool}")

@app.on_shutdown
async def cleanup_database(db_pool=Depend(get_database_pool)):
    """Clean up database resources on shutdown"""
    print(f"Database resources cleaned up: {db_pool}")
```

By leveraging these integration points, you can create applications that use dependency injection consistently throughout all aspects of your application.

# Authentication in Nexios

**🔒 Secure your API with just one line of code!**

Nexios makes authentication simple yet powerful. Here's all you need to get started:

```python
from nexios import Nexios, Request
from nexios.auth.decorators import auth

app = NexiosApp()

# Public route - accessible to everyone
@app.get("/public")
async def public_data():
    return {"message": "Hello, world! 👋"}

# Protected route - requires authentication
@app.get("/profile")
@auth()  # That's it! Your route is now protected
async def user_profile(request: Request):
    return {
        "message": f"Welcome back, {request.user.display_name}!",
        "user_id": request.user.identity,
        "is_authenticated": True
    }

# Admin-only route - requires JWT authentication
@app.get("/admin/dashboard")
@auth(["jwt"])  # Only JWT-authenticated users can access
async def admin_dashboard(request: Request):
    return {
        "message": "🔑 Admin access granted",
        "admin_features": ["user_management", "analytics", "settings"]
    }

# Protected API endpoint with role-based access
@app.get("/api/secure-data")
@auth(["jwt", "api-key"])  # Multiple auth methods supported
async def secure_data(request: Request):
    return {"data": "🔒 Ultra-secure data!"}
```

### 🔥 Key Features at a Glance

- **One-line protection**: Just add `@auth()` to secure any route
- **Multiple auth methods**: JWT, Session, API Key, or bring your own
- **Role-based access control**: Easily implement user permissions
- **Built-in security**: Protection against common web vulnerabilities
- **Flexible & extensible**: Customize to fit any use case

## Table of Contents

## Authentication Middleware

The `AuthenticationMiddleware` is the core component that handles authentication for incoming requests. It processes each request, extracts authentication credentials, and attaches user information to the request object.

### Basic Configuration

```python
from nexios.auth.middleware import AuthenticationMiddleware
from nexios.auth.backends.jwt import JWTAuthBackend

# Configure JWT backend
jwt_backend = JWTAuthBackend(
    secret_key="your-secret-key",
    algorithm="HS256",
    authenticate_func=load_user_from_jwt
)

# Add to middleware
app.add_middleware(AuthenticationMiddleware(backend=jwt_backend))
```

**Explanation:**

1. The `AuthenticationMiddleware` is initialized with a backend (in this case, `JWTAuthBackend`)
2. The middleware processes each incoming request before it reaches your route handlers
3. It extracts authentication credentials from the request (e.g., JWT token from headers)
4. The credentials are passed to the backend's `authenticate` method
5. If authentication succeeds, the user object is attached to `request.user`
6. If authentication fails, `request.user` is set to an `UnauthenticatedUser` instance

## Built-in User Classes

Nexios provides several built-in user classes that you can use or extend for your authentication needs.

### BaseUser

The abstract base class that defines the interface all user objects must implement.

```python
from nexios.auth.base import BaseUser

class CustomUser(BaseUser):
    @property
    def is_authenticated(self) -> bool:
        return True  # Implement authentication check

    @property
    def display_name(self) -> str:
        return "User Display Name"  # Implement display name

    @property
    def identity(self) -> str:
        return "user123"  # Implement unique identifier
```

**Key Methods:**

- `is_authenticated`: Returns `True` if the user is authenticated
- `display_name`: Returns a human-readable name for the user
- `identity`: Returns a unique identifier for the user

### SimpleUser

A concrete implementation of `BaseUser` for basic authentication needs.

```python
from nexios.auth.base import SimpleUser

# Create an authenticated user
user = SimpleUser(username="john_doe")
print(user.is_authenticated)  # True
print(user.display_name)     # "john_doe"
print(user.identity)         # "john_doe"
```

**Features:**

- Simple constructor that takes just a username
- Implements all required `BaseUser` methods
- `identity` defaults to the username
- `is_authenticated` is always `True`

### UnauthenticatedUser

Represents an unauthenticated user (returned when authentication fails).

```python
from nexios.auth.base import UnauthenticatedUser

user = UnauthenticatedUser()
print(user.is_authenticated)  # False
print(user.display_name)     # ""
print(user.identity)         # ""
```

**When to use:**

- As a default value for `request.user`
- When authentication fails
- For anonymous users

## Authentication Backends

### JWT Backend

Handles JSON Web Token authentication.

```python
from nexios.auth.backends.jwt import JWTAuthBackend
import jwt

async def load_user_from_jwt(payload: dict) -> SimpleUser:
    """Load user from JWT payload"""
    user_id = payload.get("sub")
    # Load user from database or other storage
    user_data = await db.users.find_one({"id": user_id})
    if user_data:
        return SimpleUser(username=user_data["username"])
    return None

jwt_backend = JWTAuthBackend(
    secret_key="your-secret-key",
    algorithm="HS256",
    authenticate_func=load_user_from_jwt,
    user_key="sub"  # JWT claim containing user ID
)
```

**Key Parameters:**

- `secret_key`: For verifying token signatures
- `algorithm`: Hashing algorithm (e.g., "HS256", "RS256")
- `authenticate_func`: Function that loads user from JWT payload
- `user_key`: JWT claim containing user identifier

### Session Backend

Handles session-based authentication.

```python
from nexios.auth.backends.session import SessionAuthBackend

async def load_user_from_session(session_data: dict) -> SimpleUser:
    """Load user from session data"""
    if "user" in session_data:
        return SimpleUser(username=session_data["user"]["username"])
    return None

session_backend = SessionAuthBackend(
    authenticate_func=load_user_from_session,
    user_key="user"  # Key in session where user data is stored
)
```

**Key Parameters:**

- `authenticate_func`: Function that loads user from session data
- `user_key`: Session key containing user data

## Protecting Routes with @auth Decorator

The `@auth` decorator controls access to route handlers based on authentication status and scopes.

### Basic Usage

```python
from nexios.auth.decorators import auth

# Require any authenticated user
@app.get("/protected")
@auth(["jwt"])
async def protected_route(request: Request):
    return {"message": f"Hello, {request.user.display_name}!"}

# Require specific scopes
@app.get("/admin")
@auth(["jwt"])
async def admin_route(request: Request):
    return {"message": "Admin access granted"}
```

## Using Multiple Authentication Backends

Nexios supports multiple authentication backends, which are tried in order until one succeeds.

```python
# First try JWT auth
app.add_middleware(
    AuthenticationMiddleware,
    backend=JWTAuthBackend(
        secret_key="jwt-secret",
        authenticate_func=load_user_from_jwt
    )
)

# Fall back to session auth
app.add_middleware(
    AuthenticationMiddleware,
    backend=SessionAuthBackend(
        authenticate_func=load_user_from_session
    )
)
```

**Key Points:**

1. Backends are tried in the order they are specified
2. The first backend that returns a user wins
3. If no backend authenticates the user, `request.user` is an `UnauthenticatedUser`
4. The authentication method is stored in `request.scope["auth"]`

## Practical Examples

### Custom User Class with Additional Methods

```python
from nexios.auth.base import BaseUser

class AdminUser(BaseUser):
    def __init__(self, username: str, roles: list):
        self.username = username
        self.roles = set(roles)

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username

    @property
    def identity(self) -> str:
        return self.username

    def has_role(self, role: str) -> bool:
        return role in self.roles

# Usage
admin = AdminUser("admin", ["admin", "superuser"])
print(admin.has_role("admin"))  # True
print(admin.has_role("user"))   # False
```

### Combining Multiple Authentication Methods

```python
# In your authentication setup
def setup_authentication(app):
    # JWT for API clients
    jwt_backend = JWTAuthBackend(
        secret_key=os.getenv("JWT_SECRET"),
        authenticate_func=load_user_from_jwt
    )

    # Session for browser-based auth
    session_backend = SessionAuthBackend(
        authenticate_func=load_user_from_session
    )

    # API key for service-to-service
    api_key_backend = APIKeyBackend(
        authenticate_func=load_user_from_api_key
    )

    # Add middleware with all backends
    app.add_middleware(
        AuthenticationMiddleware,
        backends=[jwt_backend, session_backend, api_key_backend]
    )

# In your route handlers
@app.get("/api/data")
async def get_data(request: Request):
    auth_method = request.scope.get("auth")  # "jwt", "session", or "apikey"
    return {"data": "sensitive data", "auth_method": auth_method}
```

## Custom Authentication Backends

You can create custom authentication backends by extending the `AuthenticationBackend` class. This is useful when you need to implement custom authentication logic that isn't covered by the built-in backends.

### Creating a Custom Backend

```python
from nexios.auth.base import AuthenticationBackend, BaseUser, UnauthenticatedUser

class CustomUser(BaseUser):
    def __init__(self, user_id: str, username: str, roles: list = None):
        self.user_id = user_id
        self.username = username
        self.roles = roles or []

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username

    @property
    def identity(self) -> str:
        return self.user_id

class CustomAuthBackend(AuthenticationBackend):
    def __init__(self, authenticate_func):
        self.authenticate_func = authenticate_func

    async def authenticate(self, request: Request, response: Response) -> Any:
        # Extract credentials from the request
        auth_header = request.headers.get("X-Custom-Auth")

        if not auth_header:
            return None

        # Use the provided function to validate credentials
        user_data = await self.authenticate_func(auth_header)

        if not user_data:
            return None

        # Return a tuple of (user, auth_type)
        # The auth_type is what you'll use in @auth decorator
        return CustomUser(
            user_id=user_data["id"],
            username=user_data["username"],
            roles=user_data.get("roles", [])
        ), "custom"  # "custom" is the auth type used in @auth
```

### Using the Custom Backend

```python
# Define how to authenticate the custom token
async def validate_custom_token(token: str):
    # Validate the token and return user data
    if token == "valid-token":
        return {
            "id": "user123",
            "username": "custom_user",
            "roles": ["admin", "user"]
        }
    return None

# Create and configure the backend
custom_backend = CustomAuthBackend(authenticate_func=validate_custom_token)

# Add to middleware
app.add_middleware(AuthenticationMiddleware(backend=custom_backend))

# Or add with other backends
app.add_middleware(
    AuthenticationMiddleware,
    backends=[jwt_backend, session_backend, custom_backend]
)
```

## Protecting Routes with @auth Decorator

The `@auth` decorator is used to protect routes by requiring specific authentication types. The authentication type corresponds to the second value returned by the backend's `authenticate` method.

### Basic Usage

```python
from nexios.auth.decorators import auth

# Require any authenticated user (any auth type)
@app.get("/protected")
@auth()
async def protected_route(request: Request):
    return {"message": f"Hello, {request.user.display_name}!"}

# Require specific authentication type (e.g., "jwt" or "custom")
@app.get("/custom-only")
@auth(["custom"])
async def custom_auth_only(request: Request):
    return {"message": "This route requires custom authentication"}

# Require multiple possible authentication types
@app.get("/api/data")
@auth(["jwt", "custom"])
async def api_data(request: Request):
    return {"data": "sensitive data"}
```

### How @auth Works with Backend Types

1. When a backend's `authenticate` method returns a user, it should also return an auth type (e.g., `"jwt"`, `"session"`, `"custom"`).
2. The `@auth` decorator checks if the request was authenticated with one of the specified auth types.
3. If no auth types are specified, any authenticated user is allowed.
4. If the auth type doesn't match, a 403 Forbidden response is returned.

### Example with Custom Backend

```python
# Custom backend returns (user, "custom") on successful authentication
class CustomAuthBackend(AuthenticationBackend):
    async def authenticate(self, request: Request, response: Response) -> Any:
        # ... authentication logic ...
        return user, "custom"  # This is the auth type

# Route that requires the custom auth type
@app.get("/custom-secure")
@auth(["custom"])
async def custom_secure_route(request: Request):
    # This route will only be accessible if authenticated via CustomAuthBackend
    return {"message": "Access granted to custom auth only"}
```

### Checking Authentication in Route Handlers

You can also check authentication status and type directly in your route handlers:

```python
@app.get("/check-auth")
async def check_auth(request: Request):
    if not request.user.is_authenticated:
        return {"status": "unauthenticated"}

    # Get the authentication type (e.g., "jwt", "session", "custom")
    auth_type = request.scope.get("auth")

    return {
        "status": "authenticated",
        "user": request.user.identity,
        "auth_type": auth_type,
        "is_admin": hasattr(request.user, "roles") and "admin" in request.user.roles
    }
```

## Complete Example: Custom API Key Authentication

Here's a complete example of implementing API key authentication:

```python
from nexios.auth.base import AuthenticationBackend, BaseUser

class APIKeyUser(BaseUser):
    def __init__(self, api_key: str, permissions: list):
        self.api_key = api_key
        self.permissions = permissions

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return f"API-User-{self.api_key[-6:]}"

    @property
    def identity(self) -> str:
        return self.api_key

class APIKeyBackend(AuthenticationBackend):
    def __init__(self, authenticate_func):
        self.authenticate_func = authenticate_func

    async def authenticate(self, request: Request, response: Response) -> Any:
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return None

        # Validate API key and get permissions
        permissions = await self.authenticate_func(api_key)
        if not permissions:
            return None

        return APIKeyUser(api_key, permissions), "api-key"

# Usage
async def validate_api_key(key: str):
    # In a real app, check against database
    if key == "test-key-123":
        return ["read:data", "write:data"]
    return None

api_key_backend = APIKeyBackend(authenticate_func=validate_api_key)

# Add to middleware
app.add_middleware(AuthenticationMiddleware(backend=api_key_backend))

# Protect routes with API key
@app.get("/api/data")
@auth(["api-key"])
async def get_data(request: Request, response: Response):
    return {"data": "sensitive data"}

# Or require specific permissions
@app.post("/api/data")
@auth(["api-key"])
async def post_data(request: Request, response: Response):
    if "write:data" not in request.user.permissions:
        return {"error": "Insufficient permissions"}, 403

    # Process data
    return {"status": "success"}
```

This documentation provides a comprehensive guide to implementing custom authentication backends and using the `@auth` decorator in Nexios. The examples show how to create custom user models, implement authentication logic, and protect routes based on authentication types and permissions.

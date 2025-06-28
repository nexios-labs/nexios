# Authentication

Authentication is a critical component of most web applications, enabling you to identify users, protect resources, and provide personalized experiences. Nexios provides a flexible, robust authentication system that's easy to implement and customize for your specific needs.

## Authentication Fundamentals

Authentication in Nexios provides several key benefits:

- **Multiple Backends**: Session, JWT, API Key, and custom backends
- **Middleware Integration**: Automatic user attachment to requests
- **Flexible User Models**: Support for any user data structure
- **Security Best Practices**: Built-in protection against common attacks
- **Easy Testing**: Simple mocking and testing utilities
- **Production Ready**: Scalable and secure for production use

## Security Best Practices

When implementing authentication in your Nexios application, follow these security best practices:

1. **Use HTTPS**: Always use HTTPS in production to protect credentials
2. **Secure Session Storage**: Use secure, encrypted session storage
3. **JWT Security**: Use strong secrets and appropriate expiration times
4. **API Key Rotation**: Implement key rotation for long-lived tokens
5. **Rate Limiting**: Protect authentication endpoints from brute force attacks
6. **Input Validation**: Validate all authentication inputs
7. **Error Messages**: Don't reveal sensitive information in error messages
8. **Logging**: Log authentication events for security monitoring

## Authentication Flow

The typical authentication flow in Nexios follows these steps:

1. **User submits credentials** (login form, API key, etc.)
2. **Backend validates credentials** against user database
3. **Authentication token created** (session, JWT, etc.)
4. **Token stored/sent to client** (cookie, header, etc.)
5. **Subsequent requests include token** automatically
6. **Middleware validates token** and attaches user to request
7. **Handler accesses user** via `request.user`

## Core Components

The Nexios authentication system is built around three core components:

- **`Authentication Middleware`**: Processes incoming requests, extracts credentials, and attaches user information to the request
- **`Authentication Backends`**: Validate credentials and retrieve user information
- **`User Objects`**: Represent authenticated and unauthenticated users with consistent interfaces

## Basic Authentication Setup

To get started with authentication in Nexios, you need to set up an authentication backend and add the authentication middleware:

```python
from nexios import NexiosApp
from nexios.auth.middleware import AuthenticationMiddleware
from nexios.auth.backends.session import SessionAuthBackend

app = NexiosApp()

async def get_user_by_id(user_id: int):
    # Load user by ID from your database
    user = await db.get_user(user_id)
    if user:
        return UserModel(
            id=user.id,
            username=user.username,
            email=user.email
        )
    return None

# Create authentication backend
auth_backend = SessionAuthBackend(authenticate_func=get_user_by_id)

# Add authentication middleware
app.add_middleware(AuthenticationMiddleware(backend=auth_backend))
```

Once configured, the authentication system will process each request, attempt to authenticate the user, and make the user object available via `request.user`:

```python
@app.get("/profile")
async def profile(request, response):
    if request.user.is_authenticated:
        return response.json({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email
        })
    else:
        return response.redirect("/login")

@app.get("/admin")
async def admin_panel(request, response):
    if not request.user.is_authenticated:
        return response.json({"error": "Authentication required"}, status_code=401)
    
    if not request.user.is_admin:
        return response.json({"error": "Admin access required"}, status_code=403)
    
    return response.json({"message": "Welcome to admin panel"})
```

## Authentication Middleware

The `AuthenticationMiddleware` is responsible for processing each request, delegating to the configured backend for authentication, and attaching the resulting user object to the request:

```python
from nexios.auth.middleware import AuthenticationMiddleware
from nexios.auth.backends.apikey import APIKeyBackend

# Create the authentication backend
api_key_backend = APIKeyBackend(
    key_name="X-API-Key",
    authenticate_func=get_user_by_api_key
)

# Add authentication middleware with the backend
app.add_middleware(AuthenticationMiddleware(backend=api_key_backend))
```

### Middleware Process Flow

The authentication middleware follows this process for each request:

1. **Request Arrival**: When a request arrives, the middleware intercepts it
2. **Backend Authentication**: The middleware calls the authentication backend's `authenticate` method
3. **User Resolution**: If authentication succeeds, a user object is returned along with an authentication type
4. **Request Attachment**: The user is attached to `request.scope["user"]` and accessible via `request.user`
5. **Auth Type Attachment**: An authentication type string is also attached to `request.scope["auth"]`
6. **Fallback**: If authentication fails, an `UnauthenticatedUser` instance is attached instead

### Multiple Authentication Backends

You can configure multiple authentication backends for different scenarios:

```python
from nexios.auth.middleware import AuthenticationMiddleware
from nexios.auth.backends.session import SessionAuthBackend
from nexios.auth.backends.jwt import JWTAuthBackend

# Create multiple backends
session_backend = SessionAuthBackend(authenticate_func=get_user_by_id)
jwt_backend = JWTAuthBackend(
    secret_key="your-secret-key",
    authenticate_func=get_user_by_id
)

# Add middleware with multiple backends
app.add_middleware(AuthenticationMiddleware(backends=[session_backend, jwt_backend]))
```

## Authentication Backends

Nexios includes several built-in authentication backends and allows you to create custom backends for specific needs.

### Built-in Authentication Backends

#### 1. Session Authentication Backend

Session authentication uses server-side sessions to maintain user state:

```python
from nexios.auth.backends.session import SessionAuthBackend

async def get_user_by_id(user_id: int):
    # Load user from database
    user = await db.get_user(user_id)
    if user:
        return UserModel(
            id=user.id,
            username=user.username,
            email=user.email,
            is_admin=user.is_admin
        )
    return None

session_backend = SessionAuthBackend(
    user_key="user_id",  # Session key for user ID
    authenticate_func=get_user_by_id  # Function to load user by ID
)

app.add_middleware(AuthenticationMiddleware(backend=session_backend))
```

**Session Backend Features:**
- Checks for a user ID stored in the session (typically set during login)
- Loads the full user object using the provided loader function
- Returns an authenticated user if found, or an unauthenticated user otherwise
- Works with any session storage backend (database, Redis, etc.)

**Login Handler Example:**
```python
@app.post("/login")
async def login(request, response):
    data = await request.json
    username = data.get("username")
    password = data.get("password")
    
    # Validate credentials
    user = await validate_credentials(username, password)
    if not user:
        return response.json({"error": "Invalid credentials"}, status_code=401)
    
    # Store user ID in session
    request.session["user_id"] = user.id
    
    return response.json({"message": "Login successful"})

@app.post("/logout")
async def logout(request, response):
    # Clear session
    request.session.clear()
    return response.json({"message": "Logout successful"})
```

#### 2. JWT Authentication Backend

JWT (JSON Web Token) authentication uses stateless tokens:

```python
from nexios.auth.backends.jwt import JWTAuthBackend
import jwt

async def get_user_by_id(user_id: int):
    # Load user from database
    user = await db.get_user(user_id)
    if user:
        return UserModel(
            id=user.id,
            username=user.username,
            email=user.email
        )
    return None

jwt_backend = JWTAuthBackend(
    secret_key="your-super-secret-jwt-key",
    algorithm="HS256",  # Optional, default is HS256
    token_prefix="Bearer",  # Optional, default is "Bearer"
    authenticate_func=get_user_by_id,  # Function to load user by ID
    auth_header_name="Authorization"  # Optional, default is "Authorization"
)

app.add_middleware(AuthenticationMiddleware(backend=jwt_backend))
```

**JWT Backend Features:**
- Extracts a JWT token from the Authorization header
- Validates the token signature, expiration, etc.
- Extracts the user ID from the token claims
- Loads the full user object using the provided loader function
- Supports custom claims and validation

**JWT Login Handler Example:**
```python
import jwt
from datetime import datetime, timedelta

@app.post("/login")
async def login(request, response):
    data = await request.json
    username = data.get("username")
    password = data.get("password")
    
    # Validate credentials
    user = await validate_credentials(username, password)
    if not user:
        return response.json({"error": "Invalid credentials"}, status_code=401)
    
    # Create JWT token
    payload = {
        "user_id": user.id,
        "username": user.username,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, "your-super-secret-jwt-key", algorithm="HS256")
    
    return response.json({
        "message": "Login successful",
        "token": token,
        "expires_in": 86400  # 24 hours in seconds
    })

@app.post("/refresh")
async def refresh_token(request, response):
    if not request.user.is_authenticated:
        return response.json({"error": "Authentication required"}, status_code=401)
    
    # Create new token
    payload = {
        "user_id": request.user.id,
        "username": request.user.username,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, "your-super-secret-jwt-key", algorithm="HS256")
    
    return response.json({
        "token": token,
        "expires_in": 86400
    })
```

#### 3. API Key Authentication Backend

API key authentication is commonly used for service-to-service communication:

```python
from nexios.auth.backends.apikey import APIKeyBackend

async def get_user_by_api_key(api_key: str):
    # Lookup user with the given API key
    user = await db.find_user_by_api_key(api_key)
    if user:
        return UserModel(
            id=user.id,
            username=user.username,
            api_key=api_key,
            permissions=user.permissions
        )
    return None

api_key_backend = APIKeyBackend(
    key_name="X-API-Key",  # Header containing the API key
    authenticate_func=get_user_by_api_key  # Function to load user by API key
)

app.add_middleware(AuthenticationMiddleware(backend=api_key_backend))
```

**API Key Backend Features:**
- Extracts an API key from the specified header
- Loads the full user object using the provided loader function
- Returns an authenticated user if found, or an unauthenticated user otherwise
- Ideal for service-to-service authentication

**API Key Management Example:**
```python
@app.post("/api-keys")
async def create_api_key(request, response):
    if not request.user.is_authenticated:
        return response.json({"error": "Authentication required"}, status_code=401)
    
    # Generate API key
    api_key = generate_secure_api_key()
    
    # Store API key in database
    await db.store_api_key(request.user.id, api_key)
    
    return response.json({
        "api_key": api_key,
        "created_at": datetime.utcnow().isoformat()
    })

@app.delete("/api-keys/{key_id}")
async def revoke_api_key(request, response):
    if not request.user.is_authenticated:
        return response.json({"error": "Authentication required"}, status_code=401)
    
    key_id = request.path_params.key_id
    
    # Revoke API key
    await db.revoke_api_key(request.user.id, key_id)
    
    return response.json({"message": "API key revoked"})
```

## Creating a Custom Authentication Backend

You can create custom authentication backends by implementing the `AuthenticationBackend` abstract base class:

```python
from nexios.auth.base import AuthenticationBackend, BaseUser, UnauthenticatedUser

class CustomUser(BaseUser):
    def __init__(self, id, username, is_admin=False):
        self.id = id
        self.username = username
        self.is_admin = is_admin

    @property
    def is_authenticated(self):
        return True

    def get_display_name(self):
        return self.username

class CustomAuthBackend(AuthenticationBackend):
    async def authenticate(self, request, response):
        # Extract credentials from the request
        custom_header = request.headers.get("X-Custom-Auth")
        
        if not custom_header:
            return UnauthenticatedUser()
        
        # Validate custom authentication logic
        user = await self.validate_custom_auth(custom_header)
        
        if user:
            return user, "custom"
        
        return UnauthenticatedUser()
    
    async def validate_custom_auth(self, auth_header):
        # Implement your custom authentication logic
        # This could involve checking against a database, external service, etc.
        if auth_header == "valid-token":
            return CustomUser(id=1, username="custom_user", is_admin=True)
        return None

# Use the custom backend
custom_backend = CustomAuthBackend()
app.add_middleware(AuthenticationMiddleware(backend=custom_backend))
```

## User Models

Nexios provides flexible user models that you can extend for your specific needs:

### Base User Classes

```python
from nexios.auth.base import BaseUser, UnauthenticatedUser

class AuthenticatedUser(BaseUser):
    def __init__(self, id, username, email, permissions=None):
        self.id = id
        self.username = username
        self.email = email
        self.permissions = permissions or []

    @property
    def is_authenticated(self):
        return True

    def get_display_name(self):
        return self.username

    def has_permission(self, permission):
        return permission in self.permissions

class UnauthenticatedUser(BaseUser):
    @property
    def is_authenticated(self):
        return False

    def get_display_name(self):
        return "Anonymous"
```

### Custom User Model Example

```python
class User(BaseUser):
    def __init__(self, id, username, email, role, is_active=True):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self.is_active = is_active

    @property
    def is_authenticated(self):
        return self.is_active

    def get_display_name(self):
        return self.username

    def is_admin(self):
        return self.role == "admin"

    def is_moderator(self):
        return self.role in ["admin", "moderator"]

    def can_access_feature(self, feature):
        feature_permissions = {
            "admin_panel": ["admin"],
            "user_management": ["admin", "moderator"],
            "content_creation": ["admin", "moderator", "user"]
        }
        return self.role in feature_permissions.get(feature, [])
```

## Authentication Decorators

Nexios provides decorators to simplify authentication checks:

```python
from nexios.auth.decorator import login_required, permission_required

@app.get("/profile")
@login_required
async def profile(request, response):
    # User is guaranteed to be authenticated here
    return response.json({
        "id": request.user.id,
        "username": request.user.username,
        "email": request.user.email
    })

@app.get("/admin")
@permission_required("admin")
async def admin_panel(request, response):
    # User is guaranteed to have admin permission
    return response.json({"message": "Welcome to admin panel"})

@app.get("/moderate")
@permission_required(["admin", "moderator"])
async def moderation_panel(request, response):
    # User is guaranteed to have admin or moderator permission
    return response.json({"message": "Welcome to moderation panel"})
```

## Error Handling

### Authentication Exceptions

```python
from nexios.auth.exceptions import AuthenticationFailed, PermissionDenied

@app.get("/protected")
async def protected_route(request, response):
    if not request.user.is_authenticated:
        raise AuthenticationFailed("Authentication required")
    
    if not request.user.is_admin():
        raise PermissionDenied("Admin access required")
    
    return response.json({"message": "Access granted"})
```

### Custom Error Handlers

```python
@app.add_exception_handler(AuthenticationFailed)
async def handle_auth_failed(request, response, exc):
    return response.json({
        "error": "Authentication failed",
        "message": str(exc)
    }, status_code=401)

@app.add_exception_handler(PermissionDenied)
async def handle_permission_denied(request, response, exc):
    return response.json({
        "error": "Permission denied",
        "message": str(exc)
    }, status_code=403)
```

## Testing Authentication

### Mocking Authentication

```python
import pytest
from nexios.testing import TestClient
from nexios.auth.base import BaseUser

class MockUser(BaseUser):
    def __init__(self, id=1, username="test_user", is_admin=False):
        self.id = id
        self.username = username
        self.is_admin = is_admin

    @property
    def is_authenticated(self):
        return True

@pytest.fixture
def authenticated_client():
    client = TestClient(app)
    
    # Mock authenticated user
    client.app.scope["user"] = MockUser(id=1, username="test_user")
    client.app.scope["auth"] = "session"
    
    return client

def test_protected_route(authenticated_client):
    response = authenticated_client.get("/profile")
    assert response.status_code == 200
    assert response.json()["username"] == "test_user"

def test_admin_route(authenticated_client):
    # Mock admin user
    authenticated_client.app.scope["user"] = MockUser(
        id=1, username="admin", is_admin=True
    )
    
    response = authenticated_client.get("/admin")
    assert response.status_code == 200
```

### Integration Testing

```python
async def test_login_flow(client):
    # Test login
    login_data = {"username": "test_user", "password": "password123"}
    response = await client.post("/login", json=login_data)
    assert response.status_code == 200
    
    # Test accessing protected route
    response = await client.get("/profile")
    assert response.status_code == 200
    
    # Test logout
    response = await client.post("/logout")
    assert response.status_code == 200
    
    # Test accessing protected route after logout
    response = await client.get("/profile")
    assert response.status_code == 302  # Redirect to login
```

## Security Considerations

### Password Security

```python
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

@app.post("/register")
async def register(request, response):
    data = await request.json
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    
    # Hash password before storing
    hashed_password = hash_password(password)
    
    # Store user in database
    user = await db.create_user(username, hashed_password, email)
    
    return response.json({"message": "User created successfully"}, status_code=201)
```

### Rate Limiting

```python
from nexios.middleware import RateLimitMiddleware

# Add rate limiting to authentication endpoints
app.add_middleware(RateLimitMiddleware(
    rate_limit=5,  # 5 requests
    time_window=60  # per minute
))

@app.post("/login")
async def login(request, response):
    # Login logic here
    pass
```

### Session Security

```python
from nexios.session import SessionMiddleware

# Configure secure session middleware
app.add_middleware(SessionMiddleware(
    secret_key="your-secret-key",
    max_age=3600,  # 1 hour
    secure=True,  # HTTPS only
    httponly=True,  # Prevent XSS
    samesite="strict"  # Prevent CSRF
))
```

This comprehensive authentication guide covers all aspects of implementing secure authentication in Nexios applications. The authentication system is designed to be flexible, secure, and easy to use while providing the power to handle complex authentication scenarios.


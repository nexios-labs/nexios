# Authentication in Nexios

Authentication is a critical component of most web applications, enabling you to identify users, protect resources, and provide personalized experiences. Nexios provides a flexible, robust authentication system that's easy to implement and customize for your specific needs.

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

## Authentication Backends

Nexios includes several built-in authentication backends and allows you to create custom backends for specific needs.

---

### 1. Session Authentication Backend

Session authentication uses server-side sessions to maintain user state. This is ideal for traditional web applications with browser-based access.

#### Implementation

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

#### Key Features

- Checks for a user ID stored in the session (typically set during login)
- Loads the full user object using the provided loader function
- Returns an authenticated user if found, or an unauthenticated user otherwise
- Works with any session storage backend (database, Redis, etc.)

#### Protecting Routes with Session Authentication

```python
from nexios.auth.decorator import auth

@app.get("/profile")
@auth(["session"])  # Only allow session-authenticated users
async def profile(request, response):
    return response.json({
        "id": request.user.id,
        "username": request.user.username,
        "email": request.user.email
    })

@app.get("/admin")
@auth(["session"])
async def admin_panel(request, response):
    if not request.user.is_admin:
        return response.json({"error": "Admin access required"}, status_code=403)

    return response.json({"message": "Welcome to admin panel"})
```

#### Login/Logout Handlers

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

---

### 2. JWT Authentication Backend

JWT (JSON Web Token) authentication uses stateless tokens, ideal for APIs and single-page applications.

#### Implementation

```python
from nexios.auth.backends.jwt import JWTAuthBackend
import jwt

async def get_user_by_id(**payload):
    # Load user from database
    user_id = payload.get("user_id")
    user = await db.get_user(user_id)
    if user:
        return UserModel(
            id=user.id,
            username=user.username,
            email=user.email
        )
    return None

jwt_backend = JWTAuthBackend(authenticate_func=get_user_by_id)

app.add_middleware(AuthenticationMiddleware(backend=jwt_backend))
```

#### Key Features

- Extracts a JWT token from the Authorization header
- Validates the token signature, expiration, etc.
- Extracts the user ID from the token claims
- Loads the full user object using the provided loader function
- Supports custom claims and validation

#### Protecting Routes with JWT Authentication

```python
from nexios.auth.decorator import auth

@app.get("/profile")
@auth(["jwt"])  # Only allow JWT-authenticated users
async def profile(request, response):
    return response.json({
        "id": request.user.id,
        "username": request.user.username,
        "email": request.user.email
    })

@app.get("/admin")
@auth(["jwt"])
async def admin_panel(request, response):
    if not request.user.is_admin:
        return response.json({"error": "Admin access required"}, status_code=403)

    return response.json({"message": "Welcome to admin panel"})
```

#### JWT Token Generation

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
```

---

### 3. API Key Authentication Backend

API key authentication is commonly used for service-to-service communication and machine-to-machine APIs.

#### Implementation

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

#### Key Features

- Extracts an API key from the specified header
- Loads the full user object using the provided loader function
- Returns an authenticated user if found, or an unauthenticated user otherwise
- Ideal for service-to-service authentication

#### Protecting Routes with API Key Authentication

```python
from nexios.auth.decorator import auth

@app.get("/api/data")
@auth(["apikey"])  # Only allow API key authenticated requests
async def get_data(request, response):
    if not request.user.has_permission("read_data"):
        return response.json({"error": "Insufficient permissions"}, status_code=403)

    data = await fetch_data()
    return response.json(data)
```

---

## Creating and Using Custom Authentication Backends

You can create custom authentication backends by implementing the `AuthenticationBackend` abstract base class:

### Custom Backend Implementation

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
        if auth_header == "valid-token":
            return CustomUser(id=1, username="custom_user", is_admin=True)
        return None

# Use the custom backend
custom_backend = CustomAuthBackend()
app.add_middleware(AuthenticationMiddleware(backend=custom_backend))
```

### Protecting Routes with Custom Authentication

```python
from nexios.auth.decorator import auth

@app.get("/custom-protected")
@auth(["custom"])  # Only allow custom-authenticated users
async def custom_protected_route(request, response):
    return response.json({
        "message": "Access granted to custom protected route",
        "user": request.user.username
    })

@app.get("/custom-admin")
@auth(["custom"])
async def custom_admin_route(request, response):
    if not request.user.is_admin:
        return response.json({"error": "Admin access required"}, status_code=403)

    return response.json({"message": "Welcome to custom admin panel"})
```

### Login Handler for Custom Authentication

```python
@app.post("/custom-login")
async def custom_login(request, response):
    # In a real implementation, you would validate credentials
    # and return a custom token or authentication method

    # For this example, we'll just return a valid token
    return response.json({
        "message": "Custom login successful",
        "token": "valid-token"  # This would be validated by our custom backend
    })
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

## Error Handling

### Authentication Exceptions

```python
from nexios.auth.exceptions import AuthenticationFailed

@app.get("/protected")
async def protected_route(request, response):
    if not request.user.is_authenticated:
        raise AuthenticationFailed("Authentication required")

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
```

This comprehensive authentication guide covers all aspects of implementing secure authentication in Nexios applications. The authentication system is designed to be flexible, secure, and easy to use while providing the power to handle complex authentication scenarios.

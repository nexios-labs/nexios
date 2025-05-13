
# Authentication

Authentication is a critical component of most web applications, enabling you to identify users, protect resources, and provide personalized experiences. Nexios provides a flexible, robust authentication system that's easy to implement and customize for your specific needs.
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
    # Load user by ID
    user = await db.get_user(user_id)
auth_backend = SessionAuthBackend(authenticate_func=get_user_by_id)

# Add authentication middleware
app.add_middleware(AuthenticationMiddleware(backend=auth_backend))
```

Once configured, the authentication system will process each request, attempt to authenticate the user, and make the user object available via `request.user`:

```python
@app.get("/profile")
async def profile(req, res):
    if req.user.is_authenticated:
        return res.json({
            "id": req.user.id,
            "username": req.user.username,
            "email": req.user.email
        })
    else:
        return res.redirect("/login")
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

1. When a request arrives, the middleware calls the authentication backend's `authenticate` method
2. If authentication succeeds, a user object is returned along with an authentication type
3. The user is attached to `request.scope["user"]` and accessible via `request.user`
4. An authentication type string is also attached to `request.scope["auth"]`
5. If authentication fails, an `UnauthenticatedUser` instance is attached instead

## Authentication Backends

Nexios includes several built-in authentication backends and allows you to create custom backends for specific needs.

### Built-in Authentication Backends

#### 1. Session Authentication Backend

```python
from nexios.auth.backends.session import SessionAuthBackend

session_backend = SessionAuthBackend(
    user_key="user_id",  # Session key for user ID
    authenticate_func=get_user_by_id  # Function to load user by ID
)

app.add_middleware(AuthenticationMiddleware(backend=session_backend))
```

The session backend:
- Checks for a user ID stored in the session (typically set during login)
- Loads the full user object using the provided loader function
- Returns an authenticated user if found, or an unauthenticated user otherwise

#### 2. JWT Authentication Backend

```python
from nexios.auth.backends.jwt import JWTAuthBackend

jwt_backend = JWTAuthBackend(
    secret_key="your-jwt-secret-key",
    algorithm="HS256",  # Optional, default is HS256
    token_prefix="Bearer",  # Optional, default is "Bearer"
    authenticate_func=get_user_by_id,  # Function to load user by ID
    auth_header_name="Authorization"  # Optional, default is "Authorization"
)

app.add_middleware(AuthenticationMiddleware(backend=jwt_backend))
```

The JWT backend:
- Extracts a JWT token from the Authorization header
- Validates the token signature, expiration, etc.
- Extracts the user ID from the token claims
- Loads the full user object using the provided loader function

#### 3. API Key Authentication Backend

```python
from nexios.auth.backends.apikey import APIKeyBackend

async def get_user_by_api_key(api_key):
    # Lookup user with the given API key
    user = await db.find_user_by_api_key(api_key)
    if user:
        return UserModel(id=user.id, username=user.username, api_key=api_key)
    return None

api_key_backend = APIKeyBackend(
    key_name="X-API-Key",  # Header containing the API key
    user_loader=get_user_by_api_key  # Function to load user by API key
)

app.add_middleware(AuthenticationMiddleware(backend=api_key_backend))
```

The API key backend:
- Extracts an API key from the specified header
- Loads the full user object using the provided loader function
- Returns an authenticated user if found, or an unauthenticated user otherwise

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
            # Return unauthenticated user if credentials not found
            return UnauthenticatedUser(), "no-auth"
        
        # Validate credentials
        # ...authentication logic...
        
        # If validation succeeds, return a user object and auth type
        if valid_credentials:
            user = CustomUser(id=123, username="example_user")
            return user, "custom-auth"
        
        # If validation fails, return unauthenticated user
        return UnauthenticatedUser(), "no-auth"
```

## User Objects and Lifecycle

User objects in Nexios implement the `BaseUser` interface, ensuring a consistent API regardless of the authentication backend.

### The User Lifecycle

1. **Request Arrival**: When a request reaches your application, it initially has no user information
2. **Authentication Process**:
   - The authentication middleware calls the backend's `authenticate` method
   - The backend extracts credentials from the request (headers, session, etc.)
   - The backend validates the credentials and retrieves or creates a user object
3. **User Attachment**: The middleware attaches the user object to the request
4. **Request Processing**: Your handlers can access `request.user` to check authentication status and user details
5. **Response**: After your handler processes the request, the response is sent back to the client

### User Object Interface

All user objects (both authenticated and unauthenticated) share a common interface:

```python
from nexios.auth.base import BaseUser

class CustomUser(BaseUser):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email
    
    @property
    def is_authenticated(self):
        # Always return True for authenticated users
        return True
    
    def get_display_name(self):
        # Return a human-readable name
        return self.username
```

The `UnauthenticatedUser` class implements the same interface but returns `False` for `is_authenticated`.

## Protecting Routes with Authentication

### Basic Route Protection

The simplest way to protect routes is to check `request.user.is_authenticated` in your handlers:

```python
@app.get("/admin")
async def admin_dashboard(req, res):
    if not req.user.is_authenticated:
        return res.redirect("/login")
    
    # Process authenticated request
    return res.html("Admin Dashboard")
```

## Using Authentication Decorators

For cleaner route protection, Nexios provides authentication decorators:

```python
from nexios.auth.decorator import auth

@app.get("/dashboard")
@auth(["auth-type"]) #jwt , session or cusotom
async def dashboard(req, res):
    # This route is only accessible to authenticated users
    # Unauthenticated requests will be redirected to /login
    return res.html("Dashboard")

@app.get("/api/data")
@auth(["auth-type"])
async def api_data(req, res):
    # This route returns 401 Unauthorized for unauthenticated requests
    return res.json({"data": "Protected API data"})
```

## Custom Authentication Requirements

You can create custom decorators for more specific authentication needs:

```python
from functools import wraps

def requires_admin(handler):
    @wraps(handler)
    async def wrapper(req, res, *args, **kwargs):
        if not req.user.is_authenticated or not req.user.is_admin:
            return res.json({"error": "Admin access required"}, status_code=403)
        return await handler(req, res, *args, **kwargs)
    return wrapper

@app.get("/admin/users")
@requires_admin
async def admin_users(req, res):
    # Only admins can access this route
    return res.json({"users": ["user1", "user2"]})
```

## Authentication Flows

## Session-Based Authentication

Session-based authentication is a common approach for web applications:

```python
from nexios import NexiosApp
from nexios.auth.middleware import AuthenticationMiddleware
from nexios.auth.backends.session import SessionAuthBackend
from nexios.session.middleware import SessionMiddleware

app = NexiosApp()
app.config.secret_key = "your-secure-secret-key"

# Add session middleware first
app.add_middleware(SessionMiddleware())

# Add authentication with session backend
async def get_user_by_id(user_id):
    # Query the database for the user
    user = await db.get_user(user_id)
    if user:
        return User(
            id=user.id,
            username=user.username,
            email=user.email,
            is_admin=user.is_admin
        )
    return None

session_backend = SessionAuthBackend(
    user_key="user_id",
    authenticate_func=get_user_by_id
)
app.add_middleware(AuthenticationMiddleware(backend=session_backend))

# Login route
@app.post("/login")
async def login(req, res):
    data = await req.form
    username = data.get("username")
    password = data.get("password")
    
    # Verify credentials
    user = await db.verify_credentials(username, password)
    if not user:
        return res.redirect("/login?error=invalid")
    
    # Store user ID in session
    req.session["user_id"] = user.id
    
    return res.redirect("/dashboard")

# Logout route
@app.post("/logout")
async def logout(req, res):
    # Clear session
    req.session.clear()
    
    return res.redirect("/login")
```

## JWT-Based Authentication

JWT authentication is commonly used for APIs:

```python
from nexios import NexiosApp
from nexios.auth.middleware import AuthenticationMiddleware
from nexios.auth.backends.jwt import JWTAuthBackend
import jwt
import time

app = NexiosApp()
jwt_secret = "your-jwt-secret-key"

# Configure JWT authentication
async def get_user_by_id(user_id):
    user = await db.get_user(user_id)
    if user:
        return User(
            id=user.id,
            username=user.username,
            email=user.email,
            is_admin=user.is_admin
        )
    return None

jwt_backend = JWTAuthBackend(
    secret_key=jwt_secret,
    algorithm="HS256",
    authenticate_func=get_user_by_id
)
app.add_middleware(AuthenticationMiddleware(backend=jwt_backend))

# Login route that returns JWT
@app.post("/api/login")
async def api_login(req, res):
    data = await req.json
    username = data.get("username")
    password = data.get("password")
    
    # Verify credentials
    user = await db.verify_credentials(username, password)
    if not user:
        return res.json({"error": "Invalid credentials"}, status_code=401)
    
    # Generate JWT token
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "exp": int(time.time()) + 3600  # 1 hour expiration
    }
    token = jwt.encode(payload, jwt_secret, algorithm="HS256")
    
    return res.json({
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 3600
    })

# Protected API route
@app.get("/api/profile")
@auth(["jwt"])
async def api_profile(req, res):
    return res.json({
        "id": req.user.id,
        "username": req.user.username,
        "email": req.user.email
    })
```

The authentication system in Nexios is built with modern API security practices in mind. It supports a variety of authentication methods, including JSON Web Tokens (JWT), API keys, and session-based authentication. The system is designed to be fully asynchronous, ensuring that authentication processes do not block your application's performance.


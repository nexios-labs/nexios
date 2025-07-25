# Complete Authentication Guide for Nexios

Authentication is one of the most fundamental aspects of web application security and user experience. It determines who can access your application and how their identity is verified and maintained throughout their interaction with your system. Nexios provides a comprehensive, flexible, and developer-friendly authentication system that scales from simple applications to complex enterprise systems.

## Understanding Authentication in Web Applications

### What is Authentication?

Authentication is the process of verifying that someone or something is who they claim to be. In web applications, this process involves confirming a user's identity through various types of credentials such as passwords, tokens, or certificates. The authentication system must also maintain that verified identity across multiple requests to provide a seamless user experience. Additionally, authentication serves as the foundation for protecting sensitive resources from unauthorized access.

### Core Authentication Concepts

Authentication in modern web applications operates on several fundamental principles that ensure both security and usability. The first principle is identity verification, which requires users to provide proof of who they are through credentials that only they should possess. The second principle is session persistence, which allows the application to remember a user's authenticated state across multiple requests without requiring them to re-authenticate constantly. The third principle is security enforcement, which ensures that only verified users can access protected resources and functionality.

Understanding these principles is crucial because they form the foundation of how Nexios handles authentication throughout your application. When a user first accesses your application, they must prove their identity through the authentication process. Once verified, the system creates a representation of that user that persists for the duration of their session or until their credentials expire. This approach balances security requirements with user experience by minimizing the friction of repeated authentication while maintaining strong security boundaries.

### Why Choose Nexios Authentication?

Nexios authentication system offers several distinct advantages that make it suitable for a wide range of applications. The system provides flexibility by supporting multiple authentication methods, allowing you to choose the approach that best fits your application's needs and security requirements. The design emphasizes simplicity with a clean, intuitive API that reduces the complexity of implementing secure authentication. Security is built into the system from the ground up, incorporating industry best practices and proven security patterns to protect against common vulnerabilities.

The system also prioritizes extensibility, making it straightforward to create custom authentication backends when your application has unique requirements. Performance considerations are integrated throughout the design, ensuring that authentication processing doesn't become a bottleneck in your application. Finally, the system supports industry-standard protocols and practices, making it compatible with existing security infrastructure and compliance requirements.

## Authentication Flow Deep Dive

### How Authentication Works at the Basic Level

Authentication in Nexios works through a simple three-step process that happens automatically for every request. First, when someone sends a request to your application, Nexios looks for some kind of proof that they are who they say they are. Second, Nexios checks if that proof is valid by comparing it against your user database or authentication system. Third, if the proof is valid, Nexios creates a user object and attaches it to the request so your code can use it.

The proof of identity can be many different things depending on what type of authentication you choose. It might be a username and password sent in a login form. It could be a special token included in the request headers. It might be a session cookie that was set when the user logged in earlier. The important thing is that it's something that proves the person making the request is a real user of your application.

When Nexios receives a request, it automatically examines that request looking for authentication information. This happens before your route handlers run, so by the time your code executes, the authentication work is already done. If authentication succeeds, you get a user object with information about who is making the request. If authentication fails or no authentication is provided, you get an empty user object that you can check.

### The Simple Authentication Cycle

The authentication process follows a predictable cycle that makes it easy to understand and work with. When a user first visits your application, they typically don't have any authentication credentials yet. Your application can detect this and show them a login page or prompt them to provide credentials. Once they provide valid credentials, your application creates some kind of authentication token or session that proves they are authenticated.

For all future requests from that user, they include their authentication token or session information with each request. Nexios automatically checks this information and recreates the user object for each request. This means your route handlers always have access to user information without having to manually check credentials every time. The user stays authenticated until their token expires, they log out, or their session ends.

This cycle repeats for every user and every request, but because Nexios handles it automatically, you don't have to write the same authentication code over and over again. You just configure authentication once and then use the user object that Nexios provides in your route handlers.

### Basic Example of How It Works

```python
# This is what happens automatically - you don't write this code
# 1. Request comes in with some authentication information
# 2. Nexios checks if the authentication is valid
# 3. Nexios creates a user object and attaches it to the request

# This is what you write - your route handler
@app.get("/api/profile")
async def get_profile(request, response):
    # The user object is already available
    user = request.user

    # Check if they're authenticated
    if user.is_authenticated:
        # They're logged in, show their profile
        return response.json({
            "username": user.username,
            "email": user.email
        })
    else:
        # They're not logged in, ask them to log in
        return response.json(
            {"error": "Please log in first"},
            status_code=401
        )
```

### Setting Up Basic Authentication

To use authentication in your Nexios application, you need to do two simple things. First, you choose what type of authentication you want to use and configure it. Second, you add the authentication middleware to your application so it runs automatically for every request.

```python
from nexios.auth.middleware import AuthenticationMiddleware
from nexios.auth.backends.session import SessionAuthBackend

# Step 1: Configure how to find users
async def find_user_by_id(user_id):
    # Look up the user in your database
    user_data = await database.get_user(user_id)
    if user_data:
        return User(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"]
        )
    return None

# Step 2: Create the authentication backend
auth_backend = SessionAuthBackend(authenticate_func=find_user_by_id)

# Step 3: Add it to your application
app.add_middleware(AuthenticationMiddleware(backend=auth_backend))

# That's it! Now every request will have authentication
```

## Core Components Explained

### Understanding the Three-Layer Architecture

The Nexios authentication system is built around three main components that work together to provide secure, flexible authentication. Each component has a specific responsibility and operates at a different level of the authentication process. Understanding how these components interact is essential for implementing authentication effectively and troubleshooting any issues.

The first component is the Authentication Middleware, which serves as the central coordinator of the entire authentication process. This middleware intercepts every incoming HTTP request and orchestrates the authentication workflow. It extracts authentication credentials from requests, coordinates with authentication backends for validation, and manages the user context that becomes available to your route handlers. The middleware also handles error scenarios gracefully, ensuring that authentication failures don't break your application.

The second component consists of Authentication Backends, which handle the actual credential validation logic. These backends are specialized components that understand specific authentication methods such as JWT tokens, session cookies, or API keys. Each backend knows how to extract its specific type of credentials from requests, validate those credentials against appropriate data sources, and return user objects when authentication succeeds. This modular design allows you to support multiple authentication methods simultaneously.

The third component is the User Object system, which provides a consistent interface for working with user identity throughout your application. User objects represent both authenticated and unauthenticated users with the same interface, simplifying your code and reducing the likelihood of errors. These objects store user information and metadata while providing methods for checking authentication status and accessing user properties.

### Authentication Middleware

The Authentication Middleware is the heart of Nexios's authentication system. It acts as a central coordinator that processes every incoming request, extracts authentication credentials, validates them through backends, and makes user information available to your route handlers.

### Advanced Middleware Configuration

For applications that need multiple authentication methods, you can configure multiple backends:

```python
from nexios.auth.middleware import AuthenticationMiddleware
from nexios.auth.backends.jwt import JWTAuthBackend
from nexios.auth.backends.session import SessionAuthBackend
from nexios.auth.backends.apikey import APIKeyBackend

# Create multiple backends for different authentication methods
jwt_backend = JWTAuthBackend(authenticate_func=load_user_from_jwt)
session_backend = SessionAuthBackend(authenticate_func=load_user_from_session)
api_key_backend = APIKeyBackend(
    key_name="X-API-Key",
    authenticate_func=load_user_from_api_key
)

# The middleware will try backends in order until one succeeds
app.add_middleware(
    AuthenticationMiddleware,
    backends=[jwt_backend, session_backend, api_key_backend]
)
```

### How Middleware Processes Requests

The authentication middleware follows a consistent process for every request:

1. **Request Interception**: The middleware intercepts the request before it reaches your route handlers
2. **Credential Extraction**: It examines the request for authentication credentials (headers, cookies, etc.)
3. **Backend Delegation**: Calls the `authenticate` method of the configured backend(s)
4. **User Resolution**: If authentication succeeds, a user object is created and returned
5. **Context Attachment**: The user object is attached to `request.user` for easy access
6. **Authentication Type Tracking**: The authentication method is stored in `request.scope["auth"]`
7. **Graceful Fallback**: If authentication fails, an `UnauthenticatedUser` object is attached instead

### Accessing Authentication Information

Once the middleware has processed a request, authentication information is readily available:

```python
@app.get("/api/dashboard")
async def dashboard(request, response):
    # Access the user object (always available)
    user = request.user

    # Check if user is authenticated
    if user.is_authenticated:
        # Get authentication method used
        auth_method = request.scope.get("auth")  # e.g., "jwt", "session", "apikey"

        return response.json({
            "message": f"Welcome {user.display_name}!",
            "user_id": user.identity,
            "auth_method": auth_method,
            "dashboard_data": await get_user_dashboard_data(user.id)
        })
    else:
        return response.json(
            {"error": "Authentication required to access dashboard"},
            status_code=401
        )
```

### Middleware Error Handling

The middleware gracefully handles various error scenarios:

```python
# The middleware automatically handles these cases:
# - Missing authentication credentials
# - Invalid or expired tokens
# - Database connection errors during user lookup
# - Malformed authentication headers
# - Backend authentication exceptions

@app.get("/api/protected")
async def protected_endpoint(request, response):
    user = request.user

    # User will always be available, but may be UnauthenticatedUser
    if not user.is_authenticated:
        return response.json(
            {
                "error": "Authentication required",
                "message": "Please provide valid authentication credentials"
            },
            status_code=401
        )

    # User is authenticated, proceed with business logic
    return response.json({"data": "Protected content"})
```

## Authentication Backends

Nexios includes several built-in authentication backends and allows you to create custom backends for specific needs.

### Session Authentication Backend

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
    # In a real implementation, you would validate credentials
    # and return a custom token or authentication method

    # For this example, we'll just return a valid token
    return response.json({
        "message": "Login successful",
        "token": "valid-token"  # This would be validated by our custom backend
    })

@app.post("/logout")
async def logout(request, response):
    # Clear session
    request.session.clear()
    return response.json({"message": "Logout successful"})
```

### JWT Authentication Backend

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
    # In a real implementation, you would validate credentials
    # and return a custom token or authentication method

    # For this example, we'll just return a valid token
    return response.json({
        "message": "Login successful",
        "token": "valid-token"  # This would be validated by our custom backend
    })
```

### API Key Authentication Backend

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

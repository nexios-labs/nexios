# Authentication API Reference

## Overview

Nexios provides a robust authentication system that supports various authentication mechanisms. This document covers how to implement and customize authentication in your Nexios application.

## Table of Contents

- [Authentication Backend](#authentication-backend)
- [Built-in Authentication Classes](#built-in-authentication-classes)
- [Custom Authentication](#custom-authentication)
- [Error Handling](#error-handling)
- [Security Considerations](#security-considerations)
- [Best Practices](#best-practices)

## Authentication Backend

The `AuthenticationBackend` class is the foundation for implementing custom authentication in Nexios applications.

### Base Class

```python
from typing import Any, Optional
from nexios.auth import AuthenticationBackend
from nexios.http import Request, Response

class CustomAuthBackend(AuthenticationBackend):
    async def authenticate(self, req: Request, res: Response) -> Any:
        """
        Authenticate a request and return a user object.

        Args:
            req: The incoming HTTP request
            res: The HTTP response that may be modified during authentication

        Returns:
            Any: The authenticated user object if authentication succeeds

        Raises:
            AuthenticationError: If authentication fails
        """
        raise NotImplementedError("Subclasses must implement authenticate()")
```

## Built-in Authentication Classes

### JWT Authentication

```python
import jwt
from datetime import datetime, timedelta
from typing import Optional

class JWTBackend(AuthenticationBackend):
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    async def authenticate(self, req: Request, res: Response) -> dict:
        """
        Authenticate using JWT token from Authorization header.

        Token format: "Bearer <token>"
        """
        auth_header = req.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationError(401, "Missing or invalid authorization header")

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError(401, "Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(401, f"Invalid token: {str(e)}")

    def create_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a new JWT token.

        Args:
            data: Data to include in the token
            expires_delta: Optional expiration time delta (default: 15 minutes)

        Returns:
            str: Encoded JWT token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
```

### Session Authentication

```python
class SessionAuthBackend(AuthenticationBackend):
    def __init__(self, session_store: Any, session_cookie: str = "session_id"):
        self.session_store = session_store
        self.session_cookie = session_cookie

    async def authenticate(self, req: Request, res: Response) -> dict:
        """
        Authenticate using session cookie.
        """
        session_id = req.cookies.get(self.session_cookie)
        if not session_id:
            raise AuthenticationError(401, "No session cookie found")

        session_data = await self.session_store.get(session_id)
        if not session_data:
            raise AuthenticationError(401, "Invalid or expired session")

        return session_data
```

## Using Authentication in Routes

### Basic Usage

```python
from nexios import NexiosApp
from nexios.auth import AuthenticationError
from nexios.middleware import AuthMiddleware

app = NexiosApp()

# Initialize authentication backend
auth_backend = JWTBackend(secret_key="your-secret-key")

# Add authentication middleware
app.add_middleware(
    AuthMiddleware,
    backend=auth_backend,
    exclude_paths=["/login", "/docs", "/openapi.json"]
)

# Protected route
@app.get("/protected")
async def protected_route(request, response, user: dict = Depends(auth_backend)):
    return response.json({"message": f"Hello, {user['username']}!"})

# Login route
@app.post("/login")
async def login(request, response):
    credentials = await request.json()
    user = await verify_credentials(credentials["username"], credentials["password"])

    if not user:
        raise AuthenticationError(401, "Invalid credentials")

    token = auth_backend.create_token(
        {"user_id": user["id"], "username": user["username"]},
        expires_delta=timedelta(days=1)
    )

    return response.json({"access_token": token, "token_type": "bearer"})
```

## Error Handling

### AuthenticationError

```python
from nexios.auth import AuthenticationError

# Basic usage
raise AuthenticationError(401, "Invalid credentials")

# With additional headers (e.g., for WWW-Authenticate)
raise AuthenticationError(
    401,
    "Bearer token required",
    headers={"WWW-Authenticate": "Bearer realm=\"api\""}
)
```

## Security Considerations

1. **Token Security**

   - Always use HTTPS in production
   - Set appropriate token expiration times
   - Store tokens securely (httpOnly, Secure, SameSite flags for cookies)

2. **Password Security**

   - Never store plain text passwords
   - Use strong hashing algorithms (bcrypt, Argon2)
   - Implement rate limiting on authentication endpoints

3. **Session Security**
   - Use secure, httpOnly cookies for session IDs
   - Implement proper session expiration
   - Rotate session IDs after login

## Best Practices

1. **Token Management**

   - Use short-lived access tokens with refresh tokens
   - Implement token revocation
   - Log token usage for security monitoring

2. **Error Handling**

   - Use specific error messages for debugging
   - Log authentication failures
   - Implement account lockout after multiple failed attempts

3. **Performance**

   - Cache authentication results when possible
   - Use efficient session storage backends
   - Consider stateless authentication for microservices

4. **Testing**
   - Test all authentication flows
   - Test edge cases (expired tokens, invalid formats)
   - Test with different user roles and permissions

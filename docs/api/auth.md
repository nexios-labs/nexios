# Authentication API Reference

The Authentication API in Nexios provides a flexible and secure way to handle user authentication in your applications. It includes base classes for implementing custom authentication backends and utilities for managing authentication state.

## Authentication Backend

The `AuthenticationBackend` class is the foundation for implementing custom authentication in Nexios applications.

```python
from nexios.auth import AuthenticationBackend
from nexios.http import Request, Response

class CustomAuthBackend(AuthenticationBackend):
    async def authenticate(self, req: Request, res: Response) -> Any:
        # Implement your authentication logic here
        pass
```

### Methods

#### `authenticate(req: Request, res: Response) -> Any`

Authenticates a user based on the request. This method must be implemented by all authentication backends.

**Parameters:**
- `req` (Request): The incoming HTTP request containing authentication details
- `res` (Response): The HTTP response object that may be modified during authentication

**Returns:**
- Any: An authenticated user instance if authentication succeeds

**Raises:**
- `AuthenticationError`: If authentication fails

**Example:**
```python
class JWTBackend(AuthenticationBackend):
    async def authenticate(self, req: Request, res: Response) -> User:
        auth_header = req.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationError(401, "Invalid authentication credentials")
            
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = await get_user_by_id(payload["user_id"])
            if not user:
                raise AuthenticationError(401, "User not found")
            return user
        except jwt.InvalidTokenError:
            raise AuthenticationError(401, "Invalid token")
```

## Authentication Exceptions

### `AuthenticationError`

Base exception class for all authentication-related errors.

```python
from nexios.auth import AuthenticationError

# Raise with status code and detail
raise AuthenticationError(401, "Invalid credentials")

# Raise with additional headers
raise AuthenticationError(
    401,
    "Invalid credentials",
    headers={"WWW-Authenticate": "Bearer"}
)
```

**Parameters:**
- `status_code` (int): HTTP status code for the error
- `detail` (str): Error message
- `headers` (Optional[Dict[str, Any]]): Optional headers for the response

## Using Authentication in Routes

### Basic Authentication

```python
from nexios.auth import AuthenticationBackend
from nexios.dependencies import Depends

class BasicAuth(AuthenticationBackend):
    async def authenticate(self, req: Request, res: Response) -> User:
        auth = req.headers.get("Authorization")
        if not auth or not auth.startswith("Basic "):
            raise AuthenticationError(401, "Invalid credentials")
            
        credentials = base64.b64decode(auth.split(" ")[1]).decode()
        username, password = credentials.split(":")
        
        user = await verify_credentials(username, password)
        if not user:
            raise AuthenticationError(401, "Invalid credentials")
            
        return user

# Use in routes
@app.get("/protected")
async def protected_route(
    request: Request,
    response: Response,
    user: User = Depends(BasicAuth())
):
    return response.json({"message": f"Hello, {user.username}!"})
```

### JWT Authentication

```python
class JWTAuth(AuthenticationBackend):
    async def authenticate(self, req: Request, res: Response) -> User:
        token = req.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            raise AuthenticationError(401, "Missing token")
            
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = await get_user_by_id(payload["user_id"])
            if not user:
                raise AuthenticationError(401, "User not found")
            return user
        except jwt.InvalidTokenError:
            raise AuthenticationError(401, "Invalid token")

# Use in routes
@app.get("/api/protected")
async def protected_api(
    request: Request,
    response: Response,
    user: User = Depends(JWTAuth())
):
    return response.json({"user": user.dict()})
```

### Session-Based Authentication

```python
class SessionAuth(AuthenticationBackend):
    async def authenticate(self, req: Request, res: Response) -> User:
        session_id = req.cookies.get("session_id")
        if not session_id:
            raise AuthenticationError(401, "No session")
            
        session = await get_session(session_id)
        if not session or session.expired:
            raise AuthenticationError(401, "Invalid session")
            
        user = await get_user_by_id(session.user_id)
        if not user:
            raise AuthenticationError(401, "User not found")
            
        return user

# Use in routes
@app.get("/dashboard")
async def dashboard(
    request: Request,
    response: Response,
    user: User = Depends(SessionAuth())
):
    return response.json({"dashboard": await get_user_dashboard(user.id)})
```

## Best Practices

1. **Always Use HTTPS**: Ensure all authentication-related endpoints are served over HTTPS.

2. **Implement Rate Limiting**: Protect authentication endpoints from brute force attacks.

```python
from nexios.middleware import RateLimitMiddleware

app.add_middleware(
    RateLimitMiddleware,
    rate_limit=5,  # requests
    time_window=60  # seconds
)
```

3. **Secure Password Storage**: Use strong hashing algorithms for password storage.

```python
from passlib.hash import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.verify(password, hashed)
```

4. **Token Expiration**: Implement token expiration and refresh mechanisms.

```python
class JWTAuth(AuthenticationBackend):
    async def authenticate(self, req: Request, res: Response) -> User:
        token = req.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            raise AuthenticationError(401, "Missing token")
            
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if payload["exp"] < time.time():
                raise AuthenticationError(401, "Token expired")
            # ... rest of the authentication logic
        except jwt.InvalidTokenError:
            raise AuthenticationError(401, "Invalid token")
```

5. **Logging and Monitoring**: Implement comprehensive logging for authentication events.

```python
import logging

logger = logging.getLogger("auth")

class LoggingAuth(AuthenticationBackend):
    async def authenticate(self, req: Request, res: Response) -> User:
        try:
            # ... authentication logic
            logger.info(f"User {user.id} authenticated successfully")
            return user
        except AuthenticationError as e:
            logger.warning(f"Authentication failed: {str(e)}")
            raise
``` 
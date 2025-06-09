# 🚀 Day 8: JWT Auth (Part 1)

## JWT Authentication Basics

JSON Web Tokens (JWT) provide a secure way to handle authentication in Nexios:

```python
from nexios import NexiosApp,MakeConfig
from nexios.auth import AuthenticationMiddleware,JWTAuthBackend
from nexios.http import Request, Response
import jwt
from datetime import datetime, timedelta
config = MakeConfig(secret_key = "3456789876trfvbj8765rfvbnjurse4567890987ytgv")
app = NexiosApp()
async def get_user_from_payload(**payload):
    ...
backend = JWTAuthBackend(get_user_from_payload)


app.add_middleware(AuthenticationMiddleware(backend = backend))
```

## Creating and Verifying Tokens

### Token Creation

```python
from nexios.auth import create_jwt
from nexios.models import User

@app.post("/auth/login")
async def login(request: Request, response: Response):
    data = await request.json
    username = data.get("username")
    password = data.get("password")
    
    # Validate credentials (implement your own logic)
    user = await validate_user(username, password)
    if not user:
        return response.json(
            content={"error": "Invalid credentials"},
            status_code=401
        )
    
    # Create access token
    token = create_jwt(
        payload={
            "sub": str(user.id),
            "username": user.username,
            "roles": user.roles
        }
    )
    
    return {
        "access_token": token,
        "token_type": "bearer"
    }

async def validate_user(username: str, password: str) -> User:
    # Implement your user validation logic
    # Return User object if valid, None otherwise
    pass
```


## Protecting Endpoints

### Using the Auth Middleware

```python
from nexios.auth import auth
from nexios.exceptions import AuthenticationError

# Protect single endpoint
@app.get("/protected")
@auth(["jwt"])
async def protected_route(request: Request, response: Response):
    # Access authenticated user
    user = request.user
    return {
        "message": f"Hello, {user.username}!",
        "user_id": str(user.id)
    }

# Protect group of routes
protected_router = Router(prefix="/api")

@protected_router.get("/profile")
async def get_profile(request: Request, response: Response):
    user = request.user
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email
    }

@protected_router.put("/profile")
async def update_profile(request: Request, response: Response):
    user = request.user
    data = await request.json()
    
    # Update user profile
    updated_user = await update_user_profile(user.id, data)
    return updated_user.dict()

# Include protected routes
app.mount_router(protected_router)
```



## Error Handling

```python
from nexios.exceptions import AuthenticationError, AuthorizationError

@app.add_exception_handler(AuthenticationError)
async def handle_auth_error(request: Request,response :Response,  exc: AuthenticationError):
    return response.json(
        content={"error": str(exc)},
        status_code=401
    )

@app.add_exception_handler(AuthorizationError)
async def handle_auth_error(request: Request,response :Response, exc: AuthorizationError):
    return response.json(
        content={"error": str(exc)},
        status_code=403
    )
```

## 📝 Practice Exercise

1. Implement a complete authentication system:
   - User registration
   - Login with JWT
   - Password reset
   - Token refresh

2. Add role-based access control:
   - User roles
   - Permission checking
   - Role hierarchy

3. Implement security features:
   - Password hashing
   - Token blacklisting
   - Rate limiting

## 📚 Additional Resources
- [JWT Introduction](https://jwt.io/introduction)

## 🎯 Next Steps
Tomorrow in [Day 9: JWT Auth (Part 2)](../day09/index.md), we'll explore:
- Token rotation
- Token expiration
- Custom claims
- JTI blacklisting
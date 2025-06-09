# Day 8: Authentication & Authorization

Welcome to Day 8! Today we'll learn how to implement authentication and authorization in Nexios applications.

## Understanding Auth Concepts

- Authentication: Verifying who a user is
- Authorization: Determining what a user can do
- Session management
- Token-based auth
- Role-based access control (RBAC)

## Basic Authentication

```python
from nexios import NexiosApp
from nexios.http import Request, Response
from nexios.exceptions import HTTPException
import jwt
import bcrypt
from datetime import datetime, timedelta

app = NexiosApp()

# Secret key for JWT
SECRET_KEY = "your-secret-key"

async def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode(),
        hashed_password.encode()
    )

@app.post("/auth/register")
async def register(request: Request, response: Response):
    data = await request.json()
    
    # Hash password
    data["password"] = await hash_password(data["password"])
    
    # Create user
    query = users.insert().values(**data)
    user_id = await database.execute(query)
    
    return response.json({
        "id": user_id,
        "username": data["username"]
    }, status_code=201)

@app.post("/auth/login")
async def login(request: Request, response: Response):
    data = await request.json()
    
    # Find user
    query = users.select().where(users.c.username == data["username"])
    user = await database.fetch_one(query)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not await verify_password(data["password"], user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate token
    token = jwt.encode({
        "sub": user["id"],
        "exp": datetime.utcnow() + timedelta(days=1)
    }, SECRET_KEY)
    
    return response.json({"access_token": token})
```

## Authentication Middleware

```python
async def auth_middleware(request: Request, response: Response, call_next):
    auth = request.headers.get("Authorization")
    
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid token"
        )
    
    token = auth.split(" ")[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload["sub"]
        
        # Get user
        query = users.select().where(users.c.id == user_id)
        user = await database.fetch_one(query)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )
        
        # Add user to request
        request.state.user = user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    
    return await call_next()

# Protected route example
@app.get("/profile", middleware=[auth_middleware])
async def profile(request: Request, response: Response):
    return response.json(dict(request.state.user))
```

## Role-Based Authorization

```python
from functools import wraps
from typing import List

def require_roles(roles: List[str]):
    def decorator(handler):
        @wraps(handler)
        async def wrapper(request: Request, response: Response, *args, **kwargs):
            user = request.state.user
            
            # Get user roles
            query = (
                roles_table.select()
                .join(user_roles)
                .where(user_roles.c.user_id == user["id"])
            )
            user_roles = await database.fetch_all(query)
            user_role_names = [r["name"] for r in user_roles]
            
            # Check roles
            if not any(role in user_role_names for role in roles):
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient permissions"
                )
            
            return await handler(request, response, *args, **kwargs)
        return wrapper
    return decorator

# Protected admin route
@app.get("/admin/users")
@require_roles(["admin"])
async def list_users(request: Request, response: Response):
    users = await database.fetch_all(users.select())
    return response.json([dict(user) for user in users])
```

## Session Management

```python
from uuid import uuid4
import redis
import json

# Redis connection
redis_client = redis.Redis()

async def create_session(user_id: int) -> str:
    session_id = str(uuid4())
    session_data = {
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Store session
    redis_client.setex(
        f"session:{session_id}",
        timedelta(days=1).total_seconds(),
        json.dumps(session_data)
    )
    
    return session_id

async def get_session(session_id: str) -> dict:
    data = redis_client.get(f"session:{session_id}")
    if not data:
        return None
    return json.loads(data)

async def delete_session(session_id: str):
    redis_client.delete(f"session:{session_id}")

# Session middleware
async def session_middleware(request: Request, response: Response, call_next):
    session_id = request.cookies.get("session_id")
    
    if session_id:
        session = await get_session(session_id)
        if session:
            request.state.session = session
    
    return await call_next()

# Login with session
@app.post("/auth/login")
async def login(request: Request, response: Response):
    data = await request.json()
    
    # Verify credentials...
    
    # Create session
    session_id = await create_session(user["id"])
    
    # Set cookie
    response.set_cookie(
        "session_id",
        session_id,
        httponly=True,
        secure=True,
        samesite="strict"
    )
    
    return response.json({"message": "Logged in"})
```

## OAuth Integration

```python
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
oauth.register(
    name="google",
    client_id="your-client-id",
    client_secret="your-client-secret",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"}
)

@app.get("/auth/google")
async def google_auth(request: Request, response: Response):
    redirect_uri = request.url_for("google_auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google/callback")
async def google_auth_callback(request: Request, response: Response):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    
    # Create or update user...
    
    return response.redirect("/")
```

## Mini-Project: Auth System

```python
from nexios import NexiosApp
from nexios.http import Request, Response
from nexios.exceptions import HTTPException
import jwt
import bcrypt
from datetime import datetime, timedelta
import redis
import json
from uuid import uuid4
from typing import List, Optional

# Setup
app = NexiosApp()
redis_client = redis.Redis()
SECRET_KEY = "your-secret-key"

# Models
class User(BaseModel):
    id: int
    username: str
    email: str
    roles: List[str] = []

class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Auth utilities
async def create_tokens(user_id: int) -> TokenData:
    # Access token
    access_token = jwt.encode({
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }, SECRET_KEY)
    
    # Refresh token
    refresh_token = str(uuid4())
    redis_client.setex(
        f"refresh_token:{refresh_token}",
        timedelta(days=7).total_seconds(),
        str(user_id)
    )
    
    return TokenData(
        access_token=access_token,
        refresh_token=refresh_token
    )

# Auth middleware
async def auth_middleware(request: Request, response: Response, call_next):
    auth = request.headers.get("Authorization")
    
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid token"
        )
    
    token = auth.split(" ")[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload["sub"]
        
        # Get user
        query = users.select().where(users.c.id == user_id)
        user = await database.fetch_one(query)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )
        
        # Add user to request
        request.state.user = User(**dict(user))
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    
    return await call_next()

# Routes
@app.post("/auth/register")
async def register(request: Request, response: Response):
    data = await request.json()
    
    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
        raise HTTPException(
            status_code=400,
            detail="Invalid email format"
        )
    
    # Check if user exists
    query = users.select().where(
        (users.c.username == data["username"]) |
        (users.c.email == data["email"])
    )
    existing_user = await database.fetch_one(query)
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already taken"
        )
    
    # Hash password
    data["password"] = await hash_password(data["password"])
    
    # Create user
    query = users.insert().values(**data)
    user_id = await database.execute(query)
    
    # Generate tokens
    tokens = await create_tokens(user_id)
    
    return response.json(tokens.dict(), status_code=201)

@app.post("/auth/login")
async def login(request: Request, response: Response):
    data = await request.json()
    
    # Find user
    query = users.select().where(users.c.username == data["username"])
    user = await database.fetch_one(query)
    
    if not user or not await verify_password(
        data["password"],
        user["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    # Generate tokens
    tokens = await create_tokens(user["id"])
    
    return response.json(tokens.dict())

@app.post("/auth/refresh")
async def refresh_token(request: Request, response: Response):
    data = await request.json()
    refresh_token = data.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=400,
            detail="Missing refresh token"
        )
    
    # Verify refresh token
    user_id = redis_client.get(f"refresh_token:{refresh_token}")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )
    
    # Generate new tokens
    tokens = await create_tokens(int(user_id))
    
    # Delete old refresh token
    redis_client.delete(f"refresh_token:{refresh_token}")
    
    return response.json(tokens.dict())

@app.post("/auth/logout")
@auth_middleware
async def logout(request: Request, response: Response):
    auth = request.headers["Authorization"]
    token = auth.split(" ")[1]
    
    # Add token to blacklist
    redis_client.setex(
        f"blacklist:{token}",
        300,  # 5 minutes (token expiry buffer)
        "1"
    )
    
    return response.json({"message": "Logged out"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
```

## Key Concepts Learned

- Authentication basics
- JWT tokens
- Password hashing
- Session management
- Role-based access control
- OAuth integration
- Token refresh
- Security best practices

## Additional Resources

- [JWT Documentation](https://jwt.io/)
- [OAuth 2.0 Guide](https://oauth.net/2/)
- [Security Best Practices](https://owasp.org/www-project-top-ten/)
- [Password Hashing](https://crackstation.net/hashing-security.htm)

## Homework

1. Implement social authentication:
   - Google
   - GitHub
   - Facebook

2. Add two-factor authentication:
   - TOTP
   - SMS
   - Email

3. Create an audit system:
   - Login attempts
   - Password changes
   - Permission changes

## Next Steps

Tomorrow, we'll explore WebSocket integration in [Day 9: WebSockets](../day09/index.md). 
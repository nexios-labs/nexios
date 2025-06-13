---
outline: deep
---

# API Examples

This guide provides comprehensive examples of building APIs with Nexios, covering common use cases and best practices.

::: warning API Design Best Practices
Before starting, consider these important aspects:
- Use consistent URL patterns
- Implement proper error handling
- Follow REST principles
- Consider API versioning
- Plan for scalability
- Document all endpoints
:::

## RESTful API

### Basic CRUD Operations

::: tip Model Design
When designing models:
- Use appropriate field types
- Add indexes for frequently queried fields
- Implement proper validation
- Consider relationships carefully
- Add timestamps for auditing
:::

::: code-group
```python [Models]
from nexios.db import Model, Column, types
from datetime import datetime

class User(Model):
    id = Column(types.Integer, primary_key=True)
    username = Column(types.String, unique=True)
    email = Column(types.String, unique=True)
    password = Column(types.String)
    is_active = Column(types.Boolean, default=True)
    created_at = Column(types.DateTime, default=datetime.utcnow)
    updated_at = Column(types.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    class Meta:
        indexes = [
            ('username',),
            ('email',)
        ]

class Post(Model):
    id = Column(types.Integer, primary_key=True)
    title = Column(types.String)
    content = Column(types.Text)
    user_id = Column(types.Integer, foreign_key="users.id")
    published = Column(types.Boolean, default=False)
    created_at = Column(types.DateTime, default=datetime.utcnow)
    updated_at = Column(types.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    class Meta:
        indexes = [
            ('user_id',),
            ('published',)
        ]
```

```python [Schemas]
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PostCreate(BaseModel):
    title: str
    content: str
    published: bool = False

    @validator('title')
    def title_length(cls, v):
        if len(v) < 3:
            raise ValueError('Title must be at least 3 characters')
        return v

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    published: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
```

```python [Routes]
from nexios import Router
from nexios.responses import JSONResponse
from nexios.exceptions import HTTPException
from nexios.middleware import RateLimitMiddleware
from typing import List

router = Router(prefix="/api/v1")

# Add rate limiting middleware
router.add_middleware(
    RateLimitMiddleware,
    rate_limit=100,  # requests
    time_window=60   # seconds
)

@router.get("/users")
async def list_users(request, response):
    """List all users with pagination.
    
    Query Parameters:
        page (int): Page number (default: 1)
        limit (int): Items per page (default: 10)
        search (str): Search term for username/email
        sort (str): Sort field (default: created_at)
        order (str): Sort order (asc/desc, default: desc)
    
    Returns:
        dict: Paginated list of users with metadata
    """
    page = int(request.query_params.get("page", 1))
    limit = int(request.query_params.get("limit", 10))
    search = request.query_params.get("search", "")
    sort = request.query_params.get("sort", "created_at")
    order = request.query_params.get("order", "desc")
    
    # Validate pagination parameters
    if page < 1 or limit < 1 or limit > 100:
        raise HTTPException(400, "Invalid pagination parameters")
    
    # Build query
    query = User.query
    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )
    
    # Apply sorting
    if hasattr(User, sort):
        sort_field = getattr(User, sort)
        if order == "desc":
            sort_field = sort_field.desc()
        query = query.order_by(sort_field)
    
    # Execute query with pagination
    users = await query.paginate(page, limit)
    total = await query.count()
    
    return response.json({
        "items": [UserResponse.from_orm(u) for u in users],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
        "has_next": page * limit < total,
        "has_prev": page > 1
    })

@router.post("/users")
async def create_user(request, response):
    """Create a new user.
    
    Request Body:
        username (str): Unique username
        email (str): Valid email address
        password (str): Secure password
    
    Returns:
        UserResponse: Created user data
    
    Raises:
        HTTPException: If username/email exists or validation fails
    """
    try:
        data = UserCreate(**await request.json())
    except ValueError as e:
        raise HTTPException(400, str(e))
    
    # Check if user exists
    if await User.query.filter_by(
        username=data.username
    ).exists():
        raise HTTPException(400, "Username taken")
    
    if await User.query.filter_by(
        email=data.email
    ).exists():
        raise HTTPException(400, "Email already registered")
    
    # Hash password
    data.password = hash_password(data.password)
    
    # Create user
    user = await User.create(**data.dict())
    return response.json(
        UserResponse.from_orm(user),
        status_code=201
    )

@router.get("/users/{user_id:int}")
async def get_user(request, response):
    """Get user by ID.
    
    Path Parameters:
        user_id (int): User ID
    
    Returns:
        UserResponse: User data
    
    Raises:
        HTTPException: If user not found
    """
    user = await User.get_or_404(
        request.path_params.user_id
    )
    return response.json(UserResponse.from_orm(user))

@router.put("/users/{user_id:int}")
async def update_user(request, response):
    """Update user by ID.
    
    Path Parameters:
        user_id (int): User ID
    
    Request Body:
        username (str, optional): New username
        email (str, optional): New email
        is_active (bool, optional): Active status
    
    Returns:
        UserResponse: Updated user data
    
    Raises:
        HTTPException: If user not found or validation fails
    """
    user = await User.get_or_404(
        request.path_params.user_id
    )
    
    try:
        data = UserUpdate(**await request.json())
    except ValueError as e:
        raise HTTPException(400, str(e))
    
    # Check unique constraints
    if data.username and data.username != user.username:
        if await User.query.filter_by(
            username=data.username
        ).exists():
            raise HTTPException(400, "Username taken")
    
    if data.email and data.email != user.email:
        if await User.query.filter_by(
            email=data.email
        ).exists():
            raise HTTPException(400, "Email already registered")
    
    # Update user
    await user.update(**data.dict(exclude_unset=True))
    return response.json(UserResponse.from_orm(user))

@router.delete("/users/{user_id:int}")
async def delete_user(request, response):
    """Delete user by ID.
    
    Path Parameters:
        user_id (int): User ID
    
    Returns:
        None
    
    Raises:
        HTTPException: If user not found
    """
    user = await User.get_or_404(
        request.path_params.user_id
    )
    await user.delete()
    return response.json(None, status_code=204)
```
:::

::: warning Database Operations
When working with databases:
- Always use transactions for multiple operations
- Implement proper error handling
- Use appropriate indexes
- Consider query performance
- Handle concurrent access
:::

## Authentication

### JWT Authentication

::: tip Security Best Practices
For JWT authentication:
- Use strong secret keys
- Implement token rotation
- Set appropriate expiration times
- Validate token claims
- Use secure cookie settings
:::

::: code-group
```python [Auth Handler]
from nexios.auth import JWTAuth
from nexios.exceptions import HTTPException
from datetime import datetime, timedelta
from typing import Optional

class AuthConfig:
    SECRET_KEY: str = "your-secret-key"  # Use environment variable in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE: timedelta = timedelta(minutes=30)
    REFRESH_TOKEN_EXPIRE: timedelta = timedelta(days=7)
    TOKEN_ROTATION_THRESHOLD: timedelta = timedelta(minutes=5)

auth = JWTAuth(
    secret_key=AuthConfig.SECRET_KEY,
    algorithm=AuthConfig.ALGORITHM,
    access_token_expire=AuthConfig.ACCESS_TOKEN_EXPIRE,
    refresh_token_expire=AuthConfig.REFRESH_TOKEN_EXPIRE
)

@router.post("/auth/login")
async def login(request, response):
    """Authenticate user and return tokens.
    
    Request Body:
        username (str): Username
        password (str): Password
    
    Returns:
        dict: Access and refresh tokens
    
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            raise HTTPException(400, "Username and password required")
        
        # Validate credentials
        user = await User.query.filter_by(
            username=username
        ).first()
        
        if not user or not verify_password(
            password, user.password
        ):
            raise HTTPException(
                401, "Invalid credentials"
            )
        
        # Generate tokens
        access_token = auth.create_access_token({
            "sub": str(user.id),
            "username": user.username,
            "exp": datetime.utcnow() + AuthConfig.ACCESS_TOKEN_EXPIRE
        })
        
        refresh_token = auth.create_refresh_token({
            "sub": str(user.id),
            "exp": datetime.utcnow() + AuthConfig.REFRESH_TOKEN_EXPIRE
        })
        
        # Set secure cookie for refresh token
        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=AuthConfig.REFRESH_TOKEN_EXPIRE.seconds
        )
        
        return response.json({
            "access_token": access_token,
            "token_type": "bearer"
        })
    except Exception as e:
        raise HTTPException(500, f"Authentication failed: {str(e)}")

@router.post("/auth/refresh")
async def refresh_token(request, response):
    """Refresh access token using refresh token.
    
    Headers:
        Authorization: Bearer <refresh_token>
    
    Returns:
        dict: New access token
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    refresh_token = request.headers.get("Authorization")
    if not refresh_token:
        raise HTTPException(401, "Missing token")
    
    try:
        # Extract token from Bearer
        token = refresh_token.split(" ")[1]
        
        # Decode and validate token
        payload = auth.decode_refresh_token(token)
        
        # Check if token is about to expire
        exp = datetime.fromtimestamp(payload["exp"])
        if exp - datetime.utcnow() < AuthConfig.TOKEN_ROTATION_THRESHOLD:
            # Generate new refresh token
            new_refresh_token = auth.create_refresh_token({
                "sub": payload["sub"],
                "exp": datetime.utcnow() + AuthConfig.REFRESH_TOKEN_EXPIRE
            })
            response.set_cookie(
                "refresh_token",
                new_refresh_token,
                httponly=True,
                secure=True,
                samesite="strict",
                max_age=AuthConfig.REFRESH_TOKEN_EXPIRE.seconds
            )
        
        # Generate new access token
        access_token = auth.create_access_token({
            "sub": payload["sub"],
            "exp": datetime.utcnow() + AuthConfig.ACCESS_TOKEN_EXPIRE
        })
        
        return response.json({
            "access_token": access_token,
            "token_type": "bearer"
        })
    except Exception as e:
        raise HTTPException(401, f"Invalid token: {str(e)}")

@router.post("/auth/logout")
async def logout(request, response):
    """Logout user by invalidating refresh token.
    
    Returns:
        dict: Success message
    """
    response.delete_cookie("refresh_token")
    return response.json({"message": "Successfully logged out"})
```

```python [Protected Routes]
from nexios import Depend
from typing import Optional

async def get_current_user(
    request,
    token: str = Depend(auth.get_token)
) -> User:
    """Get current user from token.
    
    Args:
        request: Request object
        token: JWT token from Authorization header
    
    Returns:
        User: Current user object
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        payload = auth.decode_access_token(token)
        user = await User.get(int(payload["sub"]))
        if not user:
            raise HTTPException(401, "User not found")
        if not user.is_active:
            raise HTTPException(401, "User is inactive")
        return user
    except Exception as e:
        raise HTTPException(401, f"Invalid token: {str(e)}")

@router.get("/users/me")
async def get_current_user_info(
    request,
    response,
    user: User = Depend(get_current_user)
):
    """Get current user information.
    
    Returns:
        UserResponse: Current user data
    """
    return response.json(UserResponse.from_orm(user))

@router.post("/users/me/change-password")
async def change_password(
    request,
    response,
    user: User = Depend(get_current_user)
):
    """Change user password.
    
    Request Body:
        old_password (str): Current password
        new_password (str): New password
    
    Returns:
        dict: Success message
    
    Raises:
        HTTPException: If old password is incorrect or new password is invalid
    """
    try:
        data = await request.json()
        old_password = data.get("old_password")
        new_password = data.get("new_password")
        
        if not old_password or not new_password:
            raise HTTPException(400, "Both old and new passwords are required")
        
        # Verify old password
        if not verify_password(old_password, user.password):
            raise HTTPException(400, "Incorrect password")
        
        # Validate new password
        if len(new_password) < 8:
            raise HTTPException(400, "New password must be at least 8 characters")
        
        # Update password
        user.password = hash_password(new_password)
        await user.save()
        
        # Invalidate all sessions
        await user.invalidate_sessions()
        
        return response.json({"message": "Password changed successfully"})
    except Exception as e:
        raise HTTPException(400, str(e))
```
:::

::: warning Security Considerations
When implementing authentication:
- Never store plain-text passwords
- Use secure password hashing (bcrypt, Argon2)
- Implement rate limiting for auth endpoints
- Use secure cookie settings
- Implement proper session management
- Consider 2FA for sensitive operations
:::

::: tip Error Handling
Implement proper error handling for:
- Invalid credentials
- Expired tokens
- Rate limiting
- Account lockout
- Session management
- Password policies
:::

## File Handling

### File Upload and Download

```python
from nexios.responses import FileResponse
from pathlib import Path

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/files/upload")
async def upload_file(request, response):
    """Upload a file."""
    files = await request.files()
    if not files:
        raise HTTPException(400, "No file uploaded")
    
    file = files["file"]
    if not file.filename:
        raise HTTPException(400, "No filename")
    
    # Save file
    file_path = UPLOAD_DIR / file.filename
    await file.save(file_path)
    
    return response.json({
        "filename": file.filename,
        "size": file_path.stat().st_size
    })

@router.get("/files/{filename}")
async def download_file(request, response):
    """Download a file."""
    filename = request.path_params.filename
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(404, "File not found")
    
    return FileResponse(
        file_path,
        filename=filename,
        media_type="application/octet-stream"
    )
```

## WebSocket

### Real-time Chat

```python
from nexios.websockets import WebSocket
from dataclasses import dataclass
from typing import Dict, Set
import json

@dataclass
class ChatRoom:
    name: str
    clients: Set[WebSocket]

class ChatServer:
    def __init__(self):
        self.rooms: Dict[str, ChatRoom] = {}
    
    def get_room(self, name: str) -> ChatRoom:
        if name not in self.rooms:
            self.rooms[name] = ChatRoom(name, set())
        return self.rooms[name]
    
    async def broadcast(
        self,
        room: ChatRoom,
        message: dict,
        exclude: WebSocket = None
    ):
        for client in room.clients:
            if client != exclude:
                await client.send_json(message)

chat_server = ChatServer()

@router.websocket("/ws/chat/{room_name}")
async def chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        # Get room
        room_name = websocket.path_params.room_name
        room = chat_server.get_room(room_name)
        room.clients.add(websocket)
        
        # Announce join
        await chat_server.broadcast(
            room,
            {
                "type": "system",
                "message": "User joined"
            },
            websocket
        )
        
        # Handle messages
        async for message in websocket.iter_json():
            await chat_server.broadcast(
                room,
                {
                    "type": "message",
                    "message": message["text"]
                },
                websocket
            )
    
    finally:
        room.clients.remove(websocket)
        await chat_server.broadcast(
            room,
            {
                "type": "system",
                "message": "User left"
            }
        )
```

## Background Tasks

### Task Queue Integration

```python
from nexios.background import BackgroundTask
from nexios.email import EmailSender

email_sender = EmailSender()

@router.post("/users")
async def create_user(request, response):
    data = UserCreate(**await request.json())
    user = await User.create(**data.dict())
    
    # Schedule welcome email
    background_task = BackgroundTask(
        email_sender.send_email,
        to=user.email,
        subject="Welcome!",
        template="welcome.html",
        context={"username": user.username}
    )
    
    return response.json(
        UserResponse.from_orm(user),
        status_code=201,
        background=background_task
    )
```

## Database Integration

### SQLAlchemy Integration

```python
from nexios.db import Database, Model
from sqlalchemy import select
from sqlalchemy.orm import joinedload

db = Database("postgresql+asyncpg://user:pass@localhost/db")

@router.get("/posts")
async def list_posts(request, response):
    async with db.session() as session:
        # Complex query with joins
        query = select(Post).options(
            joinedload(Post.user)
        ).order_by(
            Post.created_at.desc()
        )
        
        # Add filters
        if category := request.query_params.get("category"):
            query = query.filter(Post.category == category)
        
        # Pagination
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 10))
        offset = (page - 1) * limit
        
        # Execute query
        result = await session.execute(
            query.limit(limit).offset(offset)
        )
        posts = result.scalars().unique().all()
        
        # Get total
        total = await session.scalar(
            select(func.count()).select_from(Post)
        )
        
        return response.json({
            "items": [
                PostResponse.from_orm(post)
                for post in posts
            ],
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        })
```

## Error Handling

### Custom Error Handlers

```python
from nexios.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return response.json(
        {
            "error": exc.detail,
            "code": exc.status_code
        },
        status_code=exc.status_code
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return response.json(
        {
            "error": "Validation error",
            "details": exc.errors()
        },
        status_code=422
    )

@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request, exc):
    return response.json(
        {
            "error": "Database integrity error",
            "detail": str(exc.orig)
        },
        status_code=409
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.exception("Unhandled error")
    return response.json(
        {
            "error": "Internal server error",
            "detail": str(exc) if app.debug else None
        },
        status_code=500
    )
```

## Testing

### API Testing

```python
from nexios.testing import TestClient
import pytest

@pytest.fixture
async def client():
    app = create_test_app()
    async with TestClient(app) as client:
        yield client

async def test_create_user(client):
    response = await client.post(
        "/api/v1/users",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "password" not in data

async def test_login(client):
    # Create user
    await client.post(
        "/api/v1/users",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    
    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

async def test_protected_route(client):
    # Try without token
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401
    
    # Login and get token
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "password123"
        }
    )
    token = response.json()["access_token"]
    
    # Try with token
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

## OpenAPI Documentation

### API Documentation

```python
from nexios import NexiosApp
from nexios.openapi import OpenAPIConfig

app = NexiosApp(
    title="My API",
    version="1.0.0",
    description="A sample API",
    openapi_config=OpenAPIConfig(
        tags=[
            {
                "name": "users",
                "description": "User operations"
            },
            {
                "name": "auth",
                "description": "Authentication"
            }
        ],
        servers=[
            {
                "url": "https://api.example.com",
                "description": "Production server"
            },
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            }
        ],
        security_schemes={
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
    )
)

@router.get(
    "/users/{user_id}",
    tags=["users"],
    summary="Get user by ID",
    description="Retrieve a user by their ID",
    responses={
        200: {
            "description": "User found",
            "content": {
                "application/json": {
                    "schema": UserResponse.schema()
                }
            }
        },
        404: {
            "description": "User not found"
        }
    }
)
async def get_user(request, response):
    """Get user by ID."""
    user = await User.get_or_404(
        request.path_params.user_id
    )
    return response.json(UserResponse.from_orm(user))
```

## Best Practices

::: tip API Design
1. Use consistent naming conventions
2. Implement proper error handling
3. Add comprehensive documentation
4. Include input validation
5. Use appropriate HTTP methods
6. Implement rate limiting
7. Add authentication where needed
8. Use proper status codes
9. Include pagination for lists
10. Keep endpoints focused
:::

### Security Checklist

- [ ] Implement authentication
- [ ] Use HTTPS
- [ ] Validate input
- [ ] Rate limit requests
- [ ] Hash passwords
- [ ] Use secure headers
- [ ] Implement CORS
- [ ] Log security events
- [ ] Regular security updates
- [ ] API key management

### Performance Tips

1. Use async operations
2. Implement caching
3. Optimize database queries
4. Use connection pooling
5. Compress responses
6. Batch operations
7. Profile endpoints
8. Monitor performance
9. Use appropriate indexes
10. Optimize payload size

## More Information

- [Authentication Guide](/guide/authentication)
- [Database Guide](/guide/database)
- [WebSocket Guide](/guide/websockets/)
- [Testing Guide](/guide/testing)
- [Security Guide](/guide/security)

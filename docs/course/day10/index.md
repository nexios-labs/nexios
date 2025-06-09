# Day 10: Testing

Welcome to Day 10! Today we'll learn how to write and run tests for Nexios applications.

## Understanding Testing in Nexios

Testing covers:
- Unit tests
- Integration tests
- End-to-end tests
- Performance tests
- Security tests
- Coverage reporting

## Basic Test Setup

```python
import pytest
from nexios import NexiosApp
from nexios.http import Request, Response
from nexios.testing import Client

@pytest.fixture
def app():
    app = NexiosApp()
    
    @app.get("/")
    async def hello(request: Request, response: Response):
        return response.json({"message": "Hello, World!"})
    
    return app

@pytest.fixture
def client(app):
    return Client(app)

def test_hello_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}
```

## Testing Routes

```python
from nexios import NexiosApp
from nexios.http import Request, Response
import pytest
from nexios.testing import Client

# Sample application
app = NexiosApp()

@app.get("/users/{user_id}")
async def get_user(request: Request, response: Response, user_id: int):
    if user_id == 404:
        return response.json(
            {"error": "User not found"},
            status_code=404
        )
    return response.json({
        "id": user_id,
        "name": "Test User"
    })

@app.post("/users")
async def create_user(request: Request, response: Response):
    data = await request.json()
    if "name" not in data:
        return response.json(
            {"error": "Name is required"},
            status_code=400
        )
    return response.json(
        {"id": 1, **data},
        status_code=201
    )

# Tests
@pytest.fixture
def client():
    return Client(app)

def test_get_user_success(client):
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Test User"
    }

def test_get_user_not_found(client):
    response = client.get("/users/404")
    assert response.status_code == 404
    assert response.json() == {"error": "User not found"}

def test_create_user_success(client):
    response = client.post(
        "/users",
        json={"name": "New User"}
    )
    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "name": "New User"
    }

def test_create_user_validation_error(client):
    response = client.post("/users", json={})
    assert response.status_code == 400
    assert response.json() == {"error": "Name is required"}
```

## Testing Database Operations

```python
import pytest
from databases import Database
import sqlalchemy
from nexios import NexiosApp
from nexios.testing import Client

# Test database
TEST_DATABASE_URL = "sqlite:///./test.db"

# Models
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True)
)

# Application with database
app = NexiosApp()
database = Database(TEST_DATABASE_URL)
app.state.database = database

@app.on_event("startup")
async def startup():
    await database.connect()
    engine = sqlalchemy.create_engine(TEST_DATABASE_URL)
    metadata.create_all(engine)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/users")
async def create_user(request: Request, response: Response):
    data = await request.json()
    query = users.insert().values(**data)
    user_id = await database.execute(query)
    return response.json({"id": user_id, **data}, status_code=201)

# Tests
@pytest.fixture
async def test_database():
    await database.connect()
    
    # Create tables
    engine = sqlalchemy.create_engine(TEST_DATABASE_URL)
    metadata.create_all(engine)
    
    yield database
    
    # Cleanup
    metadata.drop_all(engine)
    await database.disconnect()

@pytest.fixture
def client(test_database):
    return Client(app)

async def test_create_user(client):
    response = client.post(
        "/users",
        json={
            "name": "Test User",
            "email": "test@example.com"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    
    # Verify in database
    query = users.select().where(users.c.id == data["id"])
    user = await database.fetch_one(query)
    assert user["name"] == "Test User"
    assert user["email"] == "test@example.com"
```

## Testing WebSockets

```python
import pytest
from nexios import NexiosApp, WebSocket
from nexios.testing import Client

app = NexiosApp()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_json()
    await websocket.send_json({"message": f"Received: {data['message']}"})
    await websocket.close()

@pytest.fixture
def client():
    return Client(app)

async def test_websocket(client):
    with client.websocket_connect("/ws") as websocket:
        websocket.send_json({"message": "Hello"})
        data = websocket.receive_json()
        assert data == {"message": "Received: Hello"}
```

## Testing Authentication

```python
import pytest
from nexios import NexiosApp
from nexios.http import Request, Response
import jwt

SECRET_KEY = "test-secret"

app = NexiosApp()

async def auth_middleware(request: Request, response: Response, call_next):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return response.json(
            {"error": "Missing token"},
            status_code=401
        )
    
    token = auth.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        request.state.user = payload
    except jwt.InvalidTokenError:
        return response.json(
            {"error": "Invalid token"},
            status_code=401
        )
    
    return await call_next()

@app.get("/protected", middleware=[auth_middleware])
async def protected_route(request: Request, response: Response):
    return response.json({
        "message": f"Hello, {request.state.user['sub']}"
    })

@pytest.fixture
def client():
    return Client(app)

@pytest.fixture
def auth_token():
    return jwt.encode(
        {"sub": "testuser"},
        SECRET_KEY,
        algorithm="HS256"
    )

def test_protected_route_with_token(client, auth_token):
    response = client.get(
        "/protected",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, testuser"}

def test_protected_route_without_token(client):
    response = client.get("/protected")
    assert response.status_code == 401
    assert response.json() == {"error": "Missing token"}

def test_protected_route_invalid_token(client):
    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer invalid"}
    )
    assert response.status_code == 401
    assert response.json() == {"error": "Invalid token"}
```

## Testing Middleware

```python
import pytest
from nexios import NexiosApp
from nexios.http import Request, Response
import time

app = NexiosApp()

async def timing_middleware(request: Request, response: Response, call_next):
    start_time = time.time()
    response = await call_next()
    duration = time.time() - start_time
    response.headers["X-Process-Time"] = f"{duration:.4f}"
    return response

@app.get("/test", middleware=[timing_middleware])
async def test_route(request: Request, response: Response):
    return response.json({"message": "Hello"})

@pytest.fixture
def client():
    return Client(app)

def test_timing_middleware(client):
    response = client.get("/test")
    assert response.status_code == 200
    assert "X-Process-Time" in response.headers
    duration = float(response.headers["X-Process-Time"])
    assert duration >= 0
```

## Performance Testing

```python
import pytest
from nexios import NexiosApp
from nexios.http import Request, Response
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

app = NexiosApp()

@app.get("/fast")
async def fast_route(request: Request, response: Response):
    return response.json({"message": "Fast response"})

@app.get("/slow")
async def slow_route(request: Request, response: Response):
    await asyncio.sleep(0.1)
    return response.json({"message": "Slow response"})

@pytest.fixture
def client():
    return Client(app)

def test_route_performance(client):
    # Test fast route
    start_time = time.time()
    response = client.get("/fast")
    duration = time.time() - start_time
    
    assert response.status_code == 200
    assert duration < 0.01  # Should respond in less than 10ms
    
    # Test slow route
    start_time = time.time()
    response = client.get("/slow")
    duration = time.time() - start_time
    
    assert response.status_code == 200
    assert 0.1 <= duration <= 0.15  # Should take about 100ms

def test_concurrent_requests(client):
    def make_request():
        return client.get("/fast")
    
    # Make 100 concurrent requests
    with ThreadPoolExecutor(max_workers=10) as executor:
        start_time = time.time()
        responses = list(executor.map(make_request, range(100)))
        duration = time.time() - start_time
    
    # Verify responses
    assert all(r.status_code == 200 for r in responses)
    assert duration < 1.0  # Should handle 100 requests in less than 1 second
```

## Mini-Project: Testing a Blog API

```python
import pytest
from nexios import NexiosApp
from nexios.http import Request, Response
from nexios.testing import Client
from databases import Database
import sqlalchemy
from datetime import datetime
import jwt

# Database setup
TEST_DATABASE_URL = "sqlite:///./test_blog.db"
database = Database(TEST_DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Models
users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String, unique=True),
    sqlalchemy.Column("password", sqlalchemy.String)
)

posts = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String),
    sqlalchemy.Column("content", sqlalchemy.String),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id")),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, default=datetime.utcnow)
)

# Application
app = NexiosApp()
app.state.database = database

# Auth middleware
async def auth_middleware(request: Request, response: Response, call_next):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return response.json(
            {"error": "Missing token"},
            status_code=401
        )
    
    try:
        token = auth.split(" ")[1]
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
        request.state.user = payload
    except jwt.InvalidTokenError:
        return response.json(
            {"error": "Invalid token"},
            status_code=401
        )
    
    return await call_next()

# Routes
@app.post("/users")
async def create_user(request: Request, response: Response):
    data = await request.json()
    query = users.insert().values(**data)
    user_id = await database.execute(query)
    
    token = jwt.encode(
        {"sub": user_id, "username": data["username"]},
        "secret",
        algorithm="HS256"
    )
    
    return response.json({
        "id": user_id,
        "username": data["username"],
        "token": token
    }, status_code=201)

@app.post("/posts", middleware=[auth_middleware])
async def create_post(request: Request, response: Response):
    data = await request.json()
    data["user_id"] = request.state.user["sub"]
    
    query = posts.insert().values(**data)
    post_id = await database.execute(query)
    
    return response.json({
        "id": post_id,
        **data
    }, status_code=201)

@app.get("/posts")
async def list_posts(request: Request, response: Response):
    query = posts.select().order_by(posts.c.created_at.desc())
    results = await database.fetch_all(query)
    return response.json([dict(r) for r in results])

@app.get("/posts/{post_id}")
async def get_post(request: Request, response: Response, post_id: int):
    query = posts.select().where(posts.c.id == post_id)
    post = await database.fetch_one(query)
    
    if not post:
        return response.json(
            {"error": "Post not found"},
            status_code=404
        )
    
    return response.json(dict(post))

# Tests
@pytest.fixture
async def test_database():
    await database.connect()
    
    engine = sqlalchemy.create_engine(TEST_DATABASE_URL)
    metadata.create_all(engine)
    
    yield database
    
    metadata.drop_all(engine)
    await database.disconnect()

@pytest.fixture
def client(test_database):
    return Client(app)

@pytest.fixture
async def test_user(client):
    response = client.post(
        "/users",
        json={
            "username": "testuser",
            "password": "password"
        }
    )
    return response.json()

async def test_create_user(client):
    response = client.post(
        "/users",
        json={
            "username": "newuser",
            "password": "password"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert "token" in data

async def test_create_post(client, test_user):
    response = client.post(
        "/posts",
        json={
            "title": "Test Post",
            "content": "Test Content"
        },
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Post"
    assert data["content"] == "Test Content"
    assert data["user_id"] == test_user["id"]

async def test_list_posts(client, test_user):
    # Create test posts
    for i in range(3):
        client.post(
            "/posts",
            json={
                "title": f"Post {i}",
                "content": f"Content {i}"
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
    
    response = client.get("/posts")
    assert response.status_code == 200
    posts = response.json()
    assert len(posts) == 3
    assert posts[0]["title"] == "Post 2"  # Most recent first

async def test_get_post(client, test_user):
    # Create post
    post_response = client.post(
        "/posts",
        json={
            "title": "Test Post",
            "content": "Test Content"
        },
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    post_id = post_response.json()["id"]
    
    # Get post
    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 200
    post = response.json()
    assert post["title"] == "Test Post"
    assert post["content"] == "Test Content"

async def test_get_nonexistent_post(client):
    response = client.get("/posts/999")
    assert response.status_code == 404
    assert response.json() == {"error": "Post not found"}

async def test_create_post_without_auth(client):
    response = client.post(
        "/posts",
        json={
            "title": "Test Post",
            "content": "Test Content"
        }
    )
    assert response.status_code == 401
    assert response.json() == {"error": "Missing token"}

if __name__ == "__main__":
    pytest.main([__file__])
```

## Key Concepts Learned

- Test setup and fixtures
- Route testing
- Database testing
- WebSocket testing
- Authentication testing
- Middleware testing
- Performance testing
- Coverage reporting

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Code Coverage](https://coverage.readthedocs.io/)
- [Performance Testing](https://locust.io/)

## Homework

1. Create a test suite for an e-commerce API:
   - Product management
   - Shopping cart
   - Order processing
   - User accounts

2. Implement performance tests:
   - Load testing
   - Stress testing
   - Endurance testing
   - Spike testing

3. Build a CI/CD pipeline:
   - Automated testing
   - Code coverage
   - Performance benchmarks
   - Security scans

## Next Steps

Tomorrow, we'll explore deployment in [Day 11: Deployment](../day11/index.md).

# 🚀 Day 10: API Key Authentication

## Creating API Keys

Implementing API key generation and management:

```python
from nexios import get_application
from nexios.security import APIKeyAuth, generate_api_key
from nexios.http import Request, Response
from datetime import datetime, timedelta
import uuid

app = get_application()

# Configure API Key authentication
api_auth = APIKeyAuth(
    prefix="nx",  # API keys will start with "nx_"
    key_length=32  # Length of the random part
)

app.auth_backend = api_auth

class APIKeyManager:
    def __init__(self):
        self.db = app.db  # Your database connection
    
    async def create_api_key(
        self,
        user_id: str,
        name: str,
        expires_in: timedelta = None
    ) -> dict:
        # Generate new API key
        api_key = await generate_api_key()
        key_id = str(uuid.uuid4())
        
        # Calculate expiration
        expires_at = None
        if expires_in:
            expires_at = datetime.now() + expires_in
        
        # Store key details (store hash, not the key itself)
        key_hash = await api_auth.hash_key(api_key)
        await self.db.api_keys.insert_one({
            "id": key_id,
            "user_id": user_id,
            "name": name,
            "key_hash": key_hash,
            "created_at": datetime.now(),
            "expires_at": expires_at,
            "last_used": None
        })
        
        # Return the key (only time it's visible)
        return {
            "id": key_id,
            "key": api_key,
            "name": name,
            "expires_at": expires_at
        }
    
    async def list_api_keys(self, user_id: str) -> list:
        keys = await self.db.api_keys.find(
            {"user_id": user_id}
        ).to_list(None)
        
        return [{
            "id": key["id"],
            "name": key["name"],
            "created_at": key["created_at"],
            "expires_at": key["expires_at"],
            "last_used": key["last_used"]
        } for key in keys]
    
    async def revoke_api_key(
        self,
        user_id: str,
        key_id: str
    ) -> bool:
        result = await self.db.api_keys.delete_one({
            "id": key_id,
            "user_id": user_id
        })
        return result.deleted_count > 0

# Initialize manager
key_manager = APIKeyManager()

@app.post("/api-keys")
@requires_auth  # Regular user authentication
async def create_key(request: Request):
    data = await request.json()
    user_id = request.user.id
    
    # Create new API key
    key = await key_manager.create_api_key(
        user_id=user_id,
        name=data["name"],
        expires_in=timedelta(days=data.get("expires_in_days", 365))
    )
    
    return key

@app.get("/api-keys")
@requires_auth
async def list_keys(request: Request):
    keys = await key_manager.list_api_keys(request.user.id)
    return {"api_keys": keys}

@app.delete("/api-keys/{key_id}")
@requires_auth
async def revoke_key(request: Request, key_id: str):
    success = await key_manager.revoke_api_key(
        request.user.id,
        key_id
    )
    
    if not success:
        return Response(
            content={"error": "API key not found"},
            status_code=404
        )
    
    return {"message": "API key revoked"}
```

## Validating API Keys

Implementing API key validation:

```python
from nexios.security import APIKeyValidator
from typing import Optional

class APIKeyValidator:
    def __init__(self):
        self.db = app.db
    
    async def validate_key(self, api_key: str) -> Optional[dict]:
        # Hash the provided key
        key_hash = await api_auth.hash_key(api_key)
        
        # Find key in database
        key = await self.db.api_keys.find_one({
            "key_hash": key_hash
        })
        
        if not key:
            return None
        
        # Check expiration
        if key["expires_at"] and datetime.now() > key["expires_at"]:
            return None
        
        # Update last used timestamp
        await self.db.api_keys.update_one(
            {"id": key["id"]},
            {"$set": {"last_used": datetime.now()}}
        )
        
        # Get associated user
        user = await self.db.users.find_one({
            "id": key["user_id"]
        })
        
        return {
            "key_id": key["id"],
            "user": user,
            "name": key["name"]
        }

# Initialize validator
key_validator = APIKeyValidator()

@app.middleware("http")
async def validate_api_key(request: Request, call_next):
    # Skip validation for auth routes
    if request.url.path.startswith("/auth"):
        return await call_next(request)
    
    # Check header first
    api_key = request.headers.get("X-API-Key")
    
    # Then check query parameter
    if not api_key:
        api_key = request.query_params.get("api_key")
    
    if not api_key:
        return Response(
            content={"error": "API key required"},
            status_code=401
        )
    
    # Validate key
    key_info = await key_validator.validate_key(api_key)
    if not key_info:
        return Response(
            content={"error": "Invalid API key"},
            status_code=401
        )
    
    # Add key info to request
    request.state.api_key = key_info
    request.user = key_info["user"]
    
    return await call_next(request)
```

## Using API Keys

Examples of using API keys in requests:

```python
# Using in header
@app.get("/api/data")
async def get_data(request: Request):
    # API key already validated by middleware
    user = request.user
    key_info = request.state.api_key
    
    return {
        "data": "Your protected data",
        "user": user.username,
        "key_name": key_info["name"]
    }

# Rate limiting by API key
from nexios.cache import RedisCache
from nexios.exceptions import RateLimitExceeded

class APIKeyRateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.cache = RedisCache()
        self.rate_limit = requests_per_minute
    
    async def check_rate_limit(self, key_id: str) -> bool:
        current = await self.cache.incr(f"rate:{key_id}")
        
        if current == 1:
            await self.cache.expire(f"rate:{key_id}", 60)
        
        return current <= self.rate_limit

# Rate limiting middleware
rate_limiter = APIKeyRateLimiter(requests_per_minute=60)

@app.middleware("http")
async def rate_limit_by_key(request: Request, call_next):
    if hasattr(request.state, "api_key"):
        key_id = request.state.api_key["key_id"]
        
        if not await rate_limiter.check_rate_limit(key_id):
            return Response(
                content={"error": "Rate limit exceeded"},
                status_code=429
            )
    
    return await call_next(request)
```

## 📝 Practice Exercise

1. Build an API key management system:
   - Key generation with custom prefixes
   - Expiration dates
   - Usage tracking
   - Rate limiting

2. Implement security features:
   - Key rotation
   - Permissions per key
   - IP restrictions
   - Usage analytics

3. Create a key management UI:
   - List active keys
   - Create/revoke keys
   - View usage stats
   - Set permissions

## 📚 Additional Resources
- [API Key Best Practices](https://nexios.dev/guide/api-keys)
- [Rate Limiting](https://nexios.dev/guide/rate-limiting)
- [Security Guidelines](https://nexios.dev/guide/security)
- [Redis Integration](https://nexios.dev/guide/redis)

## 🎯 Next Steps
Tomorrow in [Day 11: Request Validation](../day11/index.md), we'll explore:
- Input validation
- Schema validation
- Custom validators
- Error handling 
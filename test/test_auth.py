from nexios.auth import AuthenticationMiddleware, JWTAuthBackend, create_jwt, auth, has_permission, BaseUser
from nexios.auth.backends.base import AuthenticationBackend
from nexios.auth.model import AuthResult
import pytest

from nexios.application import NexiosApp
from nexios.auth.backends.jwt import decode_jwt
from nexios.auth.users.simple import SimpleUser, UnauthenticatedUser
from nexios.config import MakeConfig, set_config
from nexios.http import Request, Response
from nexios.testing import Client
from datetime import datetime,timedelta,timezone

# Test User Model for authentication
class TestUser(BaseUser):
    def __init__(self, user_id: str, username: str, roles: list = None):
        self.user_id = user_id
        self.username = username
        self.roles = roles or []
        self._is_authenticated = True

    @property
    def is_authenticated(self) -> bool:
        return self._is_authenticated

    @property
    def display_name(self) -> str:
        return self.username

    @property
    def identity(self) -> str:
        return self.user_id

    def has_permission(self, permission: str) -> bool:
       
        return permission in self.roles

    @classmethod
    async def load_user(cls, identity: str):
        # Mock user loading for tests
        users_db = {
            "1": cls("1", "testuser", ["read", "write"]),
            "2": cls("2", "admin", ["read", "write", "admin"]),
        }
        return users_db.get(str(identity))


@pytest.fixture
async def test_client():
    config = MakeConfig({"secret_key": "1234"})
    set_config(config)
    app = NexiosApp()
    async with Client(app) as client:
        yield client, app


@pytest.fixture
def mock_user():
    return {"id": "1", "username": "testuser"}


@pytest.fixture
def valid_token(mock_user):
    return create_jwt(mock_user)


@pytest.fixture
def expired_token(mock_user):
    return create_jwt({"exp": 1, **mock_user})


async def test_jwt_auth_success(test_client, valid_token):
    client, app = test_client

    # Setup authentication middleware with new API
    jwt_backend = JWTAuthBackend()
    app.add_middleware(AuthenticationMiddleware(TestUser, jwt_backend))

    @app.get("/protected")
    @auth("jwt")
    async def protected_route(req: Request, res: Response):
        return res.json({"user": req.user})

    response = await client.get(
        "/protected", headers={"Authorization": f"Bearer {valid_token}"}
    )

    assert response.status_code == 200
    assert response.json()["user"] is not None


async def test_jwt_auth_missing_header(test_client, mock_user):
    client, app = test_client

    # Setup authentication middleware with new API
    jwt_backend = JWTAuthBackend()
    app.add_middleware(AuthenticationMiddleware(TestUser, jwt_backend))

    @app.get("/protected")
    @auth("jwt")
    async def protected_route(req: Request, res: Response):
        return res.json({"user": req.user})

    # Test without auth header
    response = await client.get("/protected")

    assert response.status_code == 401


async def test_jwt_auth_invalid_token(test_client, mock_user):
    client, app = test_client

    # Setup authentication middleware with new API
    jwt_backend = JWTAuthBackend()
    app.add_middleware(AuthenticationMiddleware(TestUser, jwt_backend))

    @app.get("/protected")
    @auth("jwt")
    async def protected_route(req: Request, res: Response):
        return res.json({"user": req.user})

    # Test with invalid token
    response = await client.get(
        "/protected", headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401


async def test_jwt_auth_expired_token(test_client, mock_user, expired_token):
    client, app = test_client

    # Setup authentication middleware with new API
    jwt_backend = JWTAuthBackend()
    app.add_middleware(AuthenticationMiddleware(TestUser, jwt_backend))

    @app.get("/protected")
    @auth("jwt")
    async def protected_route(req: Request, res: Response):
        return res.json({"user": req.user})

    # Test with expired token
    response = await client.get(
        "/protected", headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401


async def test_jwt_auth_validation_failure(test_client, valid_token):
    client, app = test_client

    # Setup authentication middleware with new API
    jwt_backend = JWTAuthBackend()
    app.add_middleware(AuthenticationMiddleware(TestUser, jwt_backend))

    @app.get("/protected")
    @auth("jwt")
    async def protected_route(req: Request, res: Response):
        return res.json({"user": req.user})

    response = await client.get(
        "/protected", headers={"Authorization": "Bearer"}
    )

    # Should return 401 because user identity "nonexistent" is not found
    assert response.status_code == 401


async def test_jwt_auth_with_auth_decorator(test_client, mock_user, valid_token):
    client, app = test_client

    # Setup authentication middleware with new API
    jwt_backend = JWTAuthBackend()
    app.add_middleware(AuthenticationMiddleware(TestUser, jwt_backend))

    @app.get("/protected-decorator")
    @auth("jwt")
    async def protected_route(req: Request, res: Response):
        return res.json({"user": req.user})

    # Test with valid token
    response = await client.get(
        "/protected-decorator", headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert response.status_code == 200
    assert response.json()["user"] is not None

    # Test without token (should be unauthorized)
    response = await client.get("/protected-decorator")
    assert response.status_code == 401


def test_create_jwt():
    from jwt import decode as jwt_decode

    payload = {"user_id": 1, "username": "test"}
    token = create_jwt(payload, "test_secret")

    decoded = jwt_decode(token, "test_secret", algorithms=["HS256"])
    assert decoded["user_id"] == 1
    assert decoded["username"] == "test"


def test_decode_jwt_valid():
    payload = {"user_id": 1, "username": "test"}
    token = create_jwt(payload, "test_secret", algorithm="HS256")

    decoded = decode_jwt(token, "test_secret", ["HS256"])
    assert decoded["user_id"] == 1
    assert decoded["username"] == "test"


def test_decode_jwt_expired():
    payload = {"user_id": 1, "username": "test", "exp": 1}  # Expired in 1970
    token = create_jwt(payload, "test_secret", algorithm="HS256")

    with pytest.raises(ValueError, match="Token has expired"):
        decode_jwt(token, "test_secret", ["HS256"])


def test_decode_jwt_invalid():
    with pytest.raises(ValueError, match="Invalid token"):
        decode_jwt("invalid.token", "test_secret", ["HS256"])


async def test_custom_auth_backend(test_client):
    client, app = test_client

    class CustomAuthBackend(AuthenticationBackend):
        async def authenticate(self, request: Request, response: Response):
            if request.headers.get("X-Custom-Auth") == "valid":
                return AuthResult(success=True, identity="123456789", scope="X-auth")
            return AuthResult(success=False, identity="", scope="X-auth")


    app.add_middleware(AuthenticationMiddleware(backend=CustomAuthBackend(),user_model=SimpleUser))

    @app.get("/custom-protected")
    @auth("X-auth")
    async def custom_protected(req: Request, res: Response):
        return res.json({"user_id": req.user.identity, "username": req.user.username})

    # Test with valid custom auth
    response = await client.get("/custom-protected", headers={"X-Custom-Auth": "valid"})
    assert response.status_code == 200
    assert response.json()["user_id"] == "123456789"

    response = await client.get("/custom-protected")
    assert response.status_code == 401


async def test_has_permission_decorator(test_client):
    """Test the has_permission decorator with TestUser."""

    app = NexiosApp()
    client = Client(app)

    # Setup authentication middleware with new API
    class DummuMiddleware(AuthenticationMiddleware):

        def __init__(self):
            super().__init__(TestUser,AuthenticationBackend())
        async def process_request(self, request: Request, response: Response,  call_next):
            
            request.scope["user"] = TestUser("1", "testuser", ["read","write"])
            return await call_next()
    app.add_middleware(DummuMiddleware())

    @app.get("/protected-route")
    @has_permission("read")
    async def protected_route(request, response):
        return {"message": "Access granted"}

    # Create a valid token for user "1" who has "read" permission
    token = create_jwt({"id": "1", "username": "testuser","exp": datetime.now(timezone.utc) + timedelta(days=1)})

    # Test with user having the required permission
    response = await client.get("/protected-route", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert (response.json()) == {"message": "Access granted"}

    # Test with user missing required permission (user "2" doesn't have "admin" permission)
    @app.get("/admin-route")
    @has_permission("admin")
    async def admin_route(request, response):
        return {"message": "Admin access"}

    # User "2" doesn't have "admin" permission according to our TestUser.load_user
    response = await client.get("/admin-route", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403  # Forbidden

    # Test with multiple required permissions (all must be present)
    @app.get("/edit-route")
    @has_permission(["read", "write"])
    async def edit_route(request, response):
        return {"message": "Edit access"}

    response = await client.get("/edit-route", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert (response.json()) == {"message": "Edit access"}

    # Test with no required permissions (should allow any authenticated user)
    @app.get("/any-auth-route")
    @has_permission()
    async def any_auth_route(request, response):
        return {"message": "Any authenticated access"}

    response = await client.get("/any-auth-route", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert (response.json()) == {"message": "Any authenticated access"}
 
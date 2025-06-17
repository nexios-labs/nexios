from typing import Tuple

import pytest

from nexios import NexiosApp, get_application
from nexios.config import MakeConfig
from nexios.http import Request, Response
from nexios.session.file import FileSessionManager
from nexios.session.middleware import SessionMiddleware
from nexios.session.signed_cookies import SignedSessionManager
from nexios.testing import Client


# Fixtures for different session configurations
@pytest.fixture
async def file_session_client(tmp_path) -> Tuple[Client, NexiosApp]:
    """Client with file-based session configuration"""
    app = get_application(
        MakeConfig(
            {
                "secret_key": "file_session_secret",
                "session": {
                    "session_cookie_name": "file_session",
                    "session_permanent": True,
                    "session_expiration_time": 30,
                    "manager": FileSessionManager,
                },
                "session_file_name": str(tmp_path / "sessions"),
                "SESSION_FILE_STORAGE_PATH": str(tmp_path / "sessions"),
            }
        )
    )
    app.add_middleware(SessionMiddleware())
    async with Client(app) as client:
        yield client, app


@pytest.fixture
async def signed_session_client() -> Tuple[Client, NexiosApp]:
    """Client with signed cookie session configuration"""
    app = get_application(
        MakeConfig(
            {
                "secret_key": "signed_session_secret",
                "session": {
                    "session_cookie_name": "signed_session",
                    "session_permanent": True,
                    "session_expiration_time": 30,
                    "manager": SignedSessionManager,
                },
            }
        )
    )
    async with Client(app) as client:
        yield client, app


# # Test session middleware
async def test_session_middleware_initialization(
    file_session_client: Tuple[Client, NexiosApp],
):
    client, app = file_session_client

    @app.get("/test-session")
    async def test_session(req: Request, res: Response):

        req.session["key"] = "value"
        return res.text("OK")

    response = await client.get("/test-session")
    assert response.status_code == 200
    assert response.text == "OK"


async def test_session_middleware_no_secret_key():
    app = get_application(MakeConfig({"secret_key": None}))

    @app.get("/test-session")
    async def test_session(req: Request, res: Response):
        try:
            req.session["key"] = "value"
        except AssertionError:
            return res.text("No session", status_code=512)
        return res.text("OK")

    async with Client(app) as client:
        response = await client.get("/test-session")
        assert response.status_code == 512
        assert response.text == "No session"


# # Test file session manager
# async def test_file_session_operations(
#     file_session_client: Tuple[Client, NexiosApp], tmp_path
# ):
#     client, app = file_session_client

#     @app.get("/set-session")
#     async def set_session(req: Request, res: Response):
#         req.session["test_key"] = "test_value"
#         req.session["user"] = {"id": 1, "name": "Test"}
#         return res.text("Session set")

#     @app.get("/get-session")
#     async def get_session(req: Request, res: Response):
#         return res.json(
#             {"test_key": req.session.get("test_key"), "user": req.session.get("user")}
#         )

#     @app.get("/delete-session")
#     async def delete_session(req: Request, res: Response):
#         del req.session["test_key"]
#         return res.text("Session deleted")

#     @app.get("/clear-session")
#     async def clear_session(req: Request, res: Response):
#         req.session.clear()
#         return res.text("Session cleared")

#     #     # Set session
#     response = await client.get("/set-session")
#     assert response.status_code == 200

#     # Verify cookie was set
#     assert "file_session" in response.cookies

#     session_id = response.cookies["file_session"]

#     # # Verify session file was created
#     session_file = tmp_path / "sessions" / f"{session_id}.json"
#     assert session_file.exists()

#     response = await client.get("/get-session")
#     assert response.status_code == 200
#     # assert response.json() == {
#     #     "test_key": "test_value",
#     #     "user": {"id": 1, "name": "Test"},
#     # }

#     # Delete item from session
#     response = await client.get("/delete-session")
#     # assert response.status_code == 200

#     # Verify deletion
#     response = await client.get("/get-session")
#     # assert response.json()["test_key"] is None

#     # Clear session
#     response = await client.get("/clear-session")
#     # assert response.status_code == 200
#     # assert not session_file.exists()


# # Test signed cookie session manager
# async def test_signed_session_operations(signed_session_client: Tuple[Client, NexiosApp]):
#     client, app = signed_session_client

#     @app.get("/set-session")
#     async def set_session(req: Request, res: Response):
#         req.session["test_key"] = "test_value"
#         req.session["user"] = {"id": 1, "name": "Test"}
#         return res.text("Session set")

#     @app.get("/get-session")
#     async def get_session(req: Request, res: Response):
#         return res.json({
#             "test_key": req.session.get("test_key"),
#             "user": req.session.get("user")
#         })

#     # Set session
#     response = await client.get("/set-session")
#     assert response.status_code == 200

#     # Verify cookie was set
#     assert "signed_session" in response.cookies
#     session_cookie = response.cookies["signed_session"]

#     # Get session
#     response = await client.get("/get-session")
#     assert response.status_code == 200
#     assert response.json() == {
#         "test_key": "test_value",
#         "user": {"id": 1, "name": "Test"}
#     }

#     # Test with invalid cookie
#     client.cookies["signed_session"] = "invalid.token"
#     response = await client.get("/get-session")
#     assert response.status_code == 200
#     assert response.json() == {
#         "test_key": None,
#         "user": None
#     }

# # Test session expiration
# async def test_session_expiration(file_session_client: Tuple[Client, NexiosApp]):
#     client, app = file_session_client

#     @app.get("/set-expiring-session")
#     async def set_expiring_session(req: Request, res: Response):
#         req.session["temp"] = "data"
#         # Set expiration to 1 second from now
#         req.session._session_cache["__expires"] = (
#             datetime.now(timezone.utc) + timedelta(seconds=1)
#         ).isoformat()
#         return res.text("Session set")

#     @app.get("/check-expired")
#     async def check_expired(req: Request, res: Response):
#         return res.json({"expired": req.session.has_expired()})

#     # Set session
#     response = await client.get("/set-expiring-session")
#     assert response.status_code == 200

#     # Check immediately - should not be expired
#     response = await client.get("/check-expired")
#     assert response.status_code == 200
#     assert response.json()["expired"] is False

#     # Wait for expiration
#     import time
#     time.sleep(2)

#     # Check again - should be expired
#     response = await client.get("/check-expired")
#     assert response.status_code == 200
#     assert response.json()["expired"] is True

# # Test session cookie settings
# async def test_session_cookie_settings(file_session_client: Tuple[Client, NexiosApp]):
#     client, app = file_session_client

#     # Update cookie settings
#     app.config.session.session_cookie_httponly = True
#     app.config.session.session_cookie_secure = True
#     app.config.session.session_cookie_samesite = "lax"
#     app.config.session.session_cookie_path = "/test"
#     app.config.session.session_cookie_domain = "example.com"

#     @app.get("/set-cookie-settings")
#     async def set_cookie_settings(req: Request, res: Response):
#         req.session["test"] = "value"
#         return res.text("OK")

#     response = await client.get("/set-cookie-settings")
#     assert response.status_code == 200


#     cookie = response.cookies["file_session"]
#     assert cookie["httponly"] is True
#     assert cookie["secure"] is True
#     assert cookie["samesite"] == "lax"
#     assert cookie["path"] == "/test"
#     assert cookie["domain"] == "example.com"
# async def test_signed_session_operations(
#     signed_session_client: Tuple[Client, NexiosApp],
# ):
#     client, app = signed_session_client

#     @app.get("/set-session")
#     async def set_session(req: Request, res: Response):
#         req.session["test_key"] = "test_value"
#         req.session["user"] = {"id": 1, "name": "Test"}
#         return res.text("Session set")

#     @app.get("/get-session")
#     async def get_session(req: Request, res: Response):
#         return res.json(
#             {"test_key": req.session.get("test_key"), "user": req.session.get("user")}
#         )

#     # Set session
#     response = await client.get("/set-session")
#     assert response.status_code == 200

#     # Verify cookie was set
#     assert "signed_session" in response.cookies
#     session_cookie = response.cookies["signed_session"]

#     # Get session
#     response = await client.get("/get-session")
#     assert response.status_code == 200
#     assert response.json() == {
#         "test_key": "test_value",
#         "user": {"id": 1, "name": "Test"},
#     }

#     # Test with invalid cookie
#     client.cookies["signed_session"] = "invalid.token"
#     response = await client.get("/get-session")
#     assert response.status_code == 200
#     assert response.json() == {"test_key": None, "user": None}


# Test session cookie settings
async def test_session_cookie_settings(file_session_client: Tuple[Client, NexiosApp]):
    client, app = file_session_client

    # Update cookie settings
    app.config.session.session_cookie_httponly = True
    app.config.session.session_permanent = False

    @app.get("/set-cookie-settings")
    async def set_cookie_settings(req: Request, res: Response):
        req.session["test"] = "value"
        return res.text("OK")

    response = await client.get("/set-cookie-settings")
    assert response.status_code == 200

    response.cookies["file_session"]
    # assert cookie["httponly"] is True
    # assert cookie["secure"] is True
    # assert cookie["samesite"] == "lax"
    # assert cookie["path"] == "/test"
    # assert cookie["domain"] == "example.com"


# # Test session middleware with custom manager
# async def test_custom_session_manager(file_session_client: Tuple[Client, NexiosApp]):
#     # Define a simple in-memory session manager for testing
#     class MemorySessionManager(BaseSessionInterface):
#         _store: Dict[str, Dict[str, Any]] = {}

#         async def load(self):
#             self._session_cache = self._store.get(self.session_key, {})

#         async def save(self):
#             self._store[self.session_key] = self._session_cache

#     # app = get_application(MakeConfig({
#     #     "secret_key": "custom_session_secret",
#     #     "session": {
#     #         "manager": MemorySessionManager,
#     #         "session_cookie_name": "custom_session"
#     #     }
#     # }))
#     client, app = file_session_client
#     app.config.session.manager = MemorySessionManager
#     app.config.session.session_cookie_name = "custom"

#     @app.get("/test-custom-manager")
#     async def test_custom_manager(req: Request, res: Response):

#         if "count" not in req.session:
#             req.session["count"] = 1
#         else:

#             req.session["count"] += 1
#         return res.json({"count": req.session["count"]})

#     async with Client(app) as client:
#         # First request
#         response = await client.get("/test-custom-manager")
#         assert response.status_code == 200
#         assert response.json()["count"] == 1

#         # Second request
#         response = await client.get("/test-custom-manager")
#         assert response.status_code == 200
#         assert response.json()["count"] == 2

#         # New client should start fresh
#     async with Client(app) as new_client:
#         response = await new_client.get("/test-custom-manager")
#         assert response.status_code == 200
#         assert response.json()["count"] == 1

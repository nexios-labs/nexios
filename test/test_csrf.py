import re
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from itsdangerous import BadSignature

from nexios.config import MakeConfig as Config
from nexios.http import Request, Response
from nexios.middleware.csrf import CSRFMiddleware

# Test configuration
TEST_SECRET = "test-secret-key-1234567890"
TEST_COOKIE_NAME = "test_csrf_token"
TEST_HEADER_NAME = "X-Test-CSRF-Token"


# Fixtures
@pytest.fixture
def mock_config():
    """Create a mock config with CSRF settings."""
    config = Config()
    config.secret_key = TEST_SECRET
    config.csrf_enabled = True
    config.csrf_cookie_name = TEST_COOKIE_NAME
    config.csrf_header_name = TEST_HEADER_NAME
    config.csrf_required_urls = ["/protected/*", "/api/.*"]
    config.csrf_exempt_urls = ["/public/.*", "/health"]
    config.csrf_sensitive_cookies = ["sessionid", "auth_token"]
    return config


@pytest.fixture
def csrf_middleware(mock_config):
    """Create a CSRF middleware instance with the mock config."""
    with patch("nexios.middleware.csrf.get_config", return_value=mock_config):
        return CSRFMiddleware()


@pytest.fixture
def mock_request():
    """Create a mock request object."""
    request = MagicMock(spec=Request)
    request.method = "GET"
    request.url = MagicMock()
    request.url.path = "/"
    request.headers = {}
    request.cookies = {}
    return request


@pytest.fixture
def mock_response():
    """Create a mock response object."""
    response = MagicMock(spec=Response)
    response.headers = {}
    response.cookies = {}
    response.set_cookie = MagicMock()
    response.delete_cookie = MagicMock()
    response.text = MagicMock(return_value=response)
    return response


# Test cases
class TestCSRFMiddleware:
    def test_initialization(self, csrf_middleware, mock_config):
        """Test CSRF middleware initialization with config."""
        assert csrf_middleware.use_csrf is True
        assert csrf_middleware.cookie_name == mock_config.csrf_cookie_name
        assert csrf_middleware.header_name == mock_config.csrf_header_name
        assert len(csrf_middleware.required_urls) == 2  # /protected/*, /api/.*
        assert len(csrf_middleware.exempt_urls) == 2  # /public/.*, /health
        assert len(csrf_middleware.sensitive_cookies) == 2  # sessionid, auth_token

    def test_generate_csrf_token(self, csrf_middleware):
        """Test CSRF token generation."""
        token = csrf_middleware._generate_csrf_token()
        assert isinstance(token, str)
        assert len(token) > 0

        # Should be able to load the token with our serializer
        try:
            csrf_middleware.serializer.loads(token)
        except BadSignature:
            pytest.fail("Generated token is not valid")

    def test_csrf_tokens_match(self, csrf_middleware):
        """Test CSRF token comparison."""
        token1 = csrf_middleware._generate_csrf_token()
        token2 = token1  # Same token

        assert csrf_middleware._csrf_tokens_match(token1, token2) is True

        # Different tokens should not match
        token3 = csrf_middleware._generate_csrf_token()
        assert csrf_middleware._csrf_tokens_match(token1, token3) is False

    @pytest.mark.parametrize(
        "url,expected",
        [
            ("/protected/resource", True),
            ("/protected/other", True),
            ("/api/users", True),
            ("/api/v1/data", True),
            ("/public/info", False),
            ("/health", False),
            ("/unprotected", False),
        ],
    )
    def test_url_is_required(self, csrf_middleware, url, expected):
        """Test URL requirement checking."""
        # Convert glob patterns to regex patterns for testing
        csrf_middleware.required_urls = [
            r"^/protected/.*$",  # Convert /protected/* to regex
            r"^/api/.*$",  # Convert /api/* to regex
        ]
        assert csrf_middleware._url_is_required(url) == expected

    @pytest.mark.parametrize(
        "url,expected",
        [
            ("/public/info", True),
            ("/health", True),
            ("/protected/resource", False),
            ("/api/users", False),
        ],
    )
    def test_url_is_exempt(self, csrf_middleware, url, expected):
        """Test URL exemption checking."""
        assert csrf_middleware._url_is_exempt(url) == expected

    @pytest.mark.parametrize(
        "cookies,expected",
        [
            ({"sessionid": "123"}, True),
            ({"auth_token": "abc"}, True),
            ({"other": "cookie"}, False),
            ({}, False),
        ],
    )
    def test_has_sensitive_cookies(self, csrf_middleware, cookies, expected):
        """Test sensitive cookie detection."""
        assert csrf_middleware._has_sensitive_cookies(cookies) == expected

    @pytest.mark.asyncio
    async def test_process_response_sets_cookie(
        self, csrf_middleware, mock_request, mock_response
    ):
        """Test that the response sets the CSRF cookie."""
        await csrf_middleware.process_response(mock_request, mock_response)

        # Should set a cookie with the expected parameters
        mock_response.set_cookie.assert_called_once()
        args, kwargs = mock_response.set_cookie.call_args
        assert kwargs["key"] == TEST_COOKIE_NAME
        assert kwargs["path"] == "/"
        assert kwargs["httponly"] is True
        assert kwargs["samesite"] == "lax"

    @pytest.mark.asyncio
    async def test_process_response_disabled_csrf(
        self, mock_config, mock_request, mock_response
    ):
        """Test that no cookie is set when CSRF is disabled."""
        mock_config.csrf_enabled = False

        with patch("nexios.middleware.csrf.get_config", return_value=mock_config):
            middleware = CSRFMiddleware()
            await middleware.process_response(mock_request, mock_response)

        mock_response.set_cookie.assert_not_called()

    @pytest.mark.asyncio
    async def test_exempt_url_with_sensitive_cookies(
        self, csrf_middleware, mock_request, mock_response
    ):
        """Test that exempt URLs with sensitive cookies still need CSRF."""
        mock_request.method = "POST"
        mock_request.url.path = "/public/info"
        mock_request.cookies = {"sessionid": "123"}  # Has sensitive cookie

        async def mock_next():
            pytest.fail("Middleware should have rejected the request")

        await csrf_middleware.process_request(mock_request, mock_response, mock_next)
        mock_response.delete_cookie.assert_called_once()
        mock_response.text.assert_called_once_with(
            "CSRF token missing from cookies", status_code=403
        )

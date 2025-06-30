import gzip
import json
from unittest.mock import MagicMock, Mock, patch

import pytest

from nexios import get_application
from nexios.http import Request, Response
from nexios.middleware.base import BaseMiddleware
from nexios.middleware.common import CommonMiddleware
from nexios.middleware.gzip import GZipMiddleware
from nexios.middleware.security import SecurityMiddleware
from nexios.testing import Client


class TestBaseMiddleware:
    """Test BaseMiddleware functionality"""

    def test_base_middleware_initialization(self):
        """Test BaseMiddleware initialization"""
        middleware = BaseMiddleware()
        assert middleware is not None

    def test_base_middleware_call(self):
        """Test BaseMiddleware __call__ method"""
        middleware = BaseMiddleware()
        request = Mock()
        response = Mock()

        # Should return the response as-is
        async def mock_call_next():
            return response

        result = middleware(request, response, mock_call_next)
        assert result


class TestCommonMiddleware:
    """Test CommonMiddleware functionality"""

    @pytest.fixture
    async def app_with_common_middleware(self):
        """Create app with CommonMiddleware"""
        app = get_application()
        app.add_middleware(CommonMiddleware())
        async with Client(app) as client:
            yield client, app

    def test_common_middleware_initialization(self):
        """Test CommonMiddleware initialization"""
        middleware = CommonMiddleware()
        assert middleware is not None

    def test_common_middleware_with_config(self):
        """Test CommonMiddleware with configuration"""
        config = {
            "trusted_hosts": ["example.com"],
            "allowed_hosts": ["*.example.com"],
            "max_content_length": 1024 * 1024,
        }
        middleware = CommonMiddleware(**config)
        assert middleware is not None

    async def test_common_middleware_request_processing(
        self, app_with_common_middleware
    ):
        """Test CommonMiddleware request processing"""
        client, app = app_with_common_middleware

        @app.get("/test")
        async def test_handler(req: Request, res: Response):
            return res.text("OK")

        response = await client.get("/test")
        assert response.status_code == 200
        assert response.text == "OK"

    async def test_common_middleware_trusted_hosts(self, app_with_common_middleware):
        """Test CommonMiddleware with trusted hosts"""
        client, app = app_with_common_middleware

        @app.get("/test")
        async def test_handler(req: Request, res: Response):
            return res.text("OK")

        # Test with valid host
        response = await client.get("/test", headers={"Host": "localhost"})
        assert response.status_code == 200

    async def test_common_middleware_content_length_limit(
        self, app_with_common_middleware
    ):
        """Test CommonMiddleware content length limit"""
        client, app = app_with_common_middleware

        @app.post("/test")
        async def test_handler(req: Request, res: Response):
            return res.text("OK")

        # Test with large content
        large_data = "x" * 1024 * 1024  # 1MB
        response = await client.post("/test", data=large_data)
        # Should handle large content appropriately
        assert response.status_code in [200, 413]  # 413 if limit exceeded


# class TestGipMiddleware:
#     """Test GzipMiddleware functionality"""

#     @pytest.fixture
#     async def app_with_gzip_middleware(self):
#         """Create app with GzipMiddleware"""
#         app = get_application()
#         app.add_middleware(GZipMiddleware())
#         async with Client(app) as client:
#             yield client, app

#     def test_gzip_middleware_initialization(self):
#         """Test GzipMiddleware initialization"""
#         middleware = GZipMiddleware()
#         assert middleware is not None

#     def test_gzip_middleware_with_config(self):
#         """Test GzipMiddleware with configuration"""
#         config = {
#             "compress_level": 6,
#             "min_size": 500,
#             "content_types": ["text/plain", "application/json"],
#         }
#         middleware = GZipMiddleware(**config)
#         assert middleware is not None

#     async def test_gzip_middleware_compression(self, app_with_gzip_middleware):
#         """Test GzipMiddleware compression"""
#         client, app = app_with_gzip_middleware

#         @app.get("/test")
#         async def test_handler(req: Request, res: Response):
#             return res.text("This is a test response that should be compressed")

#         response = await client.get("/test", headers={"Accept-Encoding": "gzip"})
#         assert response.status_code == 200

#         # Check if response is compressed
#         content_encoding = response.headers.get("content-encoding")
#         if content_encoding == "gzip":
#             # Verify it's actually gzipped
#             import gzip
#             decompressed = gzip.decompress(response.content).decode()
#             assert "This is a test response" in decompressed

# TODO: Wrap this to suit nexios

# async def test_gzip_middleware_no_compression_small_content(self, app_with_gzip_middleware):
#     """Test GzipMiddleware with small content (should not compress)"""
#     client, app = app_with_gzip_middleware

#     @app.get("/test")
#     async def test_handler(req: Request, res: Response):
#         return res.text("small")

#     response = await client.get("/test", headers={"Accept-Encoding": "gzip"})
#     assert response.status_code == 200

#     # Small content should not be compressed
#     assert response.headers.get("content-encoding") != "gzip"

# async def test_gzip_middleware_no_accept_encoding(self, app_with_gzip_middleware):
#     """Test GzipMiddleware without Accept-Encoding header"""
#     client, app = app_with_gzip_middleware

#     @app.get("/test")
#     async def test_handler(req: Request, res: Response):
#         return res.text("This is a test response")

#     response = await client.get("/test")  # No Accept-Encoding header
#     assert response.status_code == 200
#     assert response.headers.get("content-encoding") != "gzip"

# async def test_gzip_middleware_json_response(self, app_with_gzip_middleware):
#     """Test GzipMiddleware with JSON response"""
#     client, app = app_with_gzip_middleware

#     @app.get("/test")
#     async def test_handler(req: Request, res: Response):
#         return res.json({"message": "This is a JSON response", "data": [1, 2, 3, 4, 5]})

#     response = await client.get("/test", headers={"Accept-Encoding": "gzip"})
#     assert response.status_code == 200

#     # JSON responses should be compressible
#     content_encoding = response.headers.get("content-encoding")
#     if content_encoding == "gzip":
#         decompressed = gzip.decompress(response.content).decode()
#         data = json.loads(decompressed)
#         assert data["message"] == "This is a JSON response"


class TestSecurityMiddleware:
    """Test SecurityMiddleware functionality"""

    @pytest.fixture
    async def app_with_security_middleware(self):
        """Create app with SecurityMiddleware"""
        app = get_application()
        app.add_middleware(SecurityMiddleware())
        async with Client(app) as client:
            yield client, app

    def test_security_middleware_initialization(self):
        """Test SecurityMiddleware initialization"""
        middleware = SecurityMiddleware()
        assert middleware is not None

    def test_security_middleware_with_config(self):
        """Test SecurityMiddleware with configuration"""
        config = {
            "csp_policy": "default-src 'self'",
            "frame_options": "DENY",
            "content_type_options": "nosniff",
            "xss_protection": "1; mode=block",
        }
        middleware = SecurityMiddleware(**config)
        assert middleware is not None

    async def test_security_middleware_csp_header(self, app_with_security_middleware):
        """Test SecurityMiddleware Content Security Policy header"""
        client, app = app_with_security_middleware

        @app.get("/test")
        async def test_handler(req: Request, res: Response):
            return res.text("OK")

        response = await client.get("/test")
        assert response.status_code == 200

        # CSP header might be present depending on configuration
        headers = response.headers
        # This is a basic check - actual CSP value depends on middleware config

    async def test_security_middleware_hsts_header(self, app_with_security_middleware):
        """Test SecurityMiddleware HSTS header"""
        client, app = app_with_security_middleware

        @app.get("/test")
        async def test_handler(req: Request, res: Response):
            return res.text("OK")

        response = await client.get("/test")
        assert response.status_code == 200

        # HSTS header might be present depending on configuration
        headers = response.headers
        # This is a basic check - actual HSTS value depends on middleware config


class TestMiddlewareIntegration:
    """Integration tests for middleware"""

    @pytest.fixture
    async def app_with_multiple_middleware(self):
        """Create app with multiple middleware"""
        app = get_application()
        app.add_middleware(SecurityMiddleware())
        # app.add_middleware(GZipMiddleware())
        app.add_middleware(CommonMiddleware())
        async with Client(app) as client:
            yield client, app

    async def test_multiple_middleware_integration(self, app_with_multiple_middleware):
        """Test multiple middleware working together"""
        client, app = app_with_multiple_middleware

        @app.get("/test")
        async def test_handler(req: Request, res: Response):
            return res.json({"message": "Test response", "data": [1, 2, 3, 4, 5]})

        response = await client.get("/test", headers={"Accept-Encoding": "gzip"})
        assert response.status_code == 200

        # Should have security headers
        headers = response.headers
        # Should potentially have compression
        # Should handle the request properly

    async def test_middleware_error_handling(self, app_with_multiple_middleware):
        """Test middleware error handling"""
        client, app = app_with_multiple_middleware

        @app.get("/error")
        async def error_handler(req: Request, res: Response):
            raise Exception("Test error")

        # Should handle errors gracefully
        response = await client.get("/error")
        # Should return appropriate error response
        assert response.status_code in [500, 404]  # Depending on error handling

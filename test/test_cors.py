# test_cors_with_app.py
import pytest

from nexios import get_application
from nexios.config import MakeConfig
from nexios.middleware.cors import CORSMiddleware
from nexios.testing import Client


@pytest.fixture
async def cors_app():
    # Create app with CORS configuration
    config = MakeConfig(
        {
            "cors": {
                "allow_origins": ["http://example.com", "https://example.org"],
                "allow_methods": ["GET", "POST"],
                "allow_headers": ["X-Custom-Header"],
                "allow_credentials": True,
                "expose_headers": ["X-Exposed-Header"],
                "debug": True,
            }
        }
    )
    app = get_application(config)

    # Add test route
    @app.get("/test")
    async def test_route(req, res):
        return res.text("OK")

    # Add CORS middleware
    app.add_middleware(CORSMiddleware())

    return app


@pytest.fixture
async def client(cors_app):
    async with Client(cors_app) as c:
        yield c


async def test_simple_request_allowed_origin(client):
    # Test simple GET request with allowed origin
    response = await client.get("/test", headers={"Origin": "http://example.com"})

    assert response.status_code == 200
    assert response.text == "OK"
    assert response.headers["Access-Control-Allow-Origin"] == "http://example.com"
    assert response.headers["Access-Control-Allow-Credentials"] == "true"
    assert response.headers["Access-Control-Expose-Headers"] == "X-Exposed-Header"


async def test_simple_request_disallowed_origin(client):
    # Test simple GET request with disallowed origin
    response = await client.get("/test", headers={"Origin": "http://disallowed.com"})

    assert response.status_code == 200
    assert response.text == "OK"
    # Should not have CORS headers for disallowed origin
    assert "Access-Control-Allow-Origin" not in response.headers


async def test_preflight_request_success(client):
    # Test successful OPTIONS preflight request
    response = await client.options(
        "/test",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-Custom-Header",
        },
    )

    assert response.status_code == 201  # Custom status from our middleware
    assert response.headers["Access-Control-Allow-Origin"] == "http://example.com"
    assert response.headers["Access-Control-Allow-Methods"] == "GET"
    assert response.headers["Access-Control-Allow-Headers"] == "x-custom-header"
    assert response.headers["Access-Control-Allow-Credentials"] == "true"
    assert response.headers["Access-Control-Max-Age"] == "600"  # Default value


async def test_preflight_request_disallowed_method(client):
    # Test OPTIONS request with disallowed method
    response = await client.options(
        "/test",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "PUT",
        },
    )

    # assert response.status_code == 400  # Default error status
    assert "PUT" not in response.headers.get("Access-Control-Allow-Methods", "")


async def test_preflight_request_disallowed_header(client):
    # Test OPTIONS request with disallowed header
    response = await client.options(
        "/test",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-Disallowed-Header",
        },
    )

    assert response.status_code == 400
    assert "X-Disallowed-Header" not in response.headers.get(
        "Access-Control-Allow-Headers", ""
    )


async def test_wildcard_origin():
    # Test app with wildcard origin
    config = MakeConfig({"cors": {"allow_origins": ["*"], "allow_methods": ["*"]}})
    app = get_application(config)

    @app.get("/wildcard")
    async def wildcard_route(req, res):
        return res.text("OK")

    app.add_middleware(CORSMiddleware())

    async with Client(app) as client:
        response = await client.get(
            "/wildcard", headers={"Origin": "http://any-origin.com"}
        )

        assert response.status_code == 200
        assert (
            response.headers["Access-Control-Allow-Origin"] == "http://any-origin.com"
        )


async def test_no_cors_headers_without_origin():
    # Test that CORS headers aren't added when no Origin header is present
    config = MakeConfig(
        {"cors": {"allow_origins": ["http://example.com"], "allow_methods": ["GET"]}}
    )
    app = get_application(config)

    @app.get("/no-origin")
    async def no_origin_route(req, res):
        return res.text("OK")

    app.add_middleware(CORSMiddleware())

    async with Client(app) as client:
        response = await client.get("/no-origin")

        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" not in response.headers

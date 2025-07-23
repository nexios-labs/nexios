from typing import Optional

import pytest
from pydantic import BaseModel

from nexios import Depend, get_application
from nexios.http import Request, Response
from nexios.testing import Client


@pytest.fixture
async def di_client():
    app = get_application()
    async with Client(app) as client:
        yield client, app


# Test basic dependency injection
async def test_basic_di(di_client):
    client, app = di_client

    async def get_message():
        return "Hello from DI"

    @app.get("/di/basic")
    async def basic_di_route(
        req: Request, res: Response, msg: str = Depend(get_message)
    ):
        return res.text(msg)

    response = await client.get("/di/basic")
    assert response.status_code == 200
    assert response.text == "Hello from DI"


# Test dependency with request access
async def test_request_dependency(di_client):
    client, app = di_client

    async def get_user_agent(req: Request):
        return req.headers.get("user-agent", "unknown")

    @app.get("/di/user-agent")
    async def user_agent_route(
        req: Request, res: Response, ua: str = Depend(get_user_agent)
    ):
        return res.text(ua)

    response = await client.get("/di/user-agent", headers={"User-Agent": "test-agent"})
    assert response.status_code == 200
    assert response.text == "test-agent"


# Test nested dependencies
async def test_nested_dependencies(di_client):
    client, app = di_client

    async def get_config():
        return {"env": "test"}

    async def get_service(config: dict = Depend(get_config)):
        return f"Service in {config['env']} environment"

    @app.get("/di/nested")
    async def nested_route(
        req: Request, res: Response, service: str = Depend(get_service)
    ):
        return res.text(service)

    response = await client.get("/di/nested")
    assert response.status_code == 200
    assert response.text == "Service in test environment"


# Test dependency with pydantic model
async def test_pydantic_dependency(di_client):
    client, app = di_client

    class QueryParams(BaseModel):
        page: int = 1
        limit: int = 10

    async def get_params(req: Request) -> QueryParams:
        return QueryParams(**req.query_params)

    @app.get("/di/pydantic")
    async def pydantic_route(
        req: Request, res: Response, params: QueryParams = Depend(get_params)
    ):
        return res.json({"page": params.page, "limit": params.limit})

    response = await client.get("/di/pydantic?page=2&limit=20")
    assert response.status_code == 200
    assert response.json() == {"page": 2, "limit": 20}


# Test optional dependencies
async def test_optional_dependency(di_client):
    client, app = di_client

    async def optional_header(req: Request):
        if "x-optional" in req.headers:
            return req.headers["x-optional"]
        return None

    @app.get("/di/optional")
    async def optional_route(
        req: Request, res: Response, header: Optional[str] = Depend(optional_header)
    ):
        return res.text(header or "not-provided")

    # Test with header
    response = await client.get("/di/optional", headers={"x-optional": "provided"})
    assert response.status_code == 200
    assert response.text == "provided"

    # Test without header
    response = await client.get("/di/optional")
    assert response.status_code == 200
    assert response.text == "not-provided"


# Test dependency error handling
async def test_dependency_error(di_client):
    client, app = di_client

    async def failing_dependency():
        raise ValueError("Dependency failed")

    @app.get("/di/error")
    async def error_route(
        req: Request, res: Response, dep: str = Depend(failing_dependency)
    ):
        return res.text("should-not-reach-here")

    response = await client.get("/di/error")
    assert response.status_code == 500
    assert "Dependency failed" in response.text


# Test sync dependencies
async def test_sync_dependency(di_client):
    client, app = di_client

    def sync_dependency():
        return "sync-result"

    @app.get("/di/sync")
    async def sync_route(
        req: Request, res: Response, result: str = Depend(sync_dependency)
    ):
        return res.text(result)

    response = await client.get("/di/sync")
    assert response.status_code == 200
    assert response.text == "sync-result"


# Test dependency with route parameters
async def test_route_param_dependency(di_client):
    client, app = di_client

    async def get_id_param(req: Request):
        return req.path_params["id"]

    @app.get("/di/param/{id}")
    async def param_route(req: Request, res: Response, id: str = Depend(get_id_param)):
        return res.text(id)

    response = await client.get("/di/param/123")
    assert response.status_code == 200
    assert response.text == "123"


# Test generator dependency (sync)
async def test_generator_dependency(di_client):
    client, app = di_client
    cleanup = []

    def gen_dep():
        cleanup.append("start")
        try:
            yield "gen-value"
        finally:
            cleanup.append("cleanup")

    @app.get("/di/gen")
    async def gen_route(req: Request, res: Response, value: str = Depend(gen_dep)):
        return res.text(value)

    response = await client.get("/di/gen")
    assert response.status_code == 200
    assert response.text == "gen-value"
    assert cleanup == ["start", "cleanup"]


# Test async generator dependency
async def test_async_generator_dependency(di_client):
    client, app = di_client
    cleanup = []

    async def agen_dep():
        cleanup.append("start")
        try:
            yield "agen-value"
        finally:
            cleanup.append("cleanup")

    @app.get("/di/agen")
    async def agen_route(req: Request, res: Response, value: str = Depend(agen_dep)):
        return res.text(value)

    response = await client.get("/di/agen")
    assert response.status_code == 200
    assert response.text == "agen-value"
    assert cleanup == ["start", "cleanup"]


async def test_dependency_injection_with_custom_error(di_client):
    client, app = di_client

    class CustomError(Exception):
        pass

    async def custom_error_dep():
        raise CustomError("This is a custom error")

    @app.get("/di/custom-error")
    async def custom_error_route(
        req: Request, res: Response, dep: str = Depend(custom_error_dep)
    ):
        return res.text("should-not-reach-here")

    response = await client.get("/di/custom-error")
    assert response.status_code == 500
    assert "This is a custom error" in response.text


async def test_global_dependency(di_client):
    class CustomError(Exception):
        pass

    async def global_dep():
        raise CustomError("global-value")

    app = get_application(dependencies=[Depend(global_dep)])

    @app.get("/di/global")
    async def global_route(req: Request, res: Response):
        return res.text("should-not-reach-here")

    async with Client(app) as client:
        response = await client.get("/di/global")
        assert response.status_code == 500
        assert "global-value" in response.text

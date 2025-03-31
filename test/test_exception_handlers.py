from nexios import NexiosApp
from nexios.exceptions import HTTPException
from nexios.http import Request, Response
from nexios import get_application
from nexios.testing import Client
import pytest
from typing import Tuple


@pytest.fixture
async def async_client():
    app = get_application()  # Fresh app instance for each test
    async with Client(app, log_requests=True) as c:
        yield c, app


class AcessDenied(HTTPException):
    pass


async def test_server_error_handle(async_client: Tuple[Client, NexiosApp]):

    client, app = async_client

    async def server_error_handler(req: Request, res: Response, exc: Exception):
        return res.json({"error": "server error"}, status_code=500)

    app.add_exception_handler(Exception, server_error_handler)

    @app.get("/home")
    async def get(req: Request, res: Response):
        raise Exception

    response = await client.get("/home")
    assert response.status_code == 500
    assert response.json() == {"error": "server error"}


async def test_http_error_handlers(async_client: Tuple[Client, NexiosApp]):

    client, app = async_client

    async def server_error_handler(req: Request, res: Response, exc: HTTPException):
        return res.json({"error": "access denied"}, status_code=exc.status_code)

    app.add_exception_handler(HTTPException, server_error_handler)

    @app.get("/home")
    async def get(req: Request, res: Response):
        raise HTTPException(status_code=403)

    response = await client.get("/home")
    assert response.status_code == 403
    assert response.json() == {"error": "access denied"}

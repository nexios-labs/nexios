from typing import Tuple

import pytest

from nexios import NexiosApp, get_application
from nexios.exceptions import HTTPException, NotFoundException
from nexios.http import Request, Response
from nexios.testing import Client


@pytest.fixture
async def async_client():
    app = get_application()  # Fresh app instance for each test
    async with Client(app, log_requests=True) as c:
        yield c, app


async def test_default_404_handler(async_client: Tuple[Client, NexiosApp]):
    client, app = async_client

    @app.get("/existing-route")
    async def existing_route(req: Request, res: Response):
        return res.text("OK")

    # Test non-existent route
    response = await client.get("/non-existent-route")
    assert response.status_code == 404
    assert "Not Found" in response.text


async def test_custom_404_handler(async_client: Tuple[Client, NexiosApp]):
    client, app = async_client

    async def custom_404_handler(req: Request, res: Response, exc: NotFoundException):
        return res.json({"error": "Custom not found"}, status_code=404)

    app.add_exception_handler(NotFoundException, custom_404_handler)

    response = await client.get("/non-existent-route")
    assert response.status_code == 404
    assert response.json() == {"error": "Custom not found"}


async def test_http_exception_handling(async_client: Tuple[Client, NexiosApp]):
    client, app = async_client

    @app.get("/test-http-exception")
    async def test_route(req: Request, res: Response):
        raise HTTPException(status_code=403, detail="Access denied")

    response = await client.get("/test-http-exception")
    assert response.status_code == 403
    assert response.json() == "Access denied"


async def test_custom_exception_handler(async_client: Tuple[Client, NexiosApp]):
    client, app = async_client

    class CustomException(Exception):
        pass

    @app.get("/test-custom-exception")
    async def test_route(req: Request, res: Response):
        raise CustomException("Something went wrong")

    async def handle_custom_exception(
        req: Request, res: Response, exc: CustomException
    ):
        return res.json({"error": str(exc)}, status_code=400)

    app.add_exception_handler(CustomException, handle_custom_exception)

    response = await client.get("/test-custom-exception")
    assert response.status_code == 400
    assert response.json() == {"error": "Something went wrong"}


async def test_status_code_exception_handler(async_client: Tuple[Client, NexiosApp]):
    client, app = async_client

    @app.get("/test-status-code")
    async def test_route(req: Request, res: Response):
        raise HTTPException(status_code=418, detail="I'm a teapot")

    async def handle_teapot(req: Request, res: Response, exc: HTTPException):
        return res.json({"message": "This is a teapot"}, status_code=418)

    app.add_exception_handler(418, handle_teapot)

    response = await client.get("/test-status-code")
    assert response.status_code == 418
    assert response.json() == {"message": "This is a teapot"}


async def test_exception_handler_ordering(async_client: Tuple[Client, NexiosApp]):
    client, app = async_client

    class SpecificException(HTTPException):
        pass

    class GeneralException(HTTPException):
        pass

    @app.get("/test-specific")
    async def test_specific(req: Request, res: Response):
        raise SpecificException(status_code=400, detail="Specific error")

    @app.get("/test-general")
    async def test_general(req: Request, res: Response):
        raise GeneralException(status_code=400, detail="General error")

    # Register general handler first
    async def general_handler(req: Request, res: Response, exc: HTTPException):
        return res.text("General handler")

    # Register specific handler second
    async def specific_handler(req: Request, res: Response, exc: SpecificException):
        return res.text("Specific handler")

    app.add_exception_handler(HTTPException, general_handler)
    app.add_exception_handler(SpecificException, specific_handler)

    # Specific exception should use specific handler
    response = await client.get("/test-specific")
    assert response.text == "Specific handler"

    # General exception should use general handler
    response = await client.get("/test-general")
    assert response.text == "General handler"


async def test_exception_with_headers(async_client: Tuple[Client, NexiosApp]):
    client, app = async_client

    @app.get("/test-headers")
    async def test_route(req: Request, res: Response):
        raise HTTPException(
            status_code=403, detail="Forbidden", headers={"X-Custom-Header": "value"}
        )

    response = await client.get("/test-headers")
    assert response.status_code == 403
    assert response.headers["x-custom-header"] == "value"


async def test_middleware_exception_handling(async_client: Tuple[Client, NexiosApp]):
    client, app = async_client

    async def error_middleware(req: Request, res: Response, call_next):
        try:
            return await call_next()
        except Exception as exc:
            return res.json({"middleware_error": str(exc)}, status_code=500)

    app.add_middleware(error_middleware)

    @app.get("/test-middleware-error")
    async def test_route(req: Request, res: Response):
        raise ValueError("Error in route")

    response = await client.get("/test-middleware-error")
    assert response.status_code == 500
    assert response.json() == {"middleware_error": "Error in route"}


async def test_combined_exception_handling(async_client: Tuple[Client, NexiosApp]):
    client, app = async_client

    class CustomError(Exception):
        pass

    async def custom_handler(req: Request, res: Response, exc: CustomError):
        return res.json({"custom": True}, status_code=400)

    app.add_exception_handler(CustomError, custom_handler)

    @app.get("/test-combined")
    async def test_route(req: Request, res: Response):
        raise CustomError("Combined test")

    response = await client.get("/test-combined")
    assert response.status_code == 400
    assert response.json() == {"custom": True}

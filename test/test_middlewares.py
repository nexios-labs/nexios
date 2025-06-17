import pytest

from nexios import NexiosApp, get_application
from nexios.http import Request, Response
from nexios.testing import Client

app: NexiosApp = get_application()


@pytest.fixture(autouse=True)
async def async_client():
    async with Client(app, log_requests=True) as c:
        yield c


async def test_middleware_modifies_response(async_client: Client):

    app.router.routes.clear()
    app.http_middleware.clear()

    async def header_middleware(request: Request, response: Response, call_next):
        await call_next()
        response.set_header("X-Middleware-Added", "True")

    app.add_middleware(header_middleware)

    @app.route("/header-test")
    async def test_route(request: Request, response: Response):
        return response.text("OK")

    # Execute test
    response = await async_client.get("/header-test")
    assert response.status_code == 200
    assert "X-Middleware-Added" in response.headers
    assert response.headers["X-Middleware-Added"] == "True"


async def test_middleware_modifies_request(async_client: Client):

    app.router.routes.clear()
    app.http_middleware.clear()

    async def modify_request(request: Request, response: Response, call_next):
        request.state.text = "modified"
        return await call_next()

    app.add_middleware(modify_request)

    @app.route("/request-test")
    async def request_test(request: Request, response: Response):
        return response.text(request.state.text)

    response = await async_client.get("/request-test")
    assert response.text == "modified"


async def test_middleware_order(async_client: Client):

    app.router.routes.clear()
    app.http_middleware.clear()

    async def first_middleware(equest: Request, response: Response, call_next):
        await call_next()
        response.set_header("X-Order-1", "First")
        return response

    async def second_middleware(equest: Request, response: Response, call_next):
        await call_next()
        response.set_header("X-Order-2", "Second")
        return response

    app.add_middleware(first_middleware)
    app.add_middleware(second_middleware)

    @app.route("/order-test")
    async def order_test(request: Request, response: Response):
        return response.text("OK")

    response = await async_client.get("/order-test")
    assert response.headers["X-Order-1"] == "First"
    assert response.headers["X-Order-2"] == "Second"


async def test_middleware_short_circuit(async_client: Client):

    app.router.routes.clear()
    app.http_middleware.clear()

    async def blocking_middleware(request: Request, response: Response, call_next):
        if request.headers.get("Authorization") != "Valid":
            return response.text("Unauthorized", status_code=403)
        return await call_next()

    app.add_middleware(blocking_middleware)

    @app.route("/protected")
    async def protected_route(request: Request, response: Response):
        return response.text("Secret")

    # Test blocked request
    response = await async_client.get("/protected")
    assert response.status_code == 403
    assert response.text == "Unauthorized"

    # Test allowed request
    response = await async_client.get("/protected", headers={"Authorization": "Valid"})
    assert response.status_code == 200
    assert response.text == "Secret"


async def test_middleware_exception_handling(async_client: Client):

    app.router.routes.clear()
    app.http_middleware.clear()

    async def exception_middleware(request: Request, response: Response, call_next):
        try:
            return await call_next()
        except Exception:
            return response.text("Handled Error", status_code=500)

    app.add_middleware(exception_middleware)

    @app.route("/error-route")
    async def error_route(request: Request, response: Response):
        raise ValueError("Something went wrong")

    response = await async_client.get("/error-route")
    assert response.status_code == 500
    assert response.text == "Handled Error"

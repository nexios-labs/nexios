import pytest

from nexios import get_application
from nexios.http import Request, Response
from nexios.routing import Router, Routes
from nexios.testing import Client


@pytest.fixture
async def async_client():
    app = get_application()  # Fresh app instance for each test
    async with Client(app, log_requests=True) as c:
        yield c, app


async def test_route_decorator(async_client):
    client, app = async_client  # Extract client and app

    @app.get("/get")
    async def handle_get(req: Request, res: Response):
        return res.json({"method": req.method})

    @app.post("/post")
    async def handle_post(req: Request, res: Response):
        return res.json({"method": req.method})

    # Test GET request
    get_response = await client.get("/get")
    assert get_response.status_code == 200
    assert get_response.json() == {"method": "GET"}

    # Test POST request
    post_response = await client.post("/post")
    assert post_response.status_code == 200
    assert post_response.json() == {"method": "POST"}


async def test_add_route_method(async_client):
    client, app = async_client  # Extract client and app

    async def handle_get(req: Request, res: Response):
        return res.json({"method": req.method})

    async def handle_post(req: Request, res: Response):
        return res.json({"method": req.method})

    # Add routes
    app.add_route(Routes("/get", handle_get, methods=["GET"]))
    app.add_route(Routes("/post", handle_post, methods=["POST"]))

    # Test GET request
    get_response = await client.get("/get")
    assert get_response.status_code == 200
    assert get_response.json() == {"method": "GET"}

    # Test POST request
    post_response = await client.post("/post")
    assert post_response.status_code == 200
    assert post_response.json() == {"method": "POST"}


async def test_routers_no_prefix(async_client):
    client, app = async_client

    router = Router()

    @router.get("/")
    async def handle_get(req: Request, res: Response):
        return res.text("i love you")

    app.mount_router(router)

    response = await client.get("/")
    assert response.status_code == 200


async def test_url_for_with_params(async_client):
    client, app = async_client

    @app.get("/get/name/{age}", name="name")
    async def get(req: Request, res: Response): ...

    url = app.url_for("name", age=0)
    assert url == "/get/name/0"


async def test_url_for_with_request(async_client):
    client, app = async_client

    @app.get("/get/name/{age}", name="name")
    async def get(req: Request, res: Response):

        return res.json({"name": req.url_for("name", age=0)})

    response = await client.get("/get/name/0")
    data = response.json()
    assert data["name"] == "/get/name/0"


async def test_url_parameters(async_client):
    client, app = async_client

    @app.get("/user/{user_id}")
    async def handle_user(req: Request, res: Response):
        user_id = req.path_params["user_id"]
        return res.json({"user_id": user_id})

    # Test with a specific user ID
    response = await client.get("/user/123")
    assert response.status_code == 200
    assert response.json() == {"user_id": "123"}


async def test_route_prefixes(async_client):
    client, app = async_client

    # Create a router with a prefix
    router = Router(prefix="/api")

    @router.get("/users")
    async def handle_users(req: Request, res: Response):
        return res.json({"message": "Users Route"})

    @router.post("/posts")
    async def handle_posts(req: Request, res: Response):
        return res.json({"message": "Posts Route"})

    # Mount the router under the app
    app.mount_router(router)

    # Test the prefixed routes
    users_response = await client.get("/api/users")
    assert users_response.status_code == 200
    assert users_response.json() == {"message": "Users Route"}

    posts_response = await client.post("/api/posts")
    assert posts_response.status_code == 200
    assert posts_response.json() == {"message": "Posts Route"}


async def test_invalid_routes(async_client):
    client, app = async_client

    # Define a valid route
    @app.get("/valid")
    async def handle_valid(req: Request, res: Response):
        return res.text("Valid Route")

    # Test an invalid route
    await client.get("/invalid")


async def test_nested_routers(async_client):
    client, app = async_client

    # Create a parent router
    parent_router = Router(prefix="/parent")

    # Create a child router
    child_router = Router(prefix="/child")

    @child_router.get("/nested")
    async def handle_nested(req: Request, res: Response):
        return res.text("Nested Router Works")

    # Mount the child router under the parent router
    parent_router.mount_router(child_router)

    # Mount the parent router under the app
    app.mount_router(parent_router)

    # Test the nested route
    response = await client.get("/parent/child/nested")
    assert response.status_code == 200
    assert response.text == "Nested Router Works"


async def test_handler_args(async_client):
    client, app = async_client

    @app.get("/user/{user_id}")
    async def handle_user(req: Request, res: Response, user_id: str):
        return res.json({"user_id": user_id})

    # Test with a specific user ID
    response = await client.get("/user/123")
    assert response.status_code == 200
    assert response.json() == {"user_id": "123"}


async def test_add_route_with_args(async_client):
    client, app = async_client

    async def handle_user(req: Request, res: Response, user_id: str):
        return res.json({"user_id": user_id})

    # Add route with args
    app.add_route(path="/user/{user_id}", handler=handle_user, methods=["GET"])

    # Test with a specific user ID
    response = await client.get("/user/123")
    assert response.status_code == 200
    assert response.json() == {"user_id": "123"}

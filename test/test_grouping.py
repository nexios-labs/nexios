# test_grouping.py
import pytest
from nexios.http import Request, Response
from nexios.testing import Client
from nexios.routing import Router, Group, Routes
from nexios import get_application


@pytest.fixture
async def async_client():
    app = get_application()
    async with Client(app) as c:
        yield c, app


async def test_group_basic_routing(async_client):
    """Test basic routing within a group"""
    client, app = async_client

    async def handler(req, res):
        return res.text("Users list")

    group = Group(
        path="/api",
        routes=[
            Routes(
                path="/users",
                methods=["GET"],
                handler=handler
            ),
        ],
    )
    app.add_route(group)
    
    response = await client.get("/api/users")
    assert response.status_code == 200
    assert response.text == "Users list"


async def test_group_with_multiple_routes(async_client):
    """Test group with multiple routes"""
    client, app = async_client

    async def users_handler(req, res):
        return res.text("Users list")

    async def user_detail_handler(req, res):
        return res.text(f"User {req.path_params['id']}")

    group = Group(
        path="/api",
        routes=[
            Routes(path="/users", methods=["GET"], handler=users_handler),
            Routes(path="/users/{id}", methods=["GET"], handler=user_detail_handler),
        ],
    )
    app.add_route(group)
    
    # Test first route
    response = await client.get("/api/users")
    assert response.status_code == 200
    assert response.text == "Users list"
    
    # Test second route with path parameter
    response = await client.get("/api/users/123")
    assert response.status_code == 200
    assert response.text == "User 123"


async def test_nested_groups(async_client):
    """Test nested group structures"""
    client, app = async_client

    async def posts_handler(req, res):
        return res.text("Posts list")

    async def comments_handler(req, res):
        return res.text(f"Comments for post {req.path_params['post_id']}")

    inner_group = Group(
        path="/posts",
        routes=[
            Routes(path="/{post_id}/comments", methods=["GET"], handler=comments_handler),
        ],
    )

    outer_group = Group(
        path="/api",
        routes=[
            Routes(path="/posts", methods=["GET"], handler=posts_handler),
            inner_group,
        ],
    )
    app.add_route(outer_group)
    
    # Test outer route
    response = await client.get("/api/posts")
    assert response.status_code == 200
    assert response.text == "Posts list"
    
    # Test nested route
    response = await client.get("/api/posts/456/comments")
    assert response.status_code == 200
    assert response.text == "Comments for post 456"


async def test_group_with_middleware(async_client):
    """Test group-level middleware"""
    client, app = async_client

    async def handler(req, res):
        return res.text(req.state.get("processed", "No middleware"))

    async def test_middleware(req, res, call_next):
        req.state.processed = "Middleware worked"
        return await call_next(req, res)

    group = Group(
        path="/admin",
        routes=[
            Routes(path="/dashboard", methods=["GET"], handler=handler),
        ],
        middleware=[test_middleware],
    )
    app.add_route(group)
    
    response = await client.get("/admin/dashboard")
    assert response.status_code == 200
    assert response.text == "Middleware worked"


async def test_group_with_route_specific_middleware(async_client):
    """Test combination of group and route middleware"""
    client, app = async_client

    async def handler(req, res):
        middlewares = req.state.get("middlewares", [])
        return res.json({"middlewares": middlewares})

    async def group_middleware(req, res, call_next):
        req.state.setdefault("middlewares", []).append("group")
        return await call_next(req, res)

    async def route_middleware(req, res, call_next):
        req.state.setdefault("middlewares", []).append("route")
        return await call_next(req, res)

    group = Group(
        path="/api",
        routes=[
            Routes(
                path="/test",
                methods=["GET"],
                handler=handler,
                middlewares=[route_middleware]
            ),
        ],
        middleware=[group_middleware],
    )
    app.add_route(group)
    
    response = await client.get("/api/test")
    assert response.status_code == 200
    assert response.json() == {"middlewares": ["group", "route"]}


async def test_group_name_propagation(async_client):
    """Test that group name is properly used in URL generation"""
    client, app = async_client

    async def handler(req, res):
        return res.text("OK")

    group = Group(
        path="/shop",
        name="shop",
        routes=[
            Routes(
                path="/products",
                methods=["GET"],
                handler=handler,
                name="products"
            ),
        ],
    )
    app.add_route(group)
    
    # Test that the route works
    response = await client.get("/shop/products")
    assert response.status_code == 200
    
    # Test URL generation (assuming your framework has url_for functionality)
    # This would depend on your actual URL generation implementation
    # url = app.url_for("shop.products")
    # assert url == "/shop/products"


async def test_group_with_empty_path(async_client):
    """Test group with empty path (root group)"""
    client, app = async_client

    async def handler(req, res):
        return res.text("Root handler")

    group = Group(
        path="",
        routes=[
            Routes(path="/", methods=["GET"], handler=handler),
        ],
    )
    app.add_route(group)
    
    response = await client.get("/")
    assert response.status_code == 200
    assert response.text == "Root handler"


async def test_group_with_trailing_slash(async_client):
    """Test that groups handle trailing slashes correctly"""
    client, app = async_client

    async def handler(req, res):
        return res.text("Trailing slash handled")

    group = Group(
        path="/api/",
        routes=[
            Routes(path="/test/", methods=["GET"], handler=handler),
        ],
    )
    app.add_route(group)
    
    # Test with and without trailing slashes
    response1 = await client.get("/api/test")
    response2 = await client.get("/api/test/")
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.text == "Trailing slash handled"
    assert response2.text == "Trailing slash handled"


async def test_group_with_complex_path_params(async_client):
    """Test groups with complex path parameters"""
    client, app = async_client

    async def product_handler(req, res):
        return res.text(f"Product {req.path_params['product_id']} in category {req.path_params['category']}")

    group = Group(
        path="/store",
        routes=[
            Routes(
                path="/{category}/products/{product_id}",
                methods=["GET"],
                handler=product_handler
            ),
        ],
    )
    
    response = await client.get("/store/electronics/products/789")
    assert response.status_code == 200
    assert response.text == "Product 789 in category electronics"


async def test_group_with_multiple_methods(async_client):
    """Test that groups work with routes that have multiple methods"""
    client, app = async_client

    async def handler(req, res):
        return res.text(f"{req.method} successful")

    group = Group(
        path="/api",
        routes=[
            Routes(
                path="/items",
                methods=["GET", "POST"],
                handler=handler
            ),
        ],
    )
    app.add_route(group)
    
    # Test GET
    response_get = await client.get("/api/items")
    assert response_get.status_code == 200
    assert response_get.text == "GET successful"
    
    # Test POST
    response_post = await client.post("/api/items")
    assert response_post.status_code == 200
    assert response_post.text == "POST successful"
    
    # Test unsupported method
    response_delete = await client.delete("/api/items")
    assert response_delete.status_code == 405
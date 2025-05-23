import pytest
from nexios.http import Request, Response
from nexios.testing import Client
from nexios.routing import Router,Group,Routes
from nexios import get_application

@pytest.fixture
async def async_client():
    app = get_application()
    async with Client(app) as c:
        yield c, app

async def test_group_basic_routing(async_client):
    """Test basic routing within a group"""
    client, app = async_client
    
    # Create a group with routes
    group = Group(
        path="/api",
        routes=[
          Routes(
            path="/users",
            methods=["GET"],
            handler=lambda req, res: res.text("Users list"),
          ),
        ]
    )
    app.add_route(group)
    
    # Test the grouped routes
    response = await client.get("/api/users")
    assert response.status_code == 200
    assert response.text == "Users list"
    
    response = await client.get("/api/posts")
    assert response.status_code == 200
    assert response.text == "Posts list"
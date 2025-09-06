from typing import Optional

import pytest
from pydantic import BaseModel, ValidationError

from nexios import NexiosApp
from nexios.testing import Client
from nexios.utils.pydantic import add_pydantic_error_handler


# Test models
class UserModel(BaseModel):
    name: str
    age: int
    email: Optional[str] = None


class ItemModel(BaseModel):
    id: int
    name: str
    price: float


# Fixtures
@pytest.fixture
def test_app():
    app = NexiosApp()
    return app


@pytest.fixture
async def client(test_app):
    async with Client(test_app) as test_client:
        yield test_client


# Test cases
class TestPydanticErrorHandling:
    async def test_flat_error_format(self, test_app, client):
        # Setup
        add_pydantic_error_handler(test_app, style="flat")

        @test_app.post("/users")
        async def create_user(request, response):
            data = await request.json
            user = UserModel(**data)
            return response.json(user.dict())

        # Test
        response = await client.post(
            "/users", json={"name": ""}  # Missing required 'age' field
        )

        assert response.status_code == 400
        data = response.json()
        assert "errors" in data
        assert "age" in data["errors"]
        assert "Field required" in data["errors"]["age"]

    async def test_list_error_format(self, test_app, client):
        # Setup
        add_pydantic_error_handler(test_app, style="list", status_code=422)

        @test_app.post("/items")
        async def create_item(request, response):
            data = await request.json
            item = ItemModel(**data)
            return response.json(item.dict())

        # Test
        response = await client.post(
            "/items", json={"id": "not_an_int"}  # Invalid type for id
        )

        assert response.status_code == 422
        data = response.json()
        assert isinstance(data["errors"], list)
        assert any("id" in str(e.get("field", "")) for e in data["errors"])
        assert any("integer" in str(e.get("message", "")) for e in data["errors"])

    async def test_nested_error_format(self, test_app, client):
        # Setup
        add_pydantic_error_handler(test_app, style="nested")

        class NestedModel(BaseModel):
            user: UserModel
            item: ItemModel

        @test_app.post("/nested")
        async def create_nested(request, response):
            data = await request.json
            nested = NestedModel(**data)
            return response.json(nested.dict())

        # Test with nested errors
        response = await client.post(
            "/nested",
            json={"user": {"name": "", "age": -1}, "item": {"id": "not_an_int"}},
        )

        assert response.status_code == 400
        data = response.json()
        if "user" in data["errors"]:
            assert "name" in data["errors"]["user"]
            assert "age" in data["errors"]["user"]

        if "item" in data["errors"]:
            assert "id" in data["errors"]["item"]
        else:
            assert False, "Expected 'item' key in errors"

    async def test_custom_status_code(self, test_app, client):
        # Setup with custom status code
        add_pydantic_error_handler(test_app, style="flat", status_code=422)

        @test_app.post("/validate")
        async def validate_data(request, response):
            data = await request.json
            user = UserModel(**data)
            return response.json(user.dict())

        # Test
        response = await client.post("/validate", json={})
        assert response.status_code == 422  # Custom status code

    async def test_valid_request(self, test_app, client):
        # Setup
        add_pydantic_error_handler(test_app)

        @test_app.post("/valid")
        async def valid_route(request, response):
            data = await request.json
            user = UserModel(**data)
            return response.json(user.dict())

        # Test valid request
        response = await client.post("/valid", json={"name": "Test User", "age": 25})

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test User"
        assert data["age"] == 25

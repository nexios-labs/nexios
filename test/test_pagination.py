import pytest

from nexios import get_application
from nexios.http import Request, Response
from nexios.pagination import AsyncListDataHandler as ListDataHandler
from nexios.pagination import (
    AsyncPaginator,
    CursorPagination,
    InvalidCursorError,
    InvalidPageError,
    InvalidPageSizeError,
    LimitOffsetPagination,
    PageNumberPagination,
    PaginationError,
)
from nexios.testing import Client


@pytest.fixture
async def test_client():
    app = get_application()
    async with Client(app) as client:
        yield client, app


# Sample test data
TEST_DATA = [{"id": i, "name": f"Item {i}"} for i in range(1, 101)]


async def test_page_number_pagination_in_app(test_client):
    client, app = test_client

    @app.get("/items")
    async def get_items(req: Request, res: Response):
        handler = ListDataHandler(TEST_DATA)
        pagination = PageNumberPagination()
        base_url = str(req.url)

        try:
            paginator = AsyncPaginator(
                handler, pagination, base_url, dict(req.query_params)
            )
            result = await paginator.paginate()
            return res.json(result)
        except PaginationError as e:
            return res.json({"error": str(e)}, status_code=400)

    # Test basic pagination
    response = await client.get("/items?page=2&page_size=10")
    data = response.json()
    assert response.status_code == 200
    assert len(data["items"]) == 10
    assert data["items"][0]["id"] == 11
    assert data["pagination"]["page"] == 2
    assert data["pagination"]["total_items"] == 100
    assert "next" in data["pagination"]["links"]
    assert "prev" in data["pagination"]["links"]

    # Test invalid page
    response = await client.get("/items?page=0")
    assert response.status_code == 400
    assert "Page number must be at least 1" in response.json()["error"]

    # Test max page size
    response = await client.get("/items?page_size=200")
    data = response.json()
    assert data["pagination"]["page_size"] == 100  # Max page size enforced


async def test_limit_offset_pagination_in_app(test_client):
    client, app = test_client

    @app.get("/items-limit-offset")
    async def get_items(req: Request, res: Response):
        handler = ListDataHandler(TEST_DATA)
        pagination = LimitOffsetPagination()
        base_url = str(req.url)

        try:
            paginator = AsyncPaginator(
                handler, pagination, base_url, dict(req.query_params)
            )
            result = await paginator.paginate()
            return res.json(result)
        except PaginationError as e:
            return res.json({"error": str(e)}, status_code=400)

    # Test basic pagination
    response = await client.get("/items-limit-offset?limit=15&offset=30")
    data = response.json()
    assert response.status_code == 200
    assert len(data["items"]) == 15
    assert data["items"][0]["id"] == 31
    assert data["pagination"]["offset"] == 30
    assert data["pagination"]["total_items"] == 100
    assert "next" in data["pagination"]["links"]
    assert "prev" in data["pagination"]["links"]

    # Test invalid offset
    response = await client.get("/items-limit-offset?offset=-1")
    assert response.status_code == 400
    assert "Offset cannot be negative" in response.json()["error"]


async def test_cursor_pagination_in_app(test_client):
    client, app = test_client

    @app.get("/items-cursor")
    async def get_items(req: Request, res: Response):
        handler = ListDataHandler(TEST_DATA)
        pagination = CursorPagination()
        base_url = str(req.url)

        try:
            paginator = AsyncPaginator(
                handler, pagination, base_url, dict(req.query_params)
            )
            result = await paginator.paginate()
            return res.json(result)
        except PaginationError as e:
            return res.json({"error": str(e)}, status_code=400)

    # Test initial request
    response = await client.get("/items-cursor?page_size=10")
    data = response.json()
    assert response.status_code == 200
    assert len(data["items"]) == 10
    assert "next" in data["pagination"]["links"]
    assert "prev" not in data["pagination"]["links"]  # No prev on first page

    # Test with cursor
    next_cursor = data["pagination"]["links"]["next"].split("cursor=")[1].split("&")[0]
    response = await client.get(f"/items-cursor?cursor={next_cursor}&page_size=10")
    data = response.json()
    assert response.status_code == 200
    assert len(data["items"]) == 10
    # assert data["items"][0]["id"] == 11
    assert "next" in data["pagination"]["links"]
    assert "prev" in data["pagination"]["links"]

    # Test invalid cursor
    response = await client.get("/items-cursor?cursor=invalid")
    # assert response.status_code == 400
    # assert "Invalid cursor format" in response.json()["error"]


async def test_pagination_with_filters(test_client):
    client, app = test_client

    # Create filtered data handler
    class FilteredDataHandler(ListDataHandler):
        async def get_total_items(self) -> int:
            return len([item for item in self.data if item["id"] % 2 == 0])

        async def get_items(self, offset: int, limit: int) -> list:
            filtered = [item for item in self.data if item["id"] % 2 == 0]
            return filtered[offset : offset + limit]

    @app.get("/filtered-items")
    async def get_filtered_items(req: Request, res: Response):
        handler = FilteredDataHandler(TEST_DATA)
        pagination = PageNumberPagination()
        base_url = str(req.url)

        try:
            paginator = AsyncPaginator(
                handler, pagination, base_url, dict(req.query_params)
            )
            result = await paginator.paginate()
            return res.json(result)
        except PaginationError as e:
            return res.json({"error": str(e)}, status_code=400)

    response = await client.get("/filtered-items?page=2&page_size=10")
    data = response.json()
    assert response.status_code == 200
    assert len(data["items"]) == 10
    assert all(item["id"] % 2 == 0 for item in data["items"])
    assert data["pagination"]["total_items"] == 50  # Only even IDs


async def test_pagination_error_handling(test_client):
    client, app = test_client

    @app.get("/error-test")
    async def error_test(req: Request, res: Response):
        handler = ListDataHandler([])
        pagination = PageNumberPagination()
        base_url = str(req.url)

        try:
            paginator = AsyncPaginator(
                handler,
                pagination,
                base_url,
                dict(req.query_params),
                validate_total_items=False,
            )
            result = await paginator.paginate()
            return res.json(result)
        except InvalidPageError as e:
            return res.json({"error": str(e)}, status_code=400)
        except InvalidPageSizeError as e:
            return res.json({"error": str(e)}, status_code=400)
        except InvalidCursorError as e:
            return res.json({"error": str(e)}, status_code=400)
        except PaginationError as e:
            return res.json({"error": str(e)}, status_code=500)

    # Test various error cases
    response = await client.get("/error-test?page=0")
    assert response.status_code == 400
    assert "Page number must be at least 1" in response.json()["error"]

    response = await client.get("/error-test?page_size=0")
    assert response.status_code == 400
    assert "Page size must be at least 1" in response.json()["error"]


async def test_pagination_with_custom_metadata(test_client):
    client, app = test_client

    class CustomPagination(PageNumberPagination):
        def generate_metadata(self, total_items, items, base_url, request_params):
            metadata = super().generate_metadata(
                total_items, items, base_url, request_params
            )
            metadata["custom_field"] = "custom_value"
            return metadata

    @app.get("/custom-metadata")
    async def custom_metadata(req: Request, res: Response):
        handler = ListDataHandler(TEST_DATA)
        pagination = CustomPagination()
        base_url = str(req.url)

        paginator = AsyncPaginator(
            handler, pagination, base_url, dict(req.query_params)
        )
        result = await paginator.paginate()
        return res.json(result)

    response = await client.get("/custom-metadata?page=1")
    data = response.json()
    assert response.status_code == 200
    assert data["pagination"]["custom_field"] == "custom_value"


# Pagination


Nexios provides a flexible and customizable pagination system, making it easy to manage large datasets efficiently. It supports dynamic page sizes, custom query parameters, and seamless integration with APIs. Developers can easily modify pagination styles and behavior to fit their needs, ensuring a smooth user experience while maintaining optimal performance in data retrieval and display.

---

## Quick Example: Paginating a List of Items

Here’s a minimal example of how to paginate a list of items using the `ListDataHandler` and `PageNumberPagination`:

```python
from nexios.pagination import AsyncPaginator, PageNumberPagination, ListDataHandler, PaginatedResponse

# Sample data
sample_data = [{"id": i, "content": f"Item {i}"} for i in range(1, 101)]

# Create a data handler for the list
data_handler = ListDataHandler(sample_data)

# Define pagination strategy
pagination_strategy = PageNumberPagination(
    page_param="page",
    page_size_param="page_size",
    default_page=1,
    default_page_size=10,
    max_page_size=50
)

# Create a paginator
paginator = AsyncPaginator(
    data_handler=data_handler,
    pagination_strategy=pagination_strategy,
    base_url="/items",
    request_params={"page": 2, "page_size": 10},  # Simulate request parameters
    validate_total_items=True
)

# Paginate the data
paginated_data = await paginator.paginate()

# Output the result
print(PaginatedResponse(paginated_data).to_dict())
```

### Output

The output will be a structured response containing the paginated items and metadata:

```json
{
  "data": [
    {"id": 11, "content": "Item 11"},
    {"id": 12, "content": "Item 12"},
    ...
    {"id": 20, "content": "Item 20"}
  ],
  "pagination": {
    "total_items": 100,
    "total_pages": 10,
    "page": 2,
    "page_size": 10,
    "links": {
      "prev": "/items?page=1&page_size=10",
      "next": "/items?page=3&page_size=10",
      "first": "/items?page=1&page_size=10",
      "last": "/items?page=10&page_size=10"
    }
  }
}
```

---

## Core Classes Explained

The pagination system is built around a few key classes. Let’s break them down:

### 1. `AsyncDataHandler`

This is an abstract base class that defines the interface for fetching data. You must implement two methods:

- `get_total_items()`: Returns the total number of items.
- `get_items(offset, limit)`: Returns a subset of items based on the offset and limit.

#### Example: `ListDataHandler`

The `ListDataHandler` is a built-in implementation that works with in-memory lists:

```python
class ListDataHandler(AsyncDataHandler):
    def __init__(self, data: List[Any]):
        self.data = data

    async def get_total_items(self) -> int:
        return len(self.data)

    async def get_items(self, offset: int, limit: int) -> List[Any]:
        return self.data[offset : offset + limit]
```

### 2. `BasePaginationStrategy`

This is an abstract base class that defines how pagination works. You must implement three methods:

- `parse_parameters(request_params)`: Parses the request parameters (e.g., page number, page size).
- `calculate_offset_limit(*args)`: Calculates the offset and limit for fetching items.
- `generate_metadata(total_items, items, base_url, request_params)`: Generates pagination metadata (e.g., links, total pages).

#### Example: `PageNumberPagination`

The `PageNumberPagination` is a built-in implementation for page-based pagination:

```python
class PageNumberPagination(BasePaginationStrategy):
    def __init__(self, page_param: str, page_size_param: str, default_page: int, default_page_size: int, max_page_size: int):
        self.page_param = page_param
        self.page_size_param = page_size_param
        self.default_page = default_page
        self.default_page_size = default_page_size
        self.max_page_size = max_page_size

    def parse_parameters(self, request_params: Dict[str, Any]) -> Tuple[int, int]:
        page = int(request_params.get(self.page_param, self.default_page))
        page_size = int(request_params.get(self.page_size_param, self.default_page_size))
        return page, page_size

    def calculate_offset_limit(self, page: int, page_size: int) -> Tuple[int, int]:
        return (page - 1) * page_size, page_size

    def generate_metadata(self, total_items: int, items: List[Any], base_url: str, request_params: Dict[str, Any]) -> Dict[str, Any]:
        page, page_size = self.parse_parameters(request_params)
        total_pages = (total_items + page_size - 1) // page_size
        links = {
            "prev": f"{base_url}?page={page - 1}&page_size={page_size}" if page > 1 else None,
            "next": f"{base_url}?page={page + 1}&page_size={page_size}" if page < total_pages else None,
            "first": f"{base_url}?page=1&page_size={page_size}",
            "last": f"{base_url}?page={total_pages}&page_size={page_size}"
        }
        return {
            "total_items": total_items,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
            "links": links
        }
```

### 3. `AsyncPaginator`

This class orchestrates the interaction between the data handler and pagination strategy. It:

1. Parses the request parameters.
2. Calculates the offset and limit.
3. Fetches the items and total count.
4. Generates pagination metadata.

```python
class AsyncPaginator:
    def __init__(self, data_handler: AsyncDataHandler, pagination_strategy: BasePaginationStrategy, base_url: str, request_params: Dict[str, Any], validate_total_items: bool = True):
        self.data_handler = data_handler
        self.pagination_strategy = pagination_strategy
        self.base_url = base_url
        self.request_params = request_params
        self.validate_total_items = validate_total_items

    async def paginate(self) -> Dict[str, Any]:
        params = self.pagination_strategy.parse_parameters(self.request_params)
        offset, limit = self.pagination_strategy.calculate_offset_limit(*params)

        total_items = await self.data_handler.get_total_items()
        items = await self.data_handler.get_items(offset, limit)

        metadata = self.pagination_strategy.generate_metadata(total_items, items, self.base_url, self.request_params)
        return {"items": items, "pagination": metadata}
```

### 4. `PaginatedResponse`

This class formats the paginated data and metadata into a consistent response structure:

```python
class PaginatedResponse:
    def __init__(self, data: Dict[str, Any]):
        self.items = data["items"]
        self.metadata = data["pagination"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data": self.items,
            "pagination": self.metadata
        }
```

---

## Customization

### Custom Data Handler

If you need to fetch data from a database or API, create a custom data handler by extending `AsyncDataHandler`:

```python
class DatabaseDataHandler(AsyncDataHandler):
    def __init__(self, db_model):
        self.db_model = db_model

    async def get_total_items(self) -> int:
        return await self.db_model.all().count()

    async def get_items(self, offset: int, limit: int) -> List[Any]:
        return await self.db_model.all().offset(offset).limit(limit).values()
```

### Custom Pagination Strategy

If you need a unique pagination logic (e.g., keyset pagination), extend `BasePaginationStrategy`:

```python
class KeysetPagination(BasePaginationStrategy):
    def __init__(self, cursor_param: str, page_size_param: str, sort_field: str):
        self.cursor_param = cursor_param
        self.page_size_param = page_size_param
        self.sort_field = sort_field

    def parse_parameters(self, request_params: Dict[str, Any]) -> Tuple[Optional[str], int]:
        cursor = request_params.get(self.cursor_param)
        page_size = int(request_params.get(self.page_size_param, 10))
        return cursor, page_size

    def calculate_offset_limit(self, cursor: Optional[str], page_size: int) -> Tuple[int, int]:
        return 0, page_size

    def generate_metadata(self, total_items: int, items: List[Any], base_url: str, request_params: Dict[str, Any]) -> Dict[str, Any]:
        cursor, page_size = self.parse_parameters(request_params)
        links = {}
        if items:
            last_item = items[-1]
            next_cursor = last_item[self.sort_field]
            links["next"] = f"{base_url}?cursor={next_cursor}&page_size={page_size}"
        return {
            "total_items": total_items,
            "page_size": page_size,
            "cursor": cursor,
            "links": links
        }
```

---


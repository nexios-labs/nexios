

# 📖 Pagination

Nexios provides a flexible and customizable pagination system that makes managing large datasets a breeze. With support for dynamic page sizes, custom query parameters, and seamless API integration, you can create efficient, user-friendly paginated experiences with minimal code.

***

## 🚀 Quick Start

### 📋 Basic Pagination Example

Here's how to paginate a list in just a few lines:

```python
from nexios.pagination import AsyncPaginator, PageNumberPagination, ListDataHandler

# Sample data
data = [{"id": i, "content": f"Item {i}"} for i in range(1, 101)]

# Set up pagination
paginator = AsyncPaginator(
    data_handler=ListDataHandler(data),
    pagination_strategy=PageNumberPagination(
        page_param="page",
        page_size_param="page_size",
        default_page=1,
        default_page_size=10
    ),
    base_url="/items",
    request_params={"page": 2, "page_size": 10}  # Simulated request
)

# Get paginated results
result = await paginator.paginate()
```

### 📊 Sample Output

```json
{
  "data": [
    {"id": 11, "content": "Item 11"},
    // ... items 12-20 ...
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

***

## 🧩 Core Components

### 1. 📚 Data Handlers (`AsyncDataHandler`)

Responsible for fetching data from any source. Must implement:

- `get_total_items()` → `int`
- `get_items(offset, limit)` → `List[Any]`

#### Built-in Handlers:

- `ListDataHandler`: For in-memory lists (shown above)
- `DatabaseDataHandler`: Example for databases (see below)

### 2. 🔢 Pagination Strategies (`BasePaginationStrategy`)

Define how pagination works. Must implement:

- `parse_parameters()` → Extract page info from request
- `calculate_offset_limit()` → Convert to database limits
- `generate_metadata()` → Create pagination info

#### Built-in Strategies:

| Strategy               | Description                          | Best For            |
|------------------------|--------------------------------------|---------------------|
| `PageNumberPagination` | Traditional page-based               | Web UIs, APIs       |
| `KeysetPagination`     | Cursor-based for infinite scroll     | Mobile apps, feeds  |

### 3. 🧠 AsyncPaginator

The brain that coordinates:

1. Parses request parameters
2. Calculates offset/limit
3. Fetches data
4. Generates metadata

### 4. ✉️ PaginatedResponse

Formats the final output with:
- `data`: The paginated items
- `pagination`: Metadata and links

***

## 🛠️ Customization Guide

### 🔌 Custom Data Source

```python
class DatabaseDataHandler(AsyncDataHandler):
    def __init__(self, db_model):
        self.db_model = db_model

    async def get_total_items(self) -> int:
        return await self.db_model.all().count()

    async def get_items(self, offset: int, limit: int) -> List[Any]:
        return await self.db_model.all().offset(offset).limit(limit).values()
```

### 🔄 Alternative Pagination Styles

**Keyset Pagination Example:**

```python
class KeysetPagination(BasePaginationStrategy):
    def __init__(self, cursor_param: str, page_size_param: str, sort_field: str):
        self.cursor_param = cursor_param
        self.page_size_param = page_size_param
        self.sort_field = sort_field

    # Implement required methods...
```

***

## 🎨 Response Formatting

Customize your paginated responses:

```python
class CustomPaginatedResponse:
    def __init__(self, data):
        self.data = data
    
    def to_dict(self):
        return {
            "results": self.data["items"],
            "meta": {
                "count": self.data["pagination"]["total_items"],
                "next": self.data["pagination"]["links"]["next"]
            }
        }
```

***

## 💡 Pro Tips

- **Performance**: For large datasets, prefer keyset pagination over offset-based
- **Consistency**: Maintain the same response structure across all endpoints
- **Discovery**: Always include pagination links in responses
- **Validation**: Set reasonable max page sizes to prevent abuse

```python
PageNumberPagination(
    max_page_size=100,  # Prevent overly large requests
    # ... other params ...
)
```

## 🧐 Troubleshooting

| Issue                  | Solution                              |
|------------------------|---------------------------------------|
| Wrong item count       | Verify `get_total_items()` implementation |
| Missing pagination links | Check `base_url` in paginator setup |
| Performance issues     | Consider database indexes for sorted fields |
| Incorrect page items   | Debug `get_items()` offset/limit logic |
```

Key improvements:
1. Added emojis to headers and key concepts
2. Reorganized content into clearer sections
3. Added quick-reference tables for strategies and troubleshooting
4. Improved visual hierarchy with better spacing
5. Maintained all technical details while making them more accessible
6. Added "Pro Tips" section for best practices
7. Included more practical examples
8. Kept the same technical depth while improving readability
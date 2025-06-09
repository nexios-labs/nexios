# Day 4: Class-Based Views with APIHandler

## Using APIHandler

APIHandler provides a class-based approach to organizing route handlers:

```python
from nexios import get_application
from nexios.handlers import APIHandler
from nexios.http import Request, Response

app = get_application()

class UserHandler(APIHandler):
    async def get(self,request: Request, response: Response) -> Response:
        """Handle GET requests"""
        return {"message": "Get users"}
    
    async def post(self, request: Request, response: Response) -> Response:
        """Handle POST requests"""
        data = await request.json()
        return {"message": "User created", "data": data}
    
    async def put(self, request: Request, response: Response) -> Response:
        """Handle PUT requests"""
        data = await request.json()
        return {"message": "User updated", "data": data}
    
    async def delete(self, request: Request, response: Response) -> Response:
        """Handle DELETE requests"""
        return {"message": "User deleted"}

app.add_route(UserHandler.as_route("/users"))
```

## Method Handlers

Each HTTP method maps to a corresponding handler method:

```python
class ItemHandler(APIHandler):
    async def get(self, request: Request) -> Response:
        """List items or get single item"""
        item_id = request.path_params.get("item_id")
        if item_id:
            return {"item": f"Item {item_id}"}
        return {"items": ["item1", "item2"]}
    
    async def post(self, request: Request) -> Response:
        """Create new item"""
        data = await request.json()
        return {
            "message": "Item created",
            "item": data
        }
    
    async def put(self, request: Request) -> Response:
        """Update existing item"""
        item_id = request.path_params["item_id"]
        data = await request.json()
        return {
            "message": f"Item {item_id} updated",
            "item": data
        }
    
    async def delete(self, request: Request) -> Response:
        """Delete item"""
        item_id = request.path_params["item_id"]
        return {
            "message": f"Item {item_id} deleted"
        }

# Register with path parameters
app.add_route(ItemHandler.as_route("/items/{item_id:int}"))
```

## Structured Responses

Using structured responses with APIHandler:

```python
from typing import List, Optional
from pydantic import BaseModel

# Data models
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float

class ItemHandler(APIHandler):
    items: List[Item] = []  # In-memory storage
    
    async def get(self,request: Request, response: Response) -> Response:
        """Return items with proper structure"""
        return response.json({
            "total": len(self.items),
            "items": [item.dict() for item in self.items]
        })
    
    async def post(self,request: Request, response: Response) -> Response:
        """Create item with validation"""
        data = await request.json
        item = Item(**data)
        self.items.append(item)
        return {
            "message": "Item created",
            "item": item.dict()
        }

app.add_route(ItemHandler.as_route("/items"))
```



## Practice Exercise

Create a complete CRUD API for a blog using class-based views:

1. Post handler with:
   - List all posts
   - Get single post
   - Create post
   - Update post
   - Delete post

2. Comment handler with:
   - List post comments
   - Add comment
   - Update comment
   - Delete comment

## Additional Resources
- [Class-Based Views Guide](../../guide/class-based-handlers.md)
- [Handler Lifecycle](../../guide/)
- [Response Patterns](https://nexios.dev/guide/responses)
- [Dependency Injection](https://nexios.dev/guide/dependencies)

##  Next Steps
Tomorrow in [Day 5: Middleware in Nexios](../day05/index.md), we'll explore:
- Built-in middleware
- Custom middleware
- Global vs route-specific middleware
- Middleware ordering
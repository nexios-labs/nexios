# Day 4: Class-Based Views – Organizing Your API Like a Pro

Welcome to Day 4! Today, we'll learn how to organize your Nexios app using **class-based views** with `APIHandler`. This is like moving from a messy desk to a well-organized office: everything has its place, and your code becomes easier to manage as your app grows.

---

## Why Class-Based Views?

Imagine you're running a business. If you handle every customer request yourself, things get messy fast. But if you have a system—like a front desk, a billing department, and a support team—everything runs smoother.

Class-based views let you group related logic (like GET, POST, PUT, DELETE for a resource) into a single class. This keeps your code DRY (Don't Repeat Yourself) and organized.

---

## 1. Getting Started with APIHandler

`APIHandler` is Nexios's way of letting you write class-based views. Each HTTP method (GET, POST, etc.) becomes a method on your class.

```python
from nexios import get_application
from nexios.handlers import APIHandler
from nexios.http import Request, Response

app = get_application()

class UserHandler(APIHandler):
    async def get(self, request: Request, response: Response):
        """Handle GET requests"""
        return {"message": "Get users"}

    async def post(self, request: Request, response: Response):
        """Handle POST requests"""
        data = await request.json()
        return {"message": "User created", "data": data}

app.add_route(UserHandler.as_route("/users"))
```

**Learning Moment:**
- Each method (`get`, `post`, etc.) handles a different HTTP verb for the same resource.
- This keeps all logic for `/users` in one place.

> **Why does this matter?**
> As your app grows, class-based views make it easier to add features, maintain code, and avoid duplication.

---

## 2. Handling Path Parameters and Multiple Methods

You can use path parameters and handle multiple actions in one class:

```python
class ItemHandler(APIHandler):
    async def get(self, request: Request, response: Response):
        item_id = request.path_params.get("item_id")
        if item_id:
            return {"item": f"Item {item_id}"}
        return {"items": ["item1", "item2"]}

    async def put(self, request: Request, response: Response):
        item_id = request.path_params["item_id"]
        data = await request.json()
        return {"message": f"Item {item_id} updated", "item": data}

    async def delete(self, request: Request, response: Response):
        item_id = request.path_params["item_id"]
        return {"message": f"Item {item_id} deleted"}

app.add_route(ItemHandler.as_route("/items/{item_id:int}"))
```

**Learning Moment:**
- All logic for `/items/{item_id}` is grouped together.
- You can easily add more methods (PATCH, OPTIONS, etc.) as needed.

---

## 3. Using Data Models for Structure

For real-world APIs, you'll want to validate and structure your data. Nexios supports Pydantic models for this.

```python
from typing import List, Optional
from pydantic import BaseModel

class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float

class ItemHandler(APIHandler):
    items: List[Item] = []  # In-memory storage

    async def get(self, request: Request, response: Response):
        return response.json({
            "total": len(self.items),
            "items": [item.dict() for item in self.items]
        })

    async def post(self, request: Request, response: Response):
        data = await request.json()
        item = Item(**data)
        self.items.append(item)
        return {"message": "Item created", "item": item.dict()}

app.add_route(ItemHandler.as_route("/items"))
```

**Learning Moment:**
- Pydantic models help you validate and document your API data.
- You can use them for both input (validation) and output (serialization).

---

## Real-World Example: Blog CRUD

Let's say you want to build a blog API. You can create a `PostHandler` and a `CommentHandler`, each as a class-based view, to keep your code organized.

- `PostHandler`: Handles listing, creating, updating, and deleting blog posts.
- `CommentHandler`: Handles comments for each post.

**Why does this matter?**
> This approach scales as your app grows—just add more handler classes for new resources!

---

## Practice: Build a Class-Based Blog API

**Try this:**
1. Create a `PostHandler` class with methods for:
   - Listing all posts
   - Getting a single post
   - Creating, updating, and deleting posts
2. Create a `CommentHandler` for managing comments on posts.
3. Use Pydantic models for validation.
4. Register your handlers with the app using `add_route`.

**Reflection:**
- How does this structure help you keep your code organized?
- What would be harder if you used only function-based views?

---

## Additional Resources
- [Class-Based Views Guide](../../guide/class-based-handlers.md)
- [Handler Lifecycle](../../guide/)
- [Response Patterns](https://nexios.dev/guide/responses)
- [Dependency Injection](https://nexios.dev/guide/dependencies)

## Next Steps
Tomorrow in [Day 5: Middleware in Nexios](../day05/index.md), we'll explore:
- Built-in middleware
- Custom middleware
- Global vs route-specific middleware
- Middleware ordering
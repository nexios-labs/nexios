# Day 2: Routing in Nexios

## Route Decorators

Nexios provides intuitive decorators for handling different HTTP methods:

```python
from nexios import NexiosApp
from nexios.http import Reqeust, Response
app = NexiosApp()

@app.get("/users")
async def get_users(request: Request, response: Response):
    return {"users": ["user1", "user2"]}

@app.post("/users")
async def create_user(request: Request, response: Response):
    return {"message": "User created"}

@app.put("/users/{user_id}")
async def update_user(request: Request, response: Response, user_id: int):
    return {"message": f"User {user_id} updated"}

@app.delete("/users/{user_id}")
async def delete_user(request: Request, response: Response, user_id: int):
    return {"message": f"User {user_id} deleted"}
```

## Path Parameters

Nexios supports various types of path parameters:

```python
# String parameter
@app.get("/users/{username}")
async def get_user_by_name(request: Request, response: Response, username: str):
    return {"username": username}

# Integer parameter
@app.get("/posts/{post_id:int}")
async def get_post(request: Request, response: Response, post_id: int):
    return {"post_id": post_id}

# Path parameter (matches full path)
@app.get("/files/{file_path:path}")
async def serve_file(request: Request, response: Response,file_path: str):
    return {"file": file_path}

# Multiple parameters
@app.get("/users/{user_id}/posts/{post_id}")
async def get_user_post(request: Request, response: Response,user_id: int, post_id: int):
    return {
        "user_id": user_id,
        "post_id": post_id
    }
```

## Query Parameters

Handle URL query parameters easily:

```python
from typing import Optional

@app.get("/search")
async def search_items(
    request: Request, response: Response
):
    query = request.query_params.get("query")
    category = request.query_params.get("category")
    limit = request.query_params.get("limit")

    return {
        "query": query,
        "category": category,
        "limit": limit
    }

# Example URL: /search?query=nexios&category=framework&limit=5
```

## Modular Route Organization

### Using Router Classes

```python
from nexios import Router

# Create a router instance
user_router = Router(prefix="/users")

@user_router.get("/")
async def list_users(request: Request, response: Response):
    return {"users": ["user1", "user2"]}

@user_router.get("/{user_id}")
async def get_user(request: Request, response: Response,user_id: int):
    return {"user_id": user_id}

# Include router in main app
app = NexiosApp()
app.mount_router(user_router)
```

### Organizing Routes by Feature

```
my-project/
├── app/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── posts.py
│   │   └── auth.py
│   └── main.py
```

Example `routes/users.py`:
```python
from nexios import Router

router = Router(prefix="/users")

@router.get("/")
async def list_users():
    return {"users": ["user1", "user2"]}

@router.post("/")
async def create_user():
    return {"message": "User created"}
```

Example `main.py`:
```python
from nexios import NexiosApp
from .routes import users, posts, auth

app = NexiosApp()

# Include all routers
app.mount_router(users.router)
app.mount_router(posts.router)
app.mount_router(auth.router)
```

##  Practice Exercise

Create a simple blog API with these routes:

1. Posts endpoints:
   ```python
   # GET /posts - List all posts
   # GET /posts/{post_id} - Get single post
   # POST /posts - Create new post
   # PUT /posts/{post_id} - Update post
   # DELETE /posts/{post_id} - Delete post
   ```

2. Comments endpoints:
   ```python
   # GET /posts/{post_id}/comments - List comments
   # POST /posts/{post_id}/comments - Add comment
   # DELETE /posts/{post_id}/comments/{comment_id} - Delete comment
   ```

## Additional Resources
- [Nexios Routing Guide](../../guide/routing.md)
- [Path Parameters](../../guide/request-info.md)
- [Query Parameters](../../guide/request-info.md)
- [Router Class](../../guide/routers-and-subapps.md)

## Next Steps
Tomorrow in [Day 3: Async, Request, and Response](../day03/index.md), we'll explore:
- Async function support
- Working with Request objects
- Response handling
- Headers and status codes
- JSON responses 
# Day 2: First Application & Routing

Welcome to Day 2 of our Nexios journey! Today, we'll dive deep into routing patterns and request handling.

## Advanced Routing Concepts

### 1. Route Parameters

Nexios supports various types of route parameters:

```python
from nexios import NexiosApp
from nexios.http import Request, Response

app = NexiosApp()

# Basic string parameter
@app.get("/users/{username}")
async def get_user(request: Request, response: Response):
    username = request.path_params.username
    return response.json({"username": username})

# Integer parameter with type hint
@app.get("/posts/{post_id:int}")
async def get_post(request: Request, response: Response):
    post_id = request.path_params.post_id  # Automatically converted to int
    return response.json({"post_id": post_id})

# Path parameter (matches entire remaining path)
@app.get("/files/{filepath:path}")
async def serve_file(request: Request, response: Response):
    filepath = request.path_params.filepath
    return response.json({"file": filepath})
```

### 2. HTTP Methods

Nexios supports all standard HTTP methods:

```python
# GET request
@app.get("/items")
async def list_items(request: Request, response: Response):
    return response.json({"items": []})

# POST request
@app.post("/items")
async def create_item(request: Request, response: Response):
    data = await request.json()
    return response.json(data, status_code=201)

# PUT request
@app.put("/items/{item_id}")
async def update_item(request: Request, response: Response):
    item_id = request.path_params.item_id
    data = await request.json()
    return response.json({"id": item_id, **data})

# DELETE request
@app.delete("/items/{item_id}")
async def delete_item(request: Request, response: Response):
    item_id = request.path_params.item_id
    return response.status(204)
```

### 3. Route Groups

Organize your routes using the Router class:

```python
from nexios.routing import Router

# Create a router with prefix
api_v1 = Router(prefix="/api/v1")

@api_v1.get("/users")
async def get_users(request: Request, response: Response):
    return response.json({"users": []})

@api_v1.post("/users")
async def create_user(request: Request, response: Response):
    data = await request.json()
    return response.json(data, status_code=201)

# Add router to application
app.include_router(api_v1)
```

## Request Handling

### 1. Query Parameters

```python
@app.get("/search")
async def search(request: Request, response: Response):
    query = request.query_params.get("q", "")
    limit = int(request.query_params.get("limit", "10"))
    return response.json({
        "query": query,
        "limit": limit,
        "results": []
    })
```

### 2. Request Body

```python
@app.post("/users")
async def create_user(request: Request, response: Response):
    # JSON data
    data = await request.json()
    
    # Form data
    form = await request.form()
    
    # Files
    files = await request.files()
    
    return response.json({"status": "created"}, status_code=201)
```

### 3. Headers

```python
@app.get("/protected")
async def protected_route(request: Request, response: Response):
    auth_token = request.headers.get("Authorization")
    if not auth_token:
        return response.json(
            {"error": "Unauthorized"}, 
            status_code=401
        )
    return response.json({"status": "authenticated"})
```

## Class-Based Views

Nexios supports class-based views for organizing related endpoints:

```python
from nexios.views import APIView

class UserView(APIView):
    async def get(self, request: Request, response: Response):
        return response.json({"users": []})
    
    async def post(self, request: Request, response: Response):
        data = await request.json()
        return response.json(data, status_code=201)
    
    async def put(self, request: Request, response: Response):
        data = await request.json()
        return response.json(data)
    
    async def delete(self, request: Request, response: Response):
        return response.status(204)

# Register the view
app.add_route("/users", UserView.as_route())
```

## Exercises

1. **Basic Routing**:
   Create routes for a blog API with the following endpoints:
   - GET `/posts` - List all posts
   - GET `/posts/{post_id}` - Get a specific post
   - POST `/posts` - Create a new post
   - PUT `/posts/{post_id}` - Update a post
   - DELETE `/posts/{post_id}` - Delete a post

2. **Query Parameters**:
   Implement a search endpoint that accepts:
   - `q` - Search query
   - `category` - Filter by category
   - `sort` - Sort direction (asc/desc)
   - `limit` - Number of results
   - `page` - Page number

3. **Route Groups**:
   Create an API with versioned endpoints:
   - `/api/v1/users`
   - `/api/v1/posts`
   - `/api/v2/users`
   - `/api/v2/posts`

## Mini-Project: Task Manager API

Create a simple task manager API with the following features:

```python
from nexios import NexiosApp
from nexios.http import Request, Response
from nexios.routing import Router

app = NexiosApp()
api = Router(prefix="/api")

# In-memory storage
tasks = []

@api.get("/tasks")
async def list_tasks(request: Request, response: Response):
    status = request.query_params.get("status")
    if status:
        filtered = [t for t in tasks if t["status"] == status]
        return response.json(filtered)
    return response.json(tasks)

@api.post("/tasks")
async def create_task(request: Request, response: Response):
    data = await request.json()
    task = {
        "id": len(tasks) + 1,
        "title": data["title"],
        "description": data.get("description", ""),
        "status": "pending"
    }
    tasks.append(task)
    return response.json(task, status_code=201)

@api.get("/tasks/{task_id:int}")
async def get_task(request: Request, response: Response):
    task_id = request.path_params.task_id
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return response.json(
            {"error": "Task not found"}, 
            status_code=404
        )
    return response.json(task)

@api.put("/tasks/{task_id:int}")
async def update_task(request: Request, response: Response):
    task_id = request.path_params.task_id
    data = await request.json()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return response.json(
            {"error": "Task not found"}, 
            status_code=404
        )
    task.update(data)
    return response.json(task)

@api.delete("/tasks/{task_id:int}")
async def delete_task(request: Request, response: Response):
    task_id = request.path_params.task_id
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return response.json(
            {"error": "Task not found"}, 
            status_code=404
        )
    tasks.remove(task)
    return response.status(204)

app.include_router(api)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000, reload=True)
```

## Key Concepts Learned

- Route parameters and types
- HTTP methods and handlers
- Query parameters
- Request body handling
- Headers management
- Class-based views
- Route grouping
- API versioning

## Additional Resources

- [Nexios Routing Documentation](https://nexios.dev/guide/routing)
- [Request Handling Guide](https://nexios.dev/guide/request)
- [Response Types](https://nexios.dev/guide/response)
- [API Examples](https://nexios.dev/examples)

## Homework

1. Extend the Task Manager API:
   - Add task categories
   - Implement task priorities
   - Add due dates
   - Create task comments

2. Create a simple blog API with:
   - Posts
   - Categories
   - Tags
   - Comments

3. Read about:
   - Request validation
   - Error handling
   - Middleware
   
## Next Steps

Tomorrow, we'll explore request handling and responses in more detail in [Day 3: Request Handling & Responses](../day03/index.md). 
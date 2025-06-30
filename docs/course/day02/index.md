# Day 2: Understanding Routing in Nexios – Your App's GPS

Welcome to Day 2! Today, we'll explore one of the most fundamental concepts in web development: **routing**. Think of routing as your app's GPS—it decides how incoming requests are mapped to the right code, just like a GPS maps you to your destination.

## Why Routing Matters

When you visit a website or use an API, you're really just sending a request to a specific address (URL). Routing is how your app knows what to do when someone visits `/`, `/about`, or `/users/42`. Without routing, your app wouldn't know how to respond to different URLs!

---

## 1. Route Decorators: The Basics

In Nexios, you define routes using **decorators**. Decorators are like signposts that tell Nexios, "When a request comes to this URL, run this function."

### Example: A Simple User API

```python
from nexios import NexiosApp
from nexios.http import Request, Response

app = NexiosApp()

@app.get("/users")
async def get_users(request: Request, response: Response):
    # This function runs when someone visits /users with a GET request
    return {"users": ["user1", "user2"]}

@app.post("/users")
async def create_user(request: Request, response: Response):
    # This function runs when someone sends a POST request to /users
    return {"message": "User created"}
```

**Learning Moment:**
- `@app.get("/users")` means "run this function for GET requests to /users."
- `@app.post("/users")` means "run this function for POST requests to /users."

> **Why does this matter?**
> Each HTTP method (GET, POST, PUT, DELETE) is used for a different purpose. GET is for fetching data, POST is for creating, PUT is for updating, and DELETE is for deleting.

---

## 2. Path Parameters: Making Routes Dynamic

What if you want to get a specific user, like `/users/alice`? That's where **path parameters** come in. They let you capture parts of the URL as variables.

```python
@app.get("/users/{username}")
async def get_user_by_name(request: Request, response: Response, username: str):
    # username will be whatever is in the URL, e.g., 'alice' in /users/alice
    return {"username": username}
```

You can also specify types:
```python
@app.get("/posts/{post_id:int}")
async def get_post(request: Request, response: Response, post_id: int):
    return {"post_id": post_id}
```

**Learning Moment:**
- Path parameters make your API flexible and RESTful.
- You can have multiple parameters, e.g., `/users/{user_id}/posts/{post_id}`.

> **Why does this matter?**
> This is how you build APIs that can handle lots of different resources without writing a new function for every possible URL.

---

## 3. Query Parameters: Optional Info in the URL

Sometimes you want to pass extra info, like filters or search terms, without changing the route. That's what **query parameters** are for. They come after a `?` in the URL, like `/search?query=python&limit=10`.

```python
@app.get("/search")
async def search_items(request: Request, response: Response):
    query = request.query_params.get("query")
    limit = request.query_params.get("limit")
    return {"query": query, "limit": limit}
```

**Learning Moment:**
- Query parameters are always strings, so convert them if you need numbers.
- They're great for searches, filters, and pagination.

> **Why does this matter?**
> Query parameters let users customize what data they get, without needing a new route for every option.

---

## 4. Organizing Routes: Routers and Structure

As your app grows, you'll want to organize your routes. Nexios lets you group related routes using **Router** classes.

```python
from nexios import Router

user_router = Router(prefix="/users")

@user_router.get("/")
async def list_users(request: Request, response: Response):
    return {"users": ["user1", "user2"]}

@user_router.get("/{user_id}")
async def get_user(request: Request, response: Response, user_id: int):
    return {"user_id": user_id}

app = NexiosApp()
app.mount_router(user_router)
```

**Learning Moment:**
- Routers help you keep your code clean and modular.
- You can put each router in its own file for big projects.

> **Why does this matter?**
> Good organization makes your code easier to maintain and scale as your app grows.

---

## 5. Real-World Example: Blog API

Let's imagine you're building a blog. Here's how you might organize your routes:

- `/posts` – List all posts (GET), create a post (POST)
- `/posts/{post_id}` – Get, update, or delete a specific post
- `/posts/{post_id}/comments` – List or add comments

**Example:**
```python
@app.get("/posts")
async def list_posts(request, response):
    return {"posts": ["Post 1", "Post 2"]}

@app.get("/posts/{post_id}")
async def get_post(request, response, post_id: int):
    return {"post_id": post_id}

@app.post("/posts")
async def create_post(request, response):
    return {"message": "Post created"}
```

---

## Practice: Build Your Own Mini-API

**Try this:**
1. Create endpoints for posts and comments as described above.
2. Use path and query parameters to make your API flexible.
3. Organize your routes using routers if you want a challenge.

**Reflection:**
- What happens if you visit a route that doesn't exist?
- How would you add pagination to your `/posts` endpoint?

---

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
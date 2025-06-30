# Day 3: Async, Request, and Response - The Core of Communication

On Day 2, we learned how to create roadmaps for our app with routing. Today, we're diving into the traffic that travels on those roads: the `Request` and `Response` objects. We'll also explore the "superpower" that makes Nexios so fast: **asynchronous programming**.

## 1. Async: The Secret to High Performance

Imagine a chef in a kitchen. A synchronous (normal) chef would cook one dish at a time: chop all vegetables, then boil water, then cook the pasta. An **asynchronous** chef is smarter: they start boiling the water, and while it's heating up, they chop the vegetables.

This is exactly what `async` does for your Nexios app. Instead of waiting for slow operations (like reading a file or querying a database), it can handle other requests in the meantime.

### How it Looks in Nexios:

```python
import asyncio
from nexios import NexiosApp
from nexios.http import Request, Response

app = NexiosApp()

@app.get("/slow")
async def slow_endpoint(request: Request, response: Response):
    # Simulate a slow database query that takes 1 second
    await asyncio.sleep(1)
    return {"message": "Finally, I'm done!"}
```

**Learning Moment:**
- The `async def` syntax tells Python this function can be "paused" and "resumed."
- `await` is the keyword that actually pauses the function, allowing other tasks to run.

> **Why does this matter?**
> Async allows your server to handle thousands of simultaneous connections efficiently, making your app fast and scalable, even when dealing with slow operations.

---

## 2. The `Request` Object: Unpacking the User's Message

Every time a user accesses one of your routes, Nexios packs all the information about their request into a `Request` object. Think of it as a detailed letter from the user.

You can inspect this object to learn everything you need to know.

```python
@app.get("/request-demo")
async def request_demo(request: Request, response: Response):
    # Let's inspect the "letter" from the user
    return {
        "http_method": request.method,         # e.g., "GET" or "POST"
        "url_visited": str(request.url),       # The full URL
        "user_headers": dict(request.headers), # Headers like User-Agent
        "query_params": dict(request.query_params), # From the URL, e.g., ?name=John
        "user_ip": request.client.host       # The user's IP address
    }
```

### Getting Data from the Request Body
For `POST` or `PUT` requests, the user often sends data (like a JSON payload or form data) in the request body. You can `await` these methods to get the data.

```python
@app.post("/users")
async def create_user(request: Request, response: Response):
    # Get the JSON data sent by the user
    user_data = await request.json()
    
    # Now you can use the data
    return {"message": f"User {user_data['name']} created!"}
```

> **Why does this matter?**
> The `Request` object is your gateway to understanding what the user wants. You'll use it to get authentication tokens from headers, data from the body, and more.

---

## 3. The `Response` Object: Crafting Your Reply

Once you've processed the request, it's time to send a reply. The `Response` object is what you use to build that reply. You can control everything: the body, the status code, and the headers.

### Controlling the Status Code
Status codes are crucial for APIs. They tell the client application whether the request was successful, if there was an error, or if they need to do something else.

```python
from nexios import status

@app.post("/items")
async def create_item(request: Request, response: Response):
    # Some logic to create an item...
    new_item = {"id": 123, "name": "A new item"}
    
    # 201 CREATED is the correct status code for a successful creation
    return response.json(new_item, status_code=status.HTTP_201_CREATED)

@app.get("/item/999")
async def get_nonexistent_item(request: Request, response: Response):
    # 404 NOT FOUND tells the client this resource doesn't exist
    return response.json(
        {"error": "Item not found"},
        status_code=status.HTTP_404_NOT_FOUND
    )
```

**Common Status Codes:**
- `200 OK`: Standard success response.
- `201 CREATED`: An item was successfully created.
- `400 BAD REQUEST`: The user sent invalid data.
- `404 NOT FOUND`: The requested resource doesn't exist.
- `401 UNAUTHORIZED`: The user needs to log in.

### Adding Custom Headers
Headers are used to send extra metadata. A common use case is setting caching policies or security headers.

```python
@app.get("/secure-data")
async def secure_response(request: Request, response: Response):
    return response.json(
        {"data": "This is a secret message"},
        headers={
            "X-Content-Type-Options": "nosniff", # A security header
            "Cache-Control": "no-cache"        # Tell browsers not to cache this
        }
    )
```

> **Why does this matter?**
> A well-crafted response gives the client all the information it needs to work correctly. Proper status codes and headers are signs of a high-quality, professional API.

---

## Practice: Build a Data-Driven Endpoint

**Try this:**
1.  Create a `POST` endpoint at `/products`.
2.  In the handler, read the JSON body from the `request`. Assume it contains `{"name": "...", "price": ...}`.
3.  Add some basic validation. If `price` is missing, return a `400 BAD REQUEST` status with an error message.
4.  If the data is valid, return a `201 CREATED` status with the product data and a custom header like `"X-Status": "Product-Created"`.

---

## Next Steps

Tomorrow, we'll look at a more structured way to build APIs using class-based views, which helps keep your code organized as it grows.

➡️ **[Continue to Day 4: Path & Query Parameters](../day04/)**
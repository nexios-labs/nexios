# Day 3: Async, Request, and Response

## Async Function Support

Nexios is built on Python's async/await syntax for high performance:

```python
from nexios import NexiosApp
from nexios.http import Request, Response
import asyncio

app = NexiosApp()

# Basic async route
@app.get("/")
async def hello(request: Request, response: Response):
    return {"message": "Hello, World!"}

# Async with delay
@app.get("/delayed")
async def delayed_response(request: Request, response: Response):
    await asyncio.sleep(1)  # Simulate delay
    return {"message": "Delayed response"}

# Multiple async operations
@app.get("/parallel")
async def parallel_tasksrequest: Request, response: Response():
    task1 = asyncio.create_task(async_operation1())
    task2 = asyncio.create_task(async_operation2())
    
    results = await asyncio.gather(task1, task2)
    return {"results": results}

async def async_operation1():
    await asyncio.sleep(1)
    return "Operation 1 complete"

async def async_operation2():
    await asyncio.sleep(2)
    return "Operation 2 complete"
```

## Working with Request Objects

The Request object provides access to all request data:

```python
from nexios import NexiosApp
from nexios.http import Request

app = NexiosApp()

@app.get("/request-demo")
async def request_demo(request: Request, response: Response):
    return {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "client": request.client.host
    }

@app.post("/data-demo")
async def data_demo(request: Request, response: Response):
    # Get JSON data
    json_data = await request.json
    
    # Get form data
    form_data = await request.form
    
    # Get raw body
    body = await request.body
    
    return {
        "json": json_data,
        "form": dict(form_data),
        "body_size": len(body)
    }
```

## Response Handling

Nexios offers flexible response options:

```python
from nexios import NexiosApp
from nexios.http import Response

app = NexiosApp()

# JSON Response
@app.get("/json")
async def json_response(request: Request, response: Response):
    return response.json(
        {"message": "Hello"},
        status_code=200
    )

# HTML Response
@app.get("/html")
async def html_response(request: Request, response: Response):
    return response.json(
        "<h1>Hello, World!</h1>",
        status_code=200
    )

# Custom Headers
@app.get("/custom-headers")
async def custom_headers(request: Request, response: Response):
    return response.json(
        "Custom response",
        headers={
            "X-Custom-Header": "value",
            "Server-Timing": "db;dur=53",
            "Cache-Control": "max-age=3600"
        }
    )

# Streaming Response
@app.get("/stream")
async def stream_response(request: Request, response: Response):
    async def number_generator():
        for i in range(10):
            yield f"data: {i}\n\n"
            await asyncio.sleep(1)
    
    return response.stream(
        number_generator(),
        media_type="text/event-stream"
    )
```

## Headers and Status Codes

Working with HTTP headers and status codes:

```python
from nexios import NexiosApp
from nexios import status

app = NexiosApp()

# Status codes
@app.post("/items")
async def create_item(request: Request, response: Response):
    return response.json(
      {"id": 1},
        status_code=status.HTTP_201_CREATED
    )

@app.get("/not-found")
async def not_found(request: Request, response: Response):
    return response.json(
        content={"error": "Resource not found"},
        status_code=status.HTTP_404_NOT_FOUND
    )

# Security headers
@app.get("/secure")
async def secure_response(request: Request, response: Response):
    return response.json(
        {"data": "secure content"},
        headers={
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        }
    )
```

## Practice Exercise

Create an API with these features:

1. Async data processing endpoint
2. File upload with progress
3. Streaming response
4. Custom error handling
5. Security headers middleware

## Additional Resources
- [Async/Await in Python](https://docs.python.org/3/library/asyncio.html)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [Security Headers](https://owasp.org/www-project-secure-headers/)
- [Event Stream Spec](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

## Next Steps
Tomorrow in [Day 4: Class-Based Views with APIHandler](../day04/index.md), we'll explore:
- Using `APIHandler`
- HTTP method handlers
- Structured responses
- Class-based organization
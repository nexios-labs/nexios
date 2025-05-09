# Headers

Headers are a fundamental part of HTTP requests and responses, carrying metadata about the message body, client capabilities, server information, and more. Nexios provides comprehensive tools for working with headers in both requests and responses.

## 📥 Request Headers
Access incoming request headers through the request.headers property:

```python{5,6}
from nexios import NexiosApp
app = NexiosApp()
@app.get("/")
async def show_headers(request, response):
    user_agent = request.headers.get("user-agent")
    accept_language = request.headers.get("accept-language")
    return {
        "user_agent": user_agent,
        "accept_language": accept_language
    }
```

::: tip 💡 Tip
Nexios normalizes header names to lowercase, so request.headers.get("User-Agent") and request.headers.get("user-agent") are equivalent.
:::

## 📤 Response Headers
Set response headers using the response.set_header() method:

```python{5,6}
from nexios import NexiosApp
app = NexiosApp()
@app.get("/")
async def set_headers(request, response):
    response = response.text("Hello, World!", headers={"X-Custom-Header": "Custom Value"})
   
```

## 🔗Setting Headers In Middleware

```python{5,6}
from nexios import NexiosApp
app = NexiosApp()

async def my_middleware(request, response, next):

    await next()

    response.set_header("X-Custom-Header", "Custom Value")

    return response

app.add_middleware(my_middleware)

@app.get("/")
async def show_headers(request, response):
    return {
        "message": "Hello, World!"
    }

```

::: warning ⚠️ Warning
Or else in rare cases, always set headers after the request is processed.

:::





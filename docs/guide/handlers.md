
# 🫴Handlers

In Nexios, all route handlers must be async functions. These handlers receive a Request object and return a Response, dict, str, or other supported types.

::: tip  💡Tip
Every Nexios handler must be async def; it’s triggered by a route and returns a value that becomes the response.
:::

Example
```py 
from nexios import NexiosApp

app = NexiosApp()

@app.get("/")  
async def index(request, response): 
    return "Hello, world!" 
```

::: warning ⚠️ Warning
Nexios Handler must take at least two arguments: `request` and `response`.
:::

The `request` and `response` objects are provided by Nexios and contain information about the incoming request and the outgoing response.

::: tip  💡Tip
User type annotation for more IDE support .

```py

from nexios.http import Request, Response

@app.get("/")  
async def index(request: Request, response: Response): 
    return "Hello, world!" 
```

:::

For more information, see [Request](/guide/request) and [Response](/guide/response)



You can also use handler with `Routes` class

```py
from nexios.routing import Routes
from nexios import NexiosApp
app = NexiosApp()

async def dynamic_handler(req, res):
    return "Hello, world!"

app.add_route(Routes("/dynamic", dynamic_handler))  # Handles All Methods by default

# 🫴Handlers

In Nexios, all route handlers must be async functions. These handlers receive a Request object and return a Response, dict, str, or other supported types.

::: tip  💡Tip
Every Nexios handler must be async def; it’s triggered by a route and returns a value that becomes the response.
:::

Example

```py 
from nexios import NexiosApp

app = NexiosApp()

@app.get("/")  // [!code focus]
async def index(request, response): // [!code focus]
    return "Hello, world!" // [!code focus]
```

::: warning ⚠️ Warning
Nexios Handler must take at least two arguments: `request` and `response`.
:::

The `request` and `response` objects are provided by Nexios and contain information about the incoming request and the outgoing response.

::: tip  💡Tip
User type annotation for more IDE support .

```py

from nexios.http import Request, Response

@app.get("/")  // [!code focus]
async def index(request: Request, response: Response): // [!code focus]
    return "Hello, world!" // [!code focus]
```

:::

For more information, see [Request](/guide/request) and [Response](/guide/response)
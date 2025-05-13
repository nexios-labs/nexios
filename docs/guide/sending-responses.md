# Sending Responses

When building applications, sending responses to client requests is a fundamental task. This guide explains how to structure and send responses effectively.

Nexios Provide Multiple Ways to Send Responses Based on Your Needs

## Basic Example
Nexios Allow you to return a `dict`, `list` or `str` as a response. Here is an example of sending a `dict` as a response:

```python{5}
from nexios import NexiosApp
app = NexiosApp()
@app.route("/")
def index(req, res):
    return {"message": "Hello, World!"}
```

This example sends a JSON response with a key-value pair where the key is "message" and the value is "Hello, World!".

But for some cased you might need more control over the response format. For example, you might want to send a custom HTML page or a PDF file or add custom headers. In this case, you can use the `response` object provided by Nexios to build the response.

```python{5}
from nexios import NexiosApp
app = NexiosApp()
@app.route("/")
def index(req, res):
    res.text("Hello, World!", status_code=200, headers={"Content-Type": "text/plain"})
```

This example sends a plain text response with a status code of 200 and a header of "Content-Type: text/plain".

Nexios Also allow returning a `Response` object. This object provides a fluent interface for building HTTP responses , similar to Express.js. It supports various response types, headers, cookies, caching, and redirections.

```python{5}
from nexios import NexiosApp
from nexios.http.response import JSONResponse
app = NexiosApp()
@app.route("/")
def index(req, res):
    return JSONResponse({"message": "Hello, World!"})
```

::: warning ⚠️ Warning
If no response response is return via any of the above methods, Nexios will a empty response with a status code of 204 and a header of "Content-Type: text/plain".

:::

::: tip 💡 Tip

In Nexios, it first checks if the handler returns a valid JSON type like a `dict`, `list`, or `str`.
If not, it checks if the return value is a `Response` object.
If it's neither, it uses the response object provided by Nexios.

:::

::: tip 💡 Recomended 
we recommend using the `response` object provided by Nexios to build the response.
:::
## File Responses

Nexios Allow you to send files as responses. Here is an example of sending a file as a response:

```python{5}
from nexios import NexiosApp
app = NexiosApp()
@app.route("/")
def index(req, res):
    return res.file("path/to/file.txt")
```

::: details Alternatively use the `FileResponse` class

```python{5}
from nexios import NexiosApp
from nexios.http.response import FileResponse
app = NexiosApp()
@app.route("/")
def index(req, res):
    return FileResponse("path/to/file.txt")
```

:::

You can also modify the file response by passing additional arguments to the `file` method:

```python{5}
from nexios import NexiosApp
from nexios.http.response import FileResponse
app = NexiosApp()
@app.route("/")
def index(req, res):
    return res.file("path/to/file.txt", content_disposition_type="attachment")

```

::: details 📖 Alternatively use the `FileResponse` class

```python{5}
from nexios import NexiosApp
from nexios.http.response import FileResponse
app = NexiosApp()
@app.route("/")
def index(req, res):
    return FileResponse("path/to/file.txt", content_disposition_type="attachment")
```

:::


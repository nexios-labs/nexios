##  Routing

Routing in Nexios is flexible and intuitive, allowing you to define how an application responds to client requests at specific endpoints (URIs or paths) using HTTP methods like GET and POST. Each route can have one or more handler functions that execute when matched, following a clear and structured definition. Let’s take a look.


### Basic (Decorator Based)

```python
from nexios import get_application

app = get_application()

# HTTP Methods
@app.get("/")
async def get_root(req, res):
    return res.text("GET /")

@app.post("/")
async def post_root(req, res):
    return res.text("POST /")

@app.put("/")
async def put_root(req, res):
    return res.text("PUT /")

@app.delete("/")
async def delete_root(req, res):
    return res.text("DELETE /")

# Wildcard Route
@app.get("/wild/*/card")
async def wildcard_route(req, res):
    return res.text("GET /wild/*/card")

# Any HTTP Method
@app.route("/hello")
async def any_method(req, res):
    return res.text("Any Method /hello")

# Custom HTTP Method
@app.route( "/cache",["PURGE"])
async def purge_cache(req, res):
    return res.text("PURGE Method /cache")

# Multiple Methods
@app.route("/post", ["PUT", "DELETE"],)
async def multiple_methods(req, res):
    return res.text("PUT or DELETE /post")

```
Adding routes dynamically using app.add_route()
```py
async def dynamic_handler(req, res):
    return res.text(f"Dynamic Route: {req.path}")

app.add_route(Route("/dynamic", dynamic_handler))  # Handles GET by default
app.add_route(Route("/dynamic-post", dynamic_handler, methods=["POST"]))  # Handles POST
app.add_route(Route("/multi-dynamic", dynamic_handler, methods=["GET", "PATCH"]))  # Handles multiple methods
```
---

### **Path Parameter**


```py

@app.get('/posts/{post_id}/comment/{comment_id}')
async def get_post_comment(req, res):
    post_id, comment_id = req.path_params #only if the path_params is more than one
    ...

```


**To retrieve a single item from the `path_params`.**

```py
@app.get('/posts/{post_id}')
async def get_post_comment(req, res):
    post_id = req.path_params.post_id 
    #-------------or-----------------#
    post_id = req.path_params.get("post_id") 
    ...

```

---


####  Optional Path Params

```py
@app.get('/posts/{post_id}')
@app.get("/posts")
async def get_post_comment(req, res):
    post_id = req.path_params.get("post_id") #returns None
    ...


```

---
### Route Convertors
Route converters in Nexios allow you to define dynamic segments in your routes with specific types or patterns. This is particularly useful when you want to enforce certain constraints on the path parameters, such as ensuring they are integers, floats, or follow a specific pattern.

**Built-in Converters**
Nexios provides several built-in converters that you can use directly in your route definitions:

1. `int`: Matches an integer.

2. `float`: Matches a floating-point number.

3. `path:` Matches any string including slashes (useful for capturing the rest of the path).

4. `uuid`: Matches a UUID string.

5. `string` : Matches any string (default behavior).
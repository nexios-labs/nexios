# Routing 🛣️

Routing of Nexios is flexible and intuitive. Let's take a look.



## The Basic Routing Example

```python
from nexios import NexiosApp

app = NexiosApp()
@app.get("/") 
async def get_root(req, res):
    return {"message": "Hello, world!"}

```

::: details How it Works 🤔

```python
from nexios import NexiosApp
app = NexiosApp() // [!code focus]
@app.method("/path") // [!code focus] #get
async def get_root(req, res): // [!code focus]
    return {"message": "Hello, world!"}// [!code focus]

```
:::

Nexios provides flexible routing that supports both traditional decorators and alternative styles like direct route registration using functions or classes, giving developers full control over how they structure their APIs.


## **Routing With Decorators**

```python
from nexios import NexiosApp

# HTTP Methods
@app.get("/")
async def get_root(req, res):
    return {"message" : "Hello World"}
@app.post("/")
async def post_root(req, res):
    return {"message" : "Hello World"}

@app.put("/")
async def put_root(req, res):
    return {"message" : "Hello World"}

@app.delete("/")
async def delete_root(req, res):
    return res.text("DELETE /")

# Wildcard Route
@app.get("/wild/*/card")
async def wildcard_route(req, res):
    return {"message" : "Hello World"}

# Any HTTP Method
@app.route("/hello")
async def any_method(req, res):
    return {"message" : "Hello World"}

# Custom HTTP Method
@app.route("/cache", ["PURGE"])
async def purge_cache(req, res):
    return res.text("PURGE Method /cache")

# Multiple Methods
@app.route("/post", ["PUT", "DELETE"])
async def multiple_methods(req, res):
    return {"message" : "Hello World"}

```
::: warning ⚠️ Warning
oute conflicts can occur if you register the same path with multiple handlers for overlapping methods without clarity. Ensure each route-method pair is unique or handled intentionally.
:::


## Other Route Methods

Nexios Provides `Routes` class for more complex routing needs. This Helps in grouping routes and makes the code more readable and maintainable.

```python
from nexios.routing import Routes
from nexios import NexiosApp
app = NexiosApp()

async def dynamic_handler(req, res):
    return {"message" : "Hello World"}

app.add_route(Routes("/dynamic", dynamic_handler))  # Handles GET by default
app.add_route(Routes("/dynamic-post", dynamic_handler, methods=["POST"]))  # Handles POST
```
::: tip Tip 💡
you can also pass a list of `Routes` objects to `NexiosApp` to register multiple routes in a single call.

```python

app = NexiosApp(routes = [
    Routes("/dynamic", dynamic_handler),  # Handles GET by default
    Routes("/dynamic-post", dynamic_handler, methods=["POST"]),  # Handles POST
])
```

:::
::: tip Quick Tip 💡

the decorator and Routes takes the same arguments. 😁

:::
## Path Parameter

Path parameters allow you to capture dynamic segments of a URL. These parameters are extracted from the URL and made available to the route handler via the `req.path_params` object.

```python{3}
from nexios import NexiosApp
app = NexiosApp()
@app.get('/posts/{post_id}/comment/{comment_id}') 
async def get_post_comment(req, res):
   ...
```

This will match `/posts/123/comment/456` and extract `123` and `456` as `post_id` and `comment_id` respectively.

You can access the path parameters using `req.path_params` object.

```python{5,6}
from nexios import NexiosApp
app = NexiosApp()
@app.get('/posts/{post_id}/comment/{comment_id}') 
async def get_post_comment(req, res):
   post_id = req.path_params.post_id
   comment_id = req.path_params.comment_id
   return {"message": f"post_id: {post_id}, comment_id: {comment_id}"}
```
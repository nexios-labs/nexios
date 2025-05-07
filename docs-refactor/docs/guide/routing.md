# Routing 🛣️

Routing of Nexios is flexible and intuitive. Let's take a look.



## 🚀 The Basic Routing Example 

```python
from nexios import NexiosApp

app = NexiosApp()
@app.get("/") 
async def get_root(req, res):
    return {"message": "Hello, world!"}

```

:::  details 🤔 How it Works 

```python
from nexios import NexiosApp
app = NexiosApp() // [!code focus]
@app.method("/path") // [!code focus] #get
async def get_root(req, res): // [!code focus]
    return {"message": "Hello, world!"}// [!code focus]

```
:::

Nexios provides flexible routing that supports both traditional decorators and alternative styles like direct route registration using functions or classes, giving developers full control over how they structure their APIs.


## 🌳 **Routing With Decorators** 

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


## 🚗 Other Route Methods 

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

### The `Routes` Class in Detail

The `Routes` class is the core building block of Nexios routing. It encapsulates all routing information for an API endpoint, including path handling, validation, OpenAPI documentation, and request processing.

```python
from nexios.routing import Routes

route = Routes(
    path="/users/{user_id}",
    handler=user_detail_handler,
    methods=["GET", "PUT", "DELETE"],
    name="user_detail",
    summary="User Detail API",
    description="Get, update or delete a user by ID",
    responses={
        200: UserResponse,
        404: {"description": "User not found"}
    },
    request_model=UserUpdate,
    middlewares=[auth_middleware, logging_middleware],
    tags=["users"],
    security=[{"bearerAuth": []}],
    operation_id="getUserDetail",
    deprecated=False,
    parameters=[
        Parameter(name="include_details", in_="query", required=False, schema=Schema(type="boolean"))
    ]
)

app.add_route(route)
```

#### Parameters

| Parameter             | Description                               | Type                                   | Default                                                |
| --------------------- | ----------------------------------------- | -------------------------------------- | ------------------------------------------------------ |
| `path`                | URL path pattern with optional parameters | `str`                                  | Required                                               |
| `handler`             | Request processing function/method        | `Callable`                             | Required                                               |
| `methods`             | Allowed HTTP methods                      | `List[str]`                            | `["get", "post", "delete", "put", "patch", "options"]` |
| `name`                | Route name (for URL generation)           | `Optional[str]`                        | `None`                                                 |
| `summary`             | Brief description for OpenAPI docs        | `Optional[str]`                        | `None`                                                 |
| `description`         | Detailed description for OpenAPI docs     | `Optional[str]`                        | `None`                                                 |
| `responses`           | Response schemas or descriptions          | `Optional[Dict[int, Any]]`             | `None`                                                 |
| `request_model`       | Pydantic model for request validation     | `Optional[Type[BaseModel]]`            | `None`                                                 |
| `middlewares`         | Route-specific middleware                 | `List[Any]`                            | `[]`                                                   |
| `tags`                | OpenAPI tags for grouping                 | `Optional[List[str]]`                  | `None`                                                 |
| `security`            | Security requirements                     | `Optional[List[Dict[str, List[str]]]]` | `None`                                                 |
| `operation_id`        | Unique identifier for OpenAPI             | `Optional[str]`                        | `None`                                                 |
| `deprecated`          | Mark route as deprecated                  | `bool`                                 | `False`                                                |
| `parameters`          | Additional parameters for OpenAPI         | `List[Parameter]`                      | `[]`                                                   |
| `exclude_from_schema` | Hide from OpenAPI docs                    | `bool`                                 | `False`  

                                              |
:::
::: tip Quick Tip 💡

the decorator and Routes takes the same arguments. 😁

:::
## 🗳️ Path Parameter 

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

Alternatively, you can use pass the path parameters to the handler directly using 

```python{5,6}
from nexios import NexiosApp
app = NexiosApp()
@app.get('/posts/{post_id}/comment/{comment_id}') 
async def get_post_comment(req, res, post_id, comment_id):
   return {"message": f"post_id: {post_id}, comment_id: {comment_id}"}
```


**Optional Route Parameters** 

To use optional parameters in Nexios, you can define them in your route Double:

```py{3,4}
from nexios import NexiosApp
app = NexiosApp()
@app.get('/posts/{post_id}') 
@app.get('/posts') 
async def get_post_comment(req, res):
   return {"message": f"post_id: {post_id}"}

```

## 🔁 Route Converters 

Route converters in Nexios allow you to enforce specific types or patterns on dynamic segments of your routes. This ensures that only valid data is processed, improving the reliability and predictability of your API.

#### **Built-in Converters**

**`int`** – Matches an integer (whole number).

```python{1}
@app.get("/items/{item_id:int}")
async def get_item(req, res):
    item_id = req.path_params.item_id
    return res.text(f"Item ID: {item_id} (Integer)")
```

* **Matches:** `/items/42`
* **Does Not Match:** `/items/apple`
**`float`** – Matches a floating-point number.

```python
@app.get("/price/{amount:float}")
async def get_price(req, res):
    amount = req.path_params.amount
    return res.text(f"Amount: {amount} (Float)")
```

* **Matches:** `/price/99.99`
* **Does Not Match:** `/price/free`
**`path`** – Matches any string, including slashes (`/`).

```python
@app.get("/files/{filepath:path}")
async def read_file(req, res):
    filepath = req.path_params.filepath
    return res.text(f"File Path: {filepath}")
```

* **Matches:** `/files/documents/report.pdf`
* **Does Not Match:** (Almost always matches)
**`uuid`** – Matches a valid UUID string.

```python
@app.get("/users/{user_id:uuid}")
async def get_user(req, res):
    user_id = req.path_params.user_id
    return res.text(f"User ID: {user_id} (UUID)")
```

* **Matches:** `/users/550e8400-e29b-41d4-a716-446655440000`
* **Does Not Match:** `/users/12345`

**`string`** – Matches any string (default behavior).

```python
@app.post("/person/{username:str}")
async def get_person(req, res):
    username = req.path_params.username
    return res.text(f"Username: {username}")
```

* **Matches:** `/person/anyname`
* **Does Not Match:** (Almost always matches)
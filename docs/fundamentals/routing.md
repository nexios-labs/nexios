---
icon: arrow-progress
---

# Routing

#### **Routing in Nexios: A Comprehensive Guide**

Routing is the backbone of any web application, defining how the application responds to client requests at specific endpoints (URIs or paths) using HTTP methods like GET, POST, PUT, DELETE, and more. Nexios provides a flexible, intuitive, and powerful routing system that allows developers to define routes in a clear and structured manner. This guide will explore Nexios routing in detail, covering basic routing, path parameters, route converters, and advanced routing techniques like modular routers and nested routing.

***

### **Basic Routing (Decorator-Based)**

Nexios simplifies route definition using decorators, making it easy to map HTTP methods to specific endpoints. Below is an example of basic routing:

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
@app.route("/cache", ["PURGE"])
async def purge_cache(req, res):
    return res.text("PURGE Method /cache")

# Multiple Methods
@app.route("/post", ["PUT", "DELETE"])
async def multiple_methods(req, res):
    return res.text("PUT or DELETE /post")
```

#### **Explanation and Notes:**

* **Decorator-Based Routing:** Nexios uses decorators like `@app.get`, `@app.post`, etc., to define routes. This approach is clean and intuitive, making it easy to associate HTTP methods with specific endpoints.
* **Wildcard Routes:** The `*` wildcard allows you to match any segment of the URL. For example, `/wild/*/card` will match `/wild/anything/card`, `/wild/123/card`, etc.
* **Custom HTTP Methods:** Nexios supports custom HTTP methods like `PURGE`, allowing you to define routes for non-standard methods.
* **Multiple Methods:** A single route can handle multiple HTTP methods, reducing redundancy in your code.

#### **Dynamic Route Addition**

Routes can also be added dynamically using the `app.add_route()` method. This is useful when routes need to be generated programmatically or loaded from external configurations.

```python
from nexios.routing import Routes
async def dynamic_handler(req, res):
    return res.text(f"Dynamic Route: {req.path}")

app.add_route(Routes("/dynamic", dynamic_handler))  # Handles GET by default
app.add_route(Routes("/dynamic-post", dynamic_handler, methods=["POST"]))  # Handles POST
app.add_route(Routes("/multi-dynamic", dynamic_handler, methods=["GET", "PATCH"]))  # Handles multiple methods
```

#### **Explanation and Notes:**

* **Dynamic Routing:** This approach is useful for scenarios where routes are not known at development time, such as when routes are loaded from a database or configuration file.
* **Flexibility:** You can specify the HTTP methods for each route, making it easy to handle different types of requests dynamically.

***

### **Path Parameters**

Path parameters allow you to capture dynamic segments of a URL. These parameters are extracted from the URL and made available to the route handler via the `req.path_params` object.

#### **Basic Path Parameters**

```python
@app.get('/posts/{post_id}/comment/{comment_id}')
async def get_post_comment(req, res):
    post_id, comment_id = req.path_params  # Extracts multiple parameters
    return res.text(f"Post ID: {post_id}, Comment ID: {comment_id}")
```

#### **Retrieving a Single Path Parameter**

```python
@app.get('/posts/{post_id}')
async def get_post(req, res):
    post_id = req.path_params.post_id  # Access using dot notation
    #-------------or-----------------#
    post_id = req.path_params.get("post_id")  # Access using .get() method
    return res.text(f"Post ID: {post_id}")
```

#### **Optional Path Parameters**

Optional path parameters allow you to define routes that can match with or without a specific parameter.

```python
@app.get('/posts/{post_id}')
@app.get("/posts")
async def get_post(req, res):
    post_id = req.path_params.get("post_id")  # Returns None if not present
    return res.text(f"Post ID: {post_id}")
```

#### **Explanation and Notes:**

* **Path Parameters:** These are dynamic segments of the URL that can be captured and used in your route handlers. They are particularly useful for RESTful APIs where resources are identified by IDs.
* **Optional Parameters:** By defining multiple routes for the same handler, you can make certain path parameters optional. This is useful for endpoints that can operate with or without specific parameters.
* **Accessing Parameters:** Path parameters can be accessed using dot notation (`req.path_params.post_id`) or the `.get()` method (`req.path_params.get("post_id")`). The `.get()` method is safer as it returns `None` if the parameter is not present.

***

### **Route Converters**

Route converters in Nexios allow you to enforce specific types or patterns on dynamic segments of your routes. This ensures that only valid data is processed, improving the reliability and predictability of your API.

#### **Built-in Converters**

1.  **`int`** – Matches an integer (whole number).

    ```python
    @app.get("/items/{item_id:int}")
    async def get_item(req, res):
        item_id = req.path_params.item_id
        return res.text(f"Item ID: {item_id} (Integer)")
    ```

    * **Matches:** `/items/42`
    * **Does Not Match:** `/items/apple`
2.  **`float`** – Matches a floating-point number.

    ```python
    @app.get("/price/{amount:float}")
    async def get_price(req, res):
        amount = req.path_params.amount
        return res.text(f"Amount: {amount} (Float)")
    ```

    * **Matches:** `/price/99.99`
    * **Does Not Match:** `/price/free`
3.  **`path`** – Matches any string, including slashes (`/`).

    ```python
    @app.get("/files/{filepath:path}")
    async def read_file(req, res):
        filepath = req.path_params.filepath
        return res.text(f"File Path: {filepath}")
    ```

    * **Matches:** `/files/documents/report.pdf`
    * **Does Not Match:** (Almost always matches)
4.  **`uuid`** – Matches a valid UUID string.

    ```python
    @app.get("/users/{user_id:uuid}")
    async def get_user(req, res):
        user_id = req.path_params.user_id
        return res.text(f"User ID: {user_id} (UUID)")
    ```

    * **Matches:** `/users/550e8400-e29b-41d4-a716-446655440000`
    * **Does Not Match:** `/users/12345`
5.  **`string`** – Matches any string (default behavior).

    ```python
    @app.post("/person/{username:str}")
    async def get_person(req, res):
        username = req.path_params.username
        return res.text(f"Username: {username}")
    ```

    * **Matches:** `/person/anyname`
    * **Does Not Match:** (Almost always matches)

#### **Explanation and Notes:**

* **Type Safety:** Converters ensure that only valid data types are processed, reducing the likelihood of errors in your application.
* **Error Handling:** If an incoming request parameter does not match the defined type, Nexios will automatically return an error response, helping maintain API integrity.
* **Flexibility:** Converters can be combined with other routing features, such as optional parameters and nested routes, to create powerful and flexible routing systems.

***

### **Routers in Nexios**

Routers are a powerful feature in Nexios that enable modular and scalable application design. They allow you to group related routes into separate modules, making your codebase cleaner and more maintainable.

#### **Benefits of Using Routers**

1. **Modular Structure** – Split routes across multiple files instead of keeping them all in one large file.
2. **Code Reusability** – Reuse common route patterns across different parts of the application.
3. **Scalability** – Easily manage larger projects with multiple endpoints.
4. **Better Maintainability** – Each feature/module can have its own router, reducing clutter in the main app file.

#### **Creating a Router**

```python
from nexios.routing import Router

# Create a new router instance
user_router = Router()

@user_router.get("/profile")
async def get_profile(req, res):
    return res.json({"message": "User Profile"})

@user_router.post("/login")
async def login(req, res):
    return res.json({"message": "User Logged In"})

@user_router.get("/settings")
async def user_settings(req, res):
    return res.json({"message": "User Settings"})
```

#### **Mounting the Router**

Once a router is defined, it needs to be mounted to the main application. This attaches the router’s routes to a specific prefix.

```python
from nexios import get_application

app = get_application()
app.mount_router("/users", user_router)
```

Now, all routes inside `user_router` will be prefixed with `/users`:

* `GET /users/profile` → Calls `get_profile`
* `POST /users/login` → Calls `login`
* `GET /users/settings` → Calls `user_settings`

#### **Explanation and Notes:**

* **Modular Design:** Routers allow you to break down your application into smaller, more manageable pieces. This is particularly useful for large applications with many endpoints.
* **Prefixing:** Mounting a router under a prefix (e.g., `/users`) ensures that all routes within the router are grouped logically.
* **Reusability:** Routers can be reused across different parts of the application or even in different projects, promoting code reuse and reducing duplication.

***

### **Nested Routers (Hierarchical Routing)**

Nested routers allow you to create a hierarchical structure for your routes, which is particularly useful for organizing large applications with multiple submodules.

#### **Example: Nested Routers**

```python
post_router = Router()

@post_router.get("/")
async def get_posts(req, res):
    return res.json({"message": "All Posts"})

@post_router.get("/{post_id}")
async def get_post(req, res):
    return res.json({"message": f"Post ID {req.path_params.post_id}"})

# Mount the post_router under the user_router
user_router.mount("/posts", post_router)
```

With this setup, the following routes are available:

* `GET /users/posts` → Calls `get_posts`
* `GET /users/posts/{post_id}` → Calls `get_post`

#### **Explanation and Notes:**

* **Hierarchical Structure:** Nested routers allow you to create a hierarchy of routes, making it easier to organize complex applications.
* **Logical Grouping:** By nesting routers, you can group related routes together, improving the readability and maintainability of your code.
* **Flexibility:** Nested routers can be combined with other routing features, such as path parameters and converters, to create powerful and flexible routing systems.

***

Nexios provides a robust and flexible routing system that caters to both simple and complex application needs. From basic route definitions to advanced features like route converters, modular routers, and nested routing, Nexios ensures that your application remains scalable, maintainable, and easy to develop. By leveraging these features, you can build well-structured APIs that are both performant and easy to manage.

## Advanced Routing Features

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

| Parameter | Description | Type | Default |
|------------|-------------|------|---------|
| `path` | URL path pattern with optional parameters | `str` | Required |
| `handler` | Request processing function/method | `Callable` | Required |
| `methods` | Allowed HTTP methods | `List[str]` | `["get", "post", "delete", "put", "patch", "options"]` |
| `name` | Route name (for URL generation) | `Optional[str]` | `None` |
| `summary` | Brief description for OpenAPI docs | `Optional[str]` | `None` |
| `description` | Detailed description for OpenAPI docs | `Optional[str]` | `None` |
| `responses` | Response schemas or descriptions | `Optional[Dict[int, Any]]` | `None` |
| `request_model` | Pydantic model for request validation | `Optional[Type[BaseModel]]` | `None` |
| `middlewares` | Route-specific middleware | `List[Any]` | `[]` |
| `tags` | OpenAPI tags for grouping | `Optional[List[str]]` | `None` |
| `security` | Security requirements | `Optional[List[Dict[str, List[str]]]]` | `None` |
| `operation_id` | Unique identifier for OpenAPI | `Optional[str]` | `None` |
| `deprecated` | Mark route as deprecated | `bool` | `False` |
| `parameters` | Additional parameters for OpenAPI | `List[Parameter]` | `[]` |
| `exclude_from_schema` | Hide from OpenAPI docs | `bool` | `False` |

### Advanced Path Parameters

Nexios supports advanced path parameter features beyond the basics:

#### Custom Regex Patterns

For more complex validation requirements, you can define custom regex patterns:

```python
@app.get("/products/{sku:[A-Z]{2}\d{6}}")
async def get_product(req, res):
    """Match only SKUs with format like 'AB123456'"""
    sku = req.path_params.sku
    return res.json({"sku": sku})
```

#### Multiple Parameters with Different Convertors

You can combine multiple parameters with different type convertors:

```python
@app.get("/reports/{year:int}/{month:int}/{format:str}")
async def get_report(req, res):
    year = req.path_params.year     # int
    month = req.path_params.month   # int
    format = req.path_params.format # str
    return res.json({"year": year, "month": month, "format": format})
```

#### Optional Segments

You can make entire path segments optional by defining multiple routes:

```python
@app.get("/articles/{category}/{tag}")
@app.get("/articles/{category}")
@app.get("/articles")
async def list_articles(req, res):
    category = req.path_params.get("category")
    tag = req.path_params.get("tag")
    
    filters = {}
    if category:
        filters["category"] = category
    if tag:
        filters["tag"] = tag
        
    return res.json({"articles": get_articles(**filters)})
```

### Router Middleware Handling

Nexios provides flexibility in how middleware is applied at different levels of your routing system:

#### Global Middleware

Applied to all routes in the application:

```python
app = get_application()
app.add_middleware(GlobalMiddleware())
```

#### Router-Level Middleware

Applied to all routes within a specific router:

```python
admin_router = Router()
admin_router.add_middleware(AdminAuthMiddleware())
```

#### Route-Specific Middleware

Applied only to specific routes:

```python
@app.get("/sensitive-data", middlewares=[RequireAuthMiddleware])
async def get_sensitive_data(req, res):
    return res.json({"data": "Secret!"})
```

#### Middleware Execution Order

Middleware is executed in the following order:

1. Global middleware (outer → inner)
2. Router-level middleware (outer → inner)
3. Route-specific middleware (outer → inner)
4. Route handler
5. Route-specific middleware (inner → outer)
6. Router-level middleware (inner → outer)
7. Global middleware (inner → outer)

Example demonstrating middleware layers:

```python
async def logging_middleware(request, response, call_next):
    print(f"Request to {request.url}")
    await call_next()
    print(f"Response from {request.url}: {response.status_code}")

class AuthMiddleware(BaseMiddleware):
    async def process_request(self, request, response, call_next):
        if not is_authenticated(request):
            return response.text("Unauthorized", status_code=401)
        await call_next()

# Global middleware
app.add_middleware(logging_middleware)

# Router middleware
api_router = Router()
api_router.add_middleware(RateLimitMiddleware)

# Route-specific middleware
@api_router.post("/users", middlewares=[ValidationMiddleware])
async def create_user(req, res):
    # This handler is wrapped with all three layers of middleware
    # Execution: logging -> rate limiting -> validation -> handler
    return res.json({"success": True})
```

### Nested Routing and URL Generation

#### Deep Nested Routers

Nexios allows for deeply nested routers to create a hierarchical API structure:

```python
app = get_application()

# First level
api_v1 = Router()
app.mount_router("/api/v1", api_v1)

# Second level
users_router = Router()
api_v1.mount_router("/users", users_router)

# Third level
profiles_router = Router()
users_router.mount_router("/profiles", profiles_router)

# Routes will be available at: /api/v1/users/profiles/...
@profiles_router.get("/{profile_id}")
async def get_profile(req, res):
    profile_id = req.path_params.profile_id
    return res.json({"profile_id": profile_id})
```

#### URL Generation with Named Routes

Nexios provides a powerful URL generation system that lets you create URLs dynamically based on route names:

```python
@app.get("/users/{user_id}/posts/{post_id}", name="user_post")
async def get_user_post(req, res):
    user_id = req.path_params.user_id
    post_id = req.path_params.post_id
    return res.json({"user_id": user_id, "post_id": post_id})

# Generate URLs in other routes
@app.get("/dashboard")
async def dashboard(req, res):
    # Generate URL with parameters
    post_url = req.app.url_for("user_post", user_id=42, post_id=123)
    
    # Returns: '/users/42/posts/123'
    return res.html(f'<a href="{post_url}">View Post</a>')
```

#### Applying Prefixes to Multiple Routes

Creating a router with a prefix automatically applies that prefix to all its routes:

```python
# Create a router with a prefix
admin_router = Router(prefix="/admin")

# All routes are prefixed with '/admin'
@admin_router.get("/dashboard")  # /admin/dashboard
async def admin_dashboard(req, res):
    return res.text("Admin Dashboard")

@admin_router.get("/users")  # /admin/users
async def admin_users(req, res):
    return res.text("Admin Users")

# Mount the router
app.mount_router(admin_router)  # No need to specify prefix again
```

#### Router Tagging for OpenAPI

You can apply tags to all routes in a router for better OpenAPI organization:

```python
# Create a router with tags
user_router = Router(tags=["users"])

# All routes inherit the "users" tag
@user_router.get("/")
async def list_users(req, res):
    # This route has the "users" tag in OpenAPI docs
    return res.json([{"id": 1, "name": "John"}])

@user_router.get("/{user_id}", tags=["details"])
async def get_user(req, res):
    # This route has both "users" and "details" tags
    return res.json({"id": req.path_params.user_id, "name": "John"})
```

This completes the overview of Nexios's robust and flexible routing system, providing you with the tools to build well-structured, scalable APIs.

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

Here’s a refined and detailed version of your Nexios built-in converters explanation with complete examples for each type:  
  

1. **`int`** – Matches an integer (whole number).  
   - **Example Route:**  
     ```python
     @app.get("/items/{item_id:int}")
     async def get_item(req, res):
         ...
     ```
   - **Matches:** `/items/42`  
   - **Does Not Match:** `/items/apple` (since "apple" is not an integer)  

2. **`float`** – Matches a floating-point number.  
   - **Example Route:**  
     ```python
     @app.get("/price/{amount:float}")
     async def get_price(req, res):
         ...
     ```
   - **Matches:** `/price/99.99`  
   - **Does Not Match:** `/price/free` (since "free" is not a float)  

3. **`path`** – Matches any string, including slashes (`/`). Useful for capturing the rest of a URL path.  
   - **Example Route:**  
     ```python
     @app.get("/files/{filepath:path}")
     async def read_file(req, res):
         ...
     ```
   - **Matches:** `/files/documents/report.pdf`  
   - **Does Not Match:** (Almost always matches since it captures everything after `/files/`)  

4. **`uuid`** – Matches a valid UUID string (commonly used for unique identifiers).  
   - **Example Route:**  
     ```python
     @app.get("/users/{user_id:uuid}")
     async def get_user(req, res):
         ...
     ```
   - **Matches:** `/users/550e8400-e29b-41d4-a716-446655440000`  
   - **Does Not Match:** `/users/12345` (since "12345" is not a UUID)  

5. **`string`** – Matches any string (default behavior if no type is specified).  
   - **Example Route:**  
     ```python
     @app.post("/person/{username:string}")
     async def get_person(req, res):
         ...
     ```
   - **Matches:** `/person/anyname`  
   - **Does Not Match:** (Almost always matches since it's a broad match for strings)  

---

### **How Converters Improve Routing**  
Using converters ensures that your routes are **more predictable** and **error-proof**, preventing unexpected data types from being processed. If an incoming request parameter does not match the defined type, Nexios will automatically return an error response, helping maintain API integrity.  


---

### **Routers in Nexios**

Routers in Nexios help in structuring large applications by grouping related routes into separate modules. This makes code organization cleaner, enhances reusability, and allows better scalability when managing multiple API endpoints.

1. `Modular Structure` – Helps split routes across multiple files instead of keeping them all in one large app.py.

2. `Code Reusability` – Common route patterns can be reused across different parts of the application.

3. `Scalability` – Makes it easier to manage larger projects with multiple endpoints.

4. `Better Maintainability` – Each feature/module can have its own router, reducing clutter in the main app file.

**Example: Creating a Router**

```py
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

**Mounting the Router to the App**
Once a router is defined, it needs to be mounted to the main application. This tells Nexios to attach the router’s routes to a specific prefix.

```py
from nexios import get_application

app = get_application()

app.mount_router("/users", user_router)

```


Now, all routes inside user_router will be prefixed with /users:

- GET /users/profile → Calls get_profile
- POST /users/login → Calls login
- GET /users/settings → Calls user_settings

---
### Nested Routers (Hierarchical Routing)
You can also nest routers inside other routers to create a more hierarchical structure. This is useful when you have multiple submodules within a section of your API.

```py
post_router = Router()

@post_router.get("/")
async def get_posts(req, res):
    return res.json({"message": "All Posts"})

@post_router.get("/{post_id}")
async def get_post(req, res):
    return res.json({"message": f"Post ID {req.path_params.post_id}"})

user_router.mount("/posts", post_router)


```
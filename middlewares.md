### **Middleware in Nexios – An Overview**  

Middleware in Nexios is like a pipeline that processes requests and responses before they reach the final route handler or after a response is sent. It allows you to modify requests, enforce security rules, log activity, or even terminate a request early based on certain conditions.  

---

### **How Middleware Works**  
When a request is made, it moves through a **series of middleware functions**, each having the power to:  
1. **Modify the Request** – Add headers, parse data, validate authentication.  
2. **Block or Allow Access** – Restrict routes based on conditions like authentication or rate limits.  
3. **Modify the Response** – Format responses, attach custom headers, or compress data.  
4. **Pass Control** – Move the request to the next middleware or directly to the final route handler.  

---


**Example**
Here is an example of a simple “Hello World” Nexios application. The remainder of this article will define and add three middleware functions to the application:

```python

from nexios import get_application

app = get_application()

async def my_logger(req, res, next):
    print(f"Received request: {req.method} {req.path}")
    await next()

async def request_time(req, res, next):
    req.context["request_time"] = req.timestamp
    await next()

async def validate_cookies(req, res, next):
    if "session_id" not in req.cookies:
        return res.json({"error": "Missing session_id cookie"}, status_code=400)
    await next()

app.add_middleware(my_logger)
app.add_middleware(request_time)
app.add_middleware(validate_cookies)

@app.get("/")
async def hello_world(req, res):
    return res.text("Hello, World!")

```

**order of execution**

```
   ┌────────────────────────┐
   │ Incoming HTTP Request  │
   └──────────┬─────────────┘
              │
   ┌──────────▼──────────┐
   │  Middleware 1 (pre) │  → (e.g., Logs request)
   └──────────┬──────────┘
              │
   ┌──────────▼──────────┐
   │  Middleware 2 (pre) │  → (e.g., Auth checks)
   └──────────┬──────────┘
              │
   ┌──────────▼──────────┐
   │    Route Handler    │  → (Processes request)
   └──────────┬──────────┘
              │
   ┌──────────▼──────────┐
   │  Middleware 2 (post)│  → (e.g., Modify response)
   └──────────┬──────────┘
              │
   ┌──────────▼──────────┐
   │  Middleware 1 (post)│  → (e.g., Log response)
   └──────────┬──────────┘
              │
   ┌──────────▼──────────┐
   │ Final Response Sent │
   └─────────────────────┘

```

---
### **Class-Based Middleware in Nexios**

Nexios allows middleware to be implemented using class-based structures for better organization and reuse. A class-based middleware can define two main methods:

* `process_request(req, res, cnext)`: Runs before the request reaches the handler.
* `process_response(req, res)`: Runs after the handler has processed the re

A class-based middleware in Nexios follows this structure:

```python
from nexios.middlewares import BaseMiddleware
class ExampleMiddleware(BaseMiddleware):
    async def process_request(self, req, res, cnext):
        """Executed before the request handler."""
        print("Processing Request:", req.method, req.url)
        cnext(req, res)  # Calls the next middleware or handler

    async def process_response(self, req, res):
        """Executed after the request handler."""
        print("Processing Response:", res.status_code)
        return res  # Must return the modified response



```

**Method Breakdown**

1. `process_request(req, res, cnext)`
Has access to req (request), res (response), and cnext (next middleware or handler).
Used for modifying the request, authentication, logging, or injecting data.
Must call cnext(req, res) to continue request processing.

2. `process_response(req, res)`
Runs after the request handler has finished executing.
Has access to req (same request object) and res (response object).
Can be used to modify response headers, format data, or handle errors.
Must return res to pass the modified response.



---
#### Route-Specific, Router-Specific, and Middleware Utilities

Middleware in Nexios provides a flexible way to handle requests and responses. It can be applied globally, to specific routes, or to entire routers. Additionally, Nexios provides middleware utilities to simplify common tasks like logging, authentication, and request validation.

### **Route-Specific Middleware**
Route-specific middleware applies only to a particular route, ensuring that it runs before and after the handler for that specific route only.


```py

async def auth_middleware(req, res, cnext):
    if not req.headers.get("Authorization"):
        res.json({"error": "Unauthorized"}, status_code = 401)
        return 
    await cnext(req, res) 

@app.route("/profile", "GET", middlewares=[auth_middleware])
async def get_profile(req, res):
    return res.json({"message": "Welcome to your profile!"})


```

Execution Order: `auth_middleware → get_profile handler → response sent`

### **Router-Specific Middleware**

Router-specific middleware applies to an entire group of routes under a router. This is useful for cases where multiple routes require the same middleware, such as authentication or logging.
```py
admin_router = Router()

def admin_auth(req, res, cnext):
    if not req.headers.get("Admin-Token"):
        res.json({"error": "Forbiden"}, status_code = 403)

        return res
    await cnext(req, res)
admin_router.add_middlewate(admin_auth)  # Applies to all routes inside admin_router

@admin_router.route("/dashboard", "GET")
def dashboard(req, res):
    res.body = {"message": "Welcome to the admin dashboard!"}

app.mount_router("/admin", admin_router)  # Mount router at "/admin"


```

**`@use_for_route` Decorator in Nexios**

The `@use_for_route` decorator in Nexios is used to bind a middleware function to specific routes or route patterns, ensuring that the middleware only executes when a matching route is accessed.

Example: Applying Middleware with `@use_for_route`

```python
from nexios.middleware.utils import use_for_route
@app.use_for_route("/dashboard", "GET")
async def log_middleware(req, res, cnext):
    print(f"User accessed {req.path.url}")
    await cnext(req, res)  # Proceed to the next function (handler or middleware)


```
---
icon: jsfiddle
---

# Middleware

Middleware in Nexios is a powerful feature that allows you to intercept, process, and modify requests and responses as they flow through your application. It acts as a pipeline, enabling you to implement cross-cutting concerns such as logging, authentication, validation, and response modification in a modular and reusable way. This documentation provides a comprehensive guide to understanding and using middleware in Nexios.

***

## **How Middleware Works**

Middleware functions are executed in a sequence, forming a pipeline that processes incoming requests and outgoing responses. Each middleware function has access to the request (`req`), response (`res`), and a `next` function to pass control to the next middleware or the final route handler.

### **Key Responsibilities of Middleware**

- **Modify the Request** – Add headers, parse data, or inject additional context.
- **Block or Allow Access** – Enforce authentication, rate limiting, or other access controls.
- **Modify the Response** – Format responses, add headers, or compress data.
- **Pass Control** – Call `next()` to continue processing the request or terminate early.


## **Basic Middleware Example**

Below is a simple example demonstrating how to define and use middleware in a Nexios application:

```python
from nexios import NexiosApp
from datetime import datetime
app = NexiosApp()

# Middleware 1: Logging
async def my_logger(req, res, next):
    print(f"Received request: {req.method} {req.path}")
    await next()  # Pass control to the next middleware or handler

# Middleware 2: Request Timing
async def request_time(req, res, next):
    req.request_time = datetime.now()  # Store request time in context
    await next()

# Middleware 3: Cookie Validation
async def validate_cookies(req, res, next):
    if "session_id" not in req.cookies:
        return res.json({"error": "Missing session_id cookie"}, status_code=400)
    await next()

# Add middleware to the application
app.add_middleware(my_logger)
app.add_middleware(request_time)
app.add_middleware(validate_cookies)

# Route Handler
@app.get("/")
async def hello_world(req, res):
    return res.text("Hello, World!")
```

::: tip  💡Tip
All code before `await next()` is executed before the route handler.
:::

## **Order of Execution**

Middleware functions are executed in the order they are added. The flow of execution is as follows:

1. **Pre-Processing** – Middleware functions execute before the route handler.
2. **Route Handler** – The request is processed by the route handler.
3. **Post-Processing** – Middleware functions execute after the route handler.

```
   Incoming request
 └──> Middleware 1 (logs)
       └──> Middleware 2 (auth check)
             └──> Route handler (e.g., /profile)
                   └──> Response is built
             ←──── Middleware 2 resumes (e.g., modify response)
       ←──── Middleware 1 resumes
←──── Final response sent

```
::: tip  💡Tip
 Middleware functions are executed in the order they are added. Ensure that middleware with dependencies (e.g., authentication before authorization) is added in the correct sequence.
:::
***

##  What is `cnext`?
In Nexios, middleware functions rely on a continuation callback (commonly called next, cnext, or callnext) to pass control to the next stage of the request pipeline. This parameter is crucial for request flow but its name is completely flexible — you're free to call it whatever makes sense for your codebase.


## **Class-Based Middleware**

Nexios supports class-based middleware for better organization and reusability. A class-based middleware must inherit from `BaseMiddleware` and implement the following methods:

* **`process_request(req, res, cnext)`** – Executed before the request reaches the handler.
* **`process_response(req, res)`** – Executed after the handler has processed the request.

###  **Example: Class-Based Middleware**

```python
from nexios.middleware import BaseMiddleware

class ExampleMiddleware(BaseMiddleware):
    async def process_request(self, req, res, cnext):
        """Executed before the request handler."""
        print("Processing Request:", req.method, req.url)
        await cnext(req, res)  # Pass control to the next middleware or handler

    async def process_response(self, req, res):
        """Executed after the request handler."""
        print("Processing Response:", res.status_code)
        return res  # Must return the modified response
```

### **Method Breakdown**

1. **`process_request(req, res, cnext)`**
   * Used for pre-processing tasks like logging, authentication, or data injection.
   * Must call `await cnext(req, res)` to continue processing.
2. **`process_response(req, res)`**
   * Used for post-processing tasks like modifying the response or logging.
   * Must return the modified `res` object.

***

## **Route-Specific Middleware**

Route-specific middleware applies only to a particular route. This is useful for applying middleware logic to specific endpoints without affecting the entire application.

### **Example: Route-Specific Middleware**

```python
async def auth_middleware(req, res, cnext):
    if not req.headers.get("Authorization"):
        return res.json({"error": "Unauthorized"}, status_code=401)
    await cnext(req, res)

@app.route("/profile", "GET", middleware=[auth_middleware])
async def get_profile(req, res):
    return res.json({"message": "Welcome to your profile!"})
```

**⚙️ Execution Order:**\
`auth_middleware → get_profile handler → response sent`

***

## **Router-Specific Middleware**

Router-specific middleware applies to all routes under a specific router. This is useful for grouping middleware logic for a set of related routes.

### **Example: Router-Specific Middleware**

```python
admin_router = Router()

async def admin_auth(req, res, cnext):
    if not req.headers.get("Admin-Token"):
        return res.json({"error": "Forbidden"}, status_code=403)
    await cnext(req, res)

admin_router.add_middleware(admin_auth)  # Applies to all routes inside admin_router

@admin_router.route("/dashboard", "GET")
async def dashboard(req, res):
    return res.json({"message": "Welcome to the admin dashboard!"})

app.mount_router("/admin", admin_router)  # Mount router at "/admin"
```

**Execution Order:**\
`admin_auth → dashboard handler → response sent`

***

## **Using `@use_for_route` Decorator**

The `@use_for_route` decorator binds a middleware function to specific routes or route patterns, ensuring that the middleware only executes when a matching route is accessed.

### **Example: `@use_for_route` Decorator**

```python
from nexios.middleware.utils import use_for_route

@use_for_route("/dashboard")
async def log_middleware(req, res, cnext):
    print(f"User accessed {req.path.url}")
    await cnext(req, res)  # Proceed to the next function (handler or middleware)
```

***




  

Always call `await next()`  in middleware to ensure the request continues processing. Failing to do so will block the request pipeline.


::: warning ⚠️ Warning
Avoind modifying the request object in middleware. This can lead to unexpected behavior or security issues.

:::


::: warning ⚠️ Warning

Modifying the response object should be done after the request is processed. It's best to use the `process_response` method of middleware or `callnext` 

:::

##  Raw ASGI Middleware

Nexios Allow you to use raw ASGI middleware. This can be useful for adding middleware that needs lower-level control over the ASGI protocol.

```python
def raw_middleware(app):
    async def middleware(scope, receive, send):
        ## Do something with scope, receive, send
        await app(scope, receive, send)
    return middleware
```

The `app(scope, receive, send)` function is the next middleware in the chain

**Adding raw middleware**

```python
app.wrap_asgi(raw_middleware)

```

::: tip 💡Tip
The `app` objects is an instance of `NexiosApp` You can access the `app` object in your middleware by calling `app`.
:::
#### Class Based Raw Middleware

```python
class RawMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        ## Do something with scope, receive, send
        await self.app(scope, receive, send)
``` 

### Raw Middleware with args

```python
class RawMiddleware:
    def __init__(self, app, *args, **kwargs):
        self.app = app

    async def __call__(self, scope, receive, send):
        ## Do something with scope, receive, send
        await self.app(scope, receive, send)

app.wrap_asgi(RawMiddleware, "arg1", "arg2")
```

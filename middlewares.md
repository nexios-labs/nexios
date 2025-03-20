# **Middleware in Nexios**  

Middleware in Nexios is a powerful feature that allows you to intercept, process, and modify requests and responses as they flow through your application. It acts as a pipeline, enabling you to implement cross-cutting concerns such as logging, authentication, validation, and response modification in a modular and reusable way. This documentation provides a comprehensive guide to understanding and using middleware in Nexios.

---



## **How Middleware Works**  

Middleware functions are executed in a sequence, forming a pipeline that processes incoming requests and outgoing responses. Each middleware function has access to the request (`req`), response (`res`), and a `next` function to pass control to the next middleware or the final route handler.

### **Key Responsibilities of Middleware**
1. **Modify the Request** – Add headers, parse data, or inject additional context.
2. **Block or Allow Access** – Enforce authentication, rate limiting, or other access controls.
3. **Modify the Response** – Format responses, add headers, or compress data.
4. **Pass Control** – Call `next()` to continue processing the request or terminate early.

---

## **Basic Middleware Example**  

Below is a simple example demonstrating how to define and use middleware in a Nexios application:

```python
from nexios import get_application

app = get_application()

# Middleware 1: Logging
async def my_logger(req, res, next):
    print(f"Received request: {req.method} {req.path}")
    await next()  # Pass control to the next middleware or handler

# Middleware 2: Request Timing
async def request_time(req, res, next):
    req.context["request_time"] = req.timestamp  # Store request time in context
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

---

## **Order of Execution**  

Middleware functions are executed in the order they are added. The flow of execution is as follows:

1. **Pre-Processing** – Middleware functions execute before the route handler.
2. **Route Handler** – The request is processed by the route handler.
3. **Post-Processing** – Middleware functions execute after the route handler.

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

## **Class-Based Middleware**  

Nexios supports class-based middleware for better organization and reusability. A class-based middleware must inherit from `BaseMiddleware` and implement the following methods:

- **`process_request(req, res, cnext)`** – Executed before the request reaches the handler.
- **`process_response(req, res)`** – Executed after the handler has processed the request.

### **Example: Class-Based Middleware**

```python
from nexios.middlewares import BaseMiddleware

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
   - Used for pre-processing tasks like logging, authentication, or data injection.  
   - Must call `await cnext(req, res)` to continue processing.  

2. **`process_response(req, res)`**  
   - Used for post-processing tasks like modifying the response or logging.  
   - Must return the modified `res` object.  

---

## **Route-Specific Middleware**  

Route-specific middleware applies only to a particular route. This is useful for applying middleware logic to specific endpoints without affecting the entire application.

### **Example: Route-Specific Middleware**

```python
async def auth_middleware(req, res, cnext):
    if not req.headers.get("Authorization"):
        return res.json({"error": "Unauthorized"}, status_code=401)
    await cnext(req, res)

@app.route("/profile", "GET", middlewares=[auth_middleware])
async def get_profile(req, res):
    return res.json({"message": "Welcome to your profile!"})
```

**Execution Order:**  
`auth_middleware → get_profile handler → response sent`

---

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

**Execution Order:**  
`admin_auth → dashboard handler → response sent`

---

## **Using `@use_for_route` Decorator**  

The `@use_for_route` decorator binds a middleware function to specific routes or route patterns, ensuring that the middleware only executes when a matching route is accessed.

### **Example: `@use_for_route` Decorator**

```python
from nexios.middleware.utils import use_for_route

@app.use_for_route("/dashboard", "GET")
async def log_middleware(req, res, cnext):
    print(f"User accessed {req.path.url}")
    await cnext(req, res)  # Proceed to the next function (handler or middleware)
```

---

## **Best Practices and Special Notes**  

1. **Order Matters**  
   Middleware functions are executed in the order they are added. Ensure that middleware with dependencies (e.g., authentication before authorization) is added in the correct sequence.

2. **Avoid Blocking the Chain**  
   Always call `await next()` or `await cnext(req, res)` in middleware to ensure the request continues processing. Failing to do so will block the request pipeline.

3. **Error Handling**  
   Use middleware to handle errors globally. For example, you can catch exceptions and return standardized error responses.

4. **Performance Considerations**  
   Middleware adds overhead to each request. Avoid heavy computations or blocking operations in middleware to maintain performance.

5. **Testing Middleware**  
   Test middleware in isolation to ensure it behaves as expected. Mock requests and responses to simulate different scenarios.

6. **Reusability**  
   Use class-based middleware or utility functions to create reusable middleware components. This reduces duplication and improves maintainability.

7. **Route-Specific Logic**  
   Use route-specific or router-specific middleware for logic that only applies to certain endpoints. This keeps global middleware lightweight and focused.

---


Middleware in Nexios is a versatile and powerful tool for intercepting and processing requests and responses. By understanding the order of execution, leveraging class-based middleware, and applying best practices, you can build robust and maintainable applications with Nexios. Whether you're logging requests, validating authentication, or modifying responses, middleware provides a clean and modular way to implement cross-cutting concerns.
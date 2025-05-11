# Class-Based Views

Class-Based Views in Nexios offer a structured and modular approach to handling HTTP requests. By encapsulating request logic within a class, developers can easily manage middleware, request preprocessing, error handling, and response formatting. The `APIHandler` class serves as the **base class** for creating class-based handlers, providing hooks for handling requests before execution, after execution, and error handling.

With the addition of middleware support, developers can now pass a list of middleware functions directly into the class, allowing for more flexible and reusable request processing.

---

## Using APIHandler with Middleware in a View

A class-based handler using `APIHandler` with middleware support can be implemented as follows:

```python
from nexios.views import APIHandler

# Example middleware functions
async def auth_middleware(request,response, cnext):
    print("Executing auth middleware")
    return await cnext()

async def logging_middleware(request,response, cnext):
    print("Executing logging middleware")
    return await cnext()

# Class-based view with middleware
class UserView(APIHandler):
    middlewares = [auth_middleware, logging_middleware]  # Pass middleware as a list

    async def get(self, request, response):
        return response.json({"message": "GET request received"})

    async def post(self, request, response):
        data = await request.json
        return response.json({"message": "POST request received", "data": data})


app.add_route(UserView.as_view("/path"))
```

### Explanation:
1. **Middleware List**: The `middleware` attribute in the class allows you to pass a list of middleware functions. These middleware functions are executed in the order they are defined.
2. **`get` Method**: Handles HTTP `GET` requests.
3. **`post` Method**: Handles HTTP `POST` requests.
4. **Automatic Method Dispatching**: The `APIHandler` base class automatically calls the correct method (`get`, `post`, etc.) based on the HTTP request type.
5. **Middleware Execution**: Middleware functions are executed before the request reaches the handler method, allowing for preprocessing (e.g., authentication, logging).

---

## Advantages of Using Class-Based Views with Middleware
<table>
    <tr>
        <th>Feature</th>
        <th>Benefit</th>
    </tr>
    <tr>
        <td><b>Code Reusability</b></td>
        <td>Middleware and common request-handling logic can be shared across multiple views.</td>
    </tr>
    <tr>
        <td><b>Separation of Concerns</b></td>
        <td>Middleware, preprocessing, error handling, and request execution are modularized.</td>
    </tr>
    <tr>
        <td><b>Better Organization</b></td>
        <td>Each HTTP method (<code>get</code>, <code>post</code>, etc.) is defined in its own function, and middleware is centralized.</td>
    </tr>
    <tr>
        <td><b>Middleware-like Hooks</b></td>
        <td>Middleware functions provide a clean way to modify request/response behavior without cluttering the handler logic.</td>
    </tr>
    <tr>
        <td><b>Improved Error Handling</b></td>
        <td>Centralized exception handling with <code>handle_error</code> prevents repeated try-except blocks.</td>
    </tr>
</table>

---

## Middleware Execution Flow
When a request is made to a class-based view with middleware, the execution flow is as follows:
1. **Middleware Execution**: Each middleware function in the `middleware` list is executed in sequence. Each middleware can modify the request or short-circuit the request by returning a response early.
2. **Handler Execution**: Once all middleware functions have been executed, the request is passed to the appropriate handler method (`get`, `post`, etc.).
3. **Response Return**: The response from the handler is returned to the client.

---

## Example Middleware Use Cases
- **Authentication**: Verify user credentials before allowing access to the handler.
- **Logging**: Log request details for debugging or monitoring purposes.
- **Rate Limiting**: Restrict the number of requests from a specific client.
- **Data Validation**: Validate request data before it reaches the handler.

---

Class-Based Views in Nexios, combined with middleware support, provide a clean, maintainable, and scalable way to handle API requests. By using the `APIHandler` base class and passing a list of middleware functions, developers can:
- Define structured request handlers.
- Implement reusable middleware for preprocessing and postprocessing.
- Centralize error handling and improve consistency across endpoints.

This approach ensures that applications are modular, reusable, and easy to maintain as they grow in complexity.


For a more streamlined approach to class-based views, check out the nexios-generics library. It offers pre-built generic views like ListAPIView, CreateAPIView, and more, reducing boilerplate and adding features like pagination, filtering, and built-in middleware support.

Explore the library on GitHub: [Nexios Generics](https://github.com/nexios-labs/nexios-generics)
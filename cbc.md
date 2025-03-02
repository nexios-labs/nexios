# Class-Based Handler
Class-Based Views  in Nexios provide a structured way to handle HTTP requests by defining reusable and modular view handlers. Instead of relying on function-based views , class based handlers allow developers to encapsulate request logic within a class, making it easier to manage middleware, request preprocessing, error handling, and response formatting.

The `APIHandler` class in Nexios is a **base class** for creating class based handlers. It provides hooks for handling requests before execution, after execution, and error handling.

---

## Using APIHandler in a View
A class based handlers using `APIHandler` can be implemented as follows:

```python
from api_handler import APIHandler  # Import the base class

class UserView(APIHandler):
    async def get(self, request, response):
        return response.json({"message": "GET request received"})

    async def post(self, request: , response) :
        data = await request.json
        return response.json({"message": "POST request received", "data": data})

    async def handle_error(self, error, request, response):
        return response.json({"error": str(error)}, status_code=500)
```

### Explanation:
1. **`get` method**: Handles HTTP `GET` requests.
2. **`post` method**: Handles HTTP `POST` requests.
3. **`handle_error` method**: Catches exceptions and returns a JSON response.
4. **Automatic method dispatching**: The `APIHandler` base class automatically calls the correct method (`get`, `post`, etc.).

---

## Advantages of Using Class-Based Views
<table>
    <tr>
        <th>Feature</th>
        <th>Benefit</th>
    </tr>
    <tr>
        <td><b>Code Reusability</b></td>
        <td>Common request-handling logic (e.g., error handling, logging) can be shared across views.</td>
    </tr>
    <tr>
        <td><b>Separation of Concerns</b></td>
        <td>Preprocessing, error handling, and request execution are modularized.</td>
    </tr>
    <tr>
        <td><b>Better Organization</b></td>
        <td>Each HTTP method (<code>get</code>, <code>post</code>, etc.) is defined in its own function.</td>
    </tr>
    <tr>
        <td><b>Middleware-like Hooks</b></td>
        <td><code>before_request</code> and <code>after_request</code> provide a simple way to modify request/response behavior.</td>
    </tr>
    <tr>
        <td><b>Improved Error Handling</b></td>
        <td>Centralized exception handling with <code>handle_error</code> prevents repeated try-except blocks.</td>
    </tr>
</table>


---

Class-Based Views in Nexios provide a clean and maintainable way to handle API requests. By using the `APIHandler` base class, developers can:
- Define structured request handlers.
- Implement global error handling.
- Use `before_request` and `after_request` for pre/post-processing.

This approach makes it easier to **scale applications**, **reuse logic**, and **ensure consistency** across endpoints.


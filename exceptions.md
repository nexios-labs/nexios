

#### **Exception Handling in Nexios**

In Nexios, exception handling is designed to work asynchronously. When an error occurs during request processing, Nexios allows developers to catch and handle it using exception handlers.  

An exception handler in Nexios is an **async function** that takes three parameters:  
- `request`: The incoming HTTP request object.  
- `response`: The HTTP response object used to send a formatted response.  
- `exception`: The raised exception instance.  

Additionally, developers can **create custom exceptions** by inheriting from `HttpException` and register them using `app.add_exception_handler()`.

---

## **Default Exception Handling**  
Nexios automatically catches unhandled exceptions and returns an appropriate HTTP response. However, for more control, you can define custom exception handlers.

### **Example: Default Error Handling**
If a route raises an error and no handler is registered:  
```python
@app.route("/error")
async def error_route(request, response):
    raise ValueError("An unexpected error occurred!")
```
**Response (default handling):**  
By default, Nexios returns a 500 Internal Server Error response for unhandled exceptions. However, if debug=True is set in the application configuration, Nexios provides a detailed error page for easier debugging, displaying stack traces and relevant request information.

---

**Custom Exception Handling**

You can define custom exception handlers for specific errors.

### **Example: Handling a `ValueError`**
```python
async def handle_value_error(request, response, exception):
    response.json({"error": "Bad Request", "detail": str(exception)}, status_code = 500)

app.add_exception_handler(ValueError, handle_value_error)

@app.route("/custom-error")
async def custom_error(request, response):
    raise ValueError("Invalid input provided")
```
**Response (custom handler for ValueError):**  
```json
{
  "error": "Bad Request",
  "detail": "Invalid input provided"
}
```
**Key Points:**  
- The handler **captures ValueError** and responds with a `400 Bad Request` status.  
- `app.add_exception_handler(ValueError, handle_value_error)` registers the handler globally.  

---

## **Creating Custom Exceptions**  
To define custom exceptions, inherit from `HttpException`. This allows setting custom status codes and messages.

### **Example: Creating a `CustomForbiddenException`**
```python
from nexios.exceptions import HttpException

class CustomForbiddenException(HttpException):
    def __init__(self, detail="You do not have permission to access this resource"):
        super().__init__(status_code=403, detail=detail)
```
**Using the custom exception in a route:**
```python
@app.route("/forbidden")
async def forbidden_route(request, response):
    raise CustomForbiddenException()

async def handle_forbidden_exception(request, response, exception):
    response.json({"error": "Forbidden", "detail": exception.detail}, status_Code = exception.status_Code)

app.add_exception_handler(CustomForbiddenException, handle_forbidden_exception)
```
**Now, when `/forbidden` is accessed, the response will be:**  
```json
{
  "error": "Forbidden",
  "detail": "You do not have permission to access this resource"
}
```

---

**Handling Multiple Exceptions**
You can register multiple exception handlers for different error types.

### **Example: Handling Multiple Errors**

```python
async def handle_not_found(request, response, exception):
    response.json({"error": "Not Found", "detail": "The requested resource was not found"},status_code = 404)

async def handle_server_error(request, response, exception):
    response.json({"error": "Internal Server Error", "detail": "Something went wrong"},status_code = 500)

app.add_exception_handler(FileNotFoundError, handle_not_found)
app.add_exception_handler(Exception, handle_server_error)
```
📌 **Key Points:**  
- `FileNotFoundError` returns a **404 Not Found** response.  
- Generic `Exception` catches all **unhandled errors** and returns **500 Internal Server Error**.  

---

## **Catching Exceptions at the Route Level**
Instead of global handlers, you can handle exceptions inside a route using try-except.

### **Example: Try-Except in Route**
```python
@app.route("/divide")
async def divide_numbers(request, response):
    try:
        num1 = int(request.query_params.get("num1", 10))
        num2 = int(request.query_params.get("num2", 0))
        result = num1 / num2
        response.json({"result": result})
    except ZeroDivisionError:
        response.status_code = 400
        response.json({"error": "Cannot divide by zero"})
```
 **Accessing `/divide?num1=10&num2=0` returns:**  
```json
{
  "error": "Cannot divide by zero"
}
```
**Key Points:**  
- This method is **useful for route-specific exception handling**.  
- It avoids unnecessary global handlers for simple errors.



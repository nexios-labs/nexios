# Response API Reference

The Response object is a core component in Nexios that provides methods to create and send HTTP responses. It encapsulates the HTTP response information and provides a fluent interface for building responses.

## Basic Response Methods

### `json()`
```python
response.json({"message": "Hello"})  # Returns a JSON response
```
The `json()` method creates a JSON response with the provided data. It automatically sets the appropriate content type and handles JSON serialization.

Parameters:
- `data`: The data to be serialized to JSON
- `status_code`: HTTP status code (default: 200)
- `headers`: Additional headers to include

Example:
```python
@app.get("/api/users")
async def get_users(request, response):
    users = await get_users_from_db()
    return response.json(
        data={"users": users},
        status_code=200,
        headers={"X-Total-Count": str(len(users))}
    )
```

### `text()`
```python
response.text("Hello, World!")  # Returns a text response
```
The `text()` method creates a plain text response with the provided content. It automatically sets the appropriate content type.

Parameters:
- `content`: The text content to send
- `status_code`: HTTP status code (default: 200)
- `content_type`: Content type (default: "text/plain")
- `headers`: Additional headers to include

Example:
```python
@app.get("/text")
async def get_text(request, response):
    return response.text(
        content="Hello, World!",
        status_code=200,
        content_type="text/plain",
        headers={"X-Custom": "value"}
    )
```

### `html()`
```python
response.html("<h1>Hello</h1>")  # Returns an HTML response
```
The `html()` method creates an HTML response with the provided content. It automatically sets the appropriate content type.

Parameters:
- `content`: The HTML content to send
- `status_code`: HTTP status code (default: 200)
- `headers`: Additional headers to include

Example:
```python
@app.get("/page")
async def get_page(request, response):
    return response.html(
        content="<h1>Hello</h1>",
        status_code=200,
        headers={"X-Frame-Options": "DENY"}
    )
```

### `file()`
```python
response.file("path/to/file.pdf")  # Returns a file response
```
The `file()` method creates a response that sends a file to the client. It automatically sets the appropriate content type based on the file extension.

Parameters:
- `path`: Path to the file
- `filename`: Custom filename for the download (optional)
- `content_type`: Custom content type (optional)
- `status_code`: HTTP status code (default: 200)
- `headers`: Additional headers to include

Example:
```python
@app.get("/download")
async def download_file(request, response):
    return response.file(
        path="files/document.pdf",
        filename="custom.pdf",
        content_type="application/pdf",
        status_code=200,
        headers={"Content-Disposition": "attachment"}
    )
```

### `stream()`
```python
response.stream(generator())  # Returns a streaming response
```
The `stream()` method creates a streaming response that sends data as it becomes available. This is useful for large responses or real-time data.

Parameters:
- `generator`: An async generator that yields response chunks
- `content_type`: Content type (default: "text/plain")
- `status_code`: HTTP status code (default: 200)
- `headers`: Additional headers to include

Example:
```python
@app.get("/stream")
async def stream_data(request, response):
    async def generate():
        for i in range(10):
            yield f"data: {i}\n\n"
            await asyncio.sleep(1)
    
    return response.stream(
        generator=generate(),
        content_type="text/event-stream",
        status_code=200,
        headers={"Cache-Control": "no-cache"}
    )
```

## Status Code Methods

### `status()`
```python
response.status(201)  # Sets the response status code
```
The `status()` method sets the HTTP status code for the response. It returns the response object for method chaining.

Parameters:
- `code`: HTTP status code

Example:
```python
@app.post("/users")
async def create_user(request, response):
    user = await create_user_in_db()
    return response.status(201).json({"user": user})
```

Common status codes:
- `200`: OK
- `201`: Created
- `204`: No Content
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

## Header Methods

### `set_header()`
```python
response.set_header("X-Custom", "value")  # Sets a response header
```
The `set_header()` method sets a response header. It returns the response object for method chaining.

Parameters:
- `key`: Header name
- `value`: Header value

Example:
```python
@app.get("/api")
async def api_endpoint(request, response):
    return response.set_header("X-API-Version", "1.0").json({"data": []})
```

### `has_header()`
```python
if response.has_header("X-Custom"):  # Checks if a header exists
    # Header exists
```
The `has_header()` method checks if a response header exists.

Parameters:
- `key`: Header name to check

Example:
```python
@app.middleware
async def security_middleware(request, response, next):
    response = await next(request, response)
    if not response.has_header("X-Content-Type-Options"):
        response.set_header("X-Content-Type-Options", "nosniff")
    return response
```

### `remove_header()`
```python
response.remove_header("X-Custom")  # Removes a response header
```
The `remove_header()` method removes a response header. It returns the response object for method chaining.

Parameters:
- `key`: Header name to remove

Example:
```python
@app.middleware
async def header_cleanup_middleware(request, response, next):
    response = await next(request, response)
    response.remove_header("X-Powered-By")
    return response
```

## Cookie Methods

### `set_cookie()`
```python
response.set_cookie(
    "session_id",
    "abc123",
    max_age=3600,
    path="/",
    domain="example.com",
    secure=True,
    httponly=True,
    samesite="strict"
)  # Sets a response cookie
```
The `set_cookie()` method sets a response cookie. It returns the response object for method chaining.

Parameters:
- `key`: Cookie name
- `value`: Cookie value
- `max_age`: Cookie lifetime in seconds (optional)
- `path`: Cookie path (optional)
- `domain`: Cookie domain (optional)
- `secure`: Whether the cookie is secure (optional)
- `httponly`: Whether the cookie is HTTP-only (optional)
- `samesite`: SameSite attribute (optional)

Example:
```python
@app.post("/login")
async def login(request, response):
    # Authenticate user
    user = await authenticate_user(request)
    
    # Set session cookie
    return response.set_cookie(
        key="session_id",
        value=user.session_id,
        max_age=3600,
        path="/",
        secure=True,
        httponly=True,
        samesite="strict"
    ).json({"message": "Logged in"})
```

### `delete_cookie()`
```python
response.delete_cookie("session_id")  # Deletes a response cookie
```
The `delete_cookie()` method deletes a response cookie. It returns the response object for method chaining.

Parameters:
- `key`: Cookie name to delete
- `path`: Cookie path (optional)
- `domain`: Cookie domain (optional)

Example:
```python
@app.post("/logout")
async def logout(request, response):
    return response.delete_cookie(
        "session_id",
        path="/",
        domain="example.com"
    ).json({"message": "Logged out"})
```

## Redirect Methods

### `redirect()`
```python
response.redirect("/new-path")  # Creates a redirect response
```
The `redirect()` method creates a redirect response. It returns the response object for method chaining.

Parameters:
- `url`: URL to redirect to
- `status_code`: HTTP status code (default: 302)
- `headers`: Additional headers to include

Example:
```python
@app.get("/old-path")
async def old_path(request, response):
    return response.redirect(
        url="/new-path",
        status_code=301,
        headers={"X-Redirect-From": "/old-path"}
    )
```

## Pagination Methods

### `paginate()`
```python
response.paginate(
    items,
    total_items=100,
    strategy="page_number",
    page_size=10
)  # Creates a paginated response
```
The `paginate()` method creates a paginated response. It returns the response object for method chaining.

Parameters:
- `items`: List of items to paginate
- `total_items`: Total number of items (optional)
- `strategy`: Pagination strategy (optional)
- `page_size`: Items per page (optional)
- `headers`: Additional headers to include

Example:
```python
@app.get("/items")
async def get_items(request, response):
    # Get pagination parameters
    page = int(request.query_params.get("page", "1"))
    limit = int(request.query_params.get("limit", "10"))
    
    # Get items
    items = await get_items_from_db(page, limit)
    total = await get_total_items_count()
    
    # Create paginated response
    return response.paginate(
        items=items,
        total_items=total,
        strategy="page_number",
        page_size=limit,
        headers={"X-Total-Count": str(total)}
    )
```

## Error Response Methods

### `error()`
```python
response.error(400, "Bad Request")  # Creates an error response
```
The `error()` method creates an error response. It returns the response object for method chaining.

Parameters:
- `status_code`: HTTP status code
- `message`: Error message
- `headers`: Additional headers to include

Example:
```python
@app.exception_handler(404)
async def not_found(request, response, exc):
    return response.error(
        status_code=404,
        message="Resource not found",
        headers={"X-Error-Type": "not_found"}
    )
```

### `json_error()`
```python
response.json_error(400, {"error": "Invalid input"})  # Creates a JSON error response
```
The `json_error()` method creates a JSON error response. It returns the response object for method chaining.

Parameters:
- `status_code`: HTTP status code
- `data`: Error data
- `headers`: Additional headers to include

Example:
```python
@app.exception_handler(ValidationError)
async def validation_error(request, response, exc):
    return response.json_error(
        status_code=400,
        data={"error": "Validation failed", "details": exc.errors()},
        headers={"X-Error-Type": "validation"}
    )
```

## Response Properties

### `status_code`
```python
code = response.status_code  # Gets the current status code
```
The `status_code` property returns the current HTTP status code of the response.

Example:
```python
@app.middleware
async def status_logging_middleware(request, response, next):
    response = await next(request, response)
    print(f"Response status: {response.status_code}")
    return response
```

### `content_type`
```python
type = response.content_type  # Gets the current content type
```
The `content_type` property returns the current content type of the response.

Example:
```python
@app.middleware
async def content_type_middleware(request, response, next):
    response = await next(request, response)
    if response.content_type == "application/json":
        response.set_header("X-JSON-Response", "true")
    return response
```

### `headers`
```python
headers = response.headers  # Gets the response headers
```
The `headers` property returns a dictionary of response headers.

Example:
```python
@app.middleware
async def header_logging_middleware(request, response, next):
    response = await next(request, response)
    print("Response headers:")
    for key, value in response.headers.items():
        print(f"{key}: {value}")
    return response
```

### `cookies`
```python
cookies = response.cookies  # Gets the response cookies
```
The `cookies` property returns a list of response cookies.

Example:
```python
@app.middleware
async def cookie_logging_middleware(request, response, next):
    response = await next(request, response)
    print("Response cookies:")
    for cookie in response.cookies:
        print(f"{cookie['name']}: {cookie['value']}")
    return response
```

### `body`
```python
body = response.body  # Gets the response body
```
The `body` property returns the response body.

Example:
```python
@app.middleware
async def body_logging_middleware(request, response, next):
    response = await next(request, response)
    print(f"Response body: {response.body}")
    return response
```

## Advanced Features

### Custom Response Classes
```python
from nexios.http.response import BaseResponse

class PDFResponse(BaseResponse):
    def __init__(self, content, filename=None):
        super().__init__(
            content,
            content_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )

@app.get("/pdf")
async def get_pdf(request, response):
    # Generate PDF
    pdf_content = generate_pdf()
    
    # Create custom response
    return response.make_response(
        PDFResponse(pdf_content, "document.pdf")
    )
```

### Response Middleware
```python
@app.middleware
async def security_headers_middleware(request, response, next):
    response = await next(request, response)
    
    # Add security headers
    response.set_header("X-Content-Type-Options", "nosniff")
    response.set_header("X-Frame-Options", "DENY")
    response.set_header("X-XSS-Protection", "1; mode=block")
    response.set_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    
    return response
```

### Response Compression
```python
@app.middleware
async def compression_middleware(request, response, next):
    response = await next(request, response)
    
    # Check if compression is supported
    if "gzip" in request.headers.get("Accept-Encoding", ""):
        # Compress response
        response.set_header("Content-Encoding", "gzip")
        response.body = compress_response(response.body)
    
    return response
```

### Response Caching
```python
@app.middleware
async def cache_middleware(request, response, next):
    response = await next(request, response)
    
    # Set cache headers
    if response.status_code == 200:
        response.set_header("Cache-Control", "public, max-age=3600")
        response.set_header("ETag", generate_etag(response.body))
    
    return response
```

### Response Streaming
```python
@app.get("/large-file")
async def get_large_file(request, response):
    async def generate():
        with open("large-file.txt", "rb") as f:
            while chunk := f.read(8192):
                yield chunk
    
    return response.stream(
        generate(),
        content_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=large-file.txt"}
    )
```

### Response Chunking
```python
@app.get("/stream")
async def stream_data(request, response):
    async def generate():
        for i in range(10):
            yield f"data: {i}\n\n"
            await asyncio.sleep(1)
    
    return response.stream(
        generate(),
        content_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )
```

### Response Range
```python
@app.get("/video")
async def get_video(request, response):
    # Get range header
    range_header = request.headers.get("Range")
    if not range_header:
        return response.error(400, "Range header required")
    
    # Parse range
    start, end = parse_range_header(range_header)
    
    # Get video chunk
    video_chunk = await get_video_chunk(start, end)
    
    # Set range headers
    response.set_header("Content-Range", f"bytes {start}-{end}/{total_size}")
    response.set_header("Accept-Ranges", "bytes")
    
    return response.stream(
        video_chunk,
        content_type="video/mp4",
        status_code=206
    )
```

### Response CORS
```python
@app.middleware
async def cors_middleware(request, response, next):
    response = await next(request, response)
    
    # Set CORS headers
    response.set_header("Access-Control-Allow-Origin", "*")
    response.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE")
    response.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
    
    return response
```

### Response Rate Limiting
```python
@app.middleware
async def rate_limit_middleware(request, response, next):
    # Check rate limit
    if not await check_rate_limit(request.client):
        return response.error(
            429,
            "Too many requests",
            headers={"Retry-After": "60"}
        )
    
    return await next(request, response)
```

### Response Metrics
```python
@app.middleware
async def metrics_middleware(request, response, next):
    start_time = time.time()
    
    response = await next(request, response)
    
    # Calculate metrics
    duration = time.time() - start_time
    response.set_header("X-Response-Time", f"{duration:.3f}")
    
    # Log metrics
    log_metrics(
        path=request.path,
        method=request.method,
        status_code=response.status_code,
        duration=duration
    )
    
    return response
```

## Key Notes

1. **Content Types**: Always set appropriate content types
2. **Status Codes**: Use correct HTTP status codes
3. **Headers**: Set security headers appropriately
4. **Cookies**: Use secure cookie settings
5. **Streaming**: Use streaming for large responses
6. **Error Handling**: Provide meaningful error messages
7. **Pagination**: Use built-in pagination for large datasets
8. **Security**: Implement proper security headers
9. **Performance**: Use appropriate response types
10. **Caching**: Set proper cache headers when needed

# Response API Reference


## Handler Signature 
```python 
async def handler(req: Request, response: Response) -> Response:
    # Usage examples below
```

##  Core Methods 

### 1. Setting Response Type

#### `text()`
```python
.text(content: str, status_code: int = 200, headers: Dict[str, Any] = {}) -> Response
```
- Sets plain text response
- Example:
  ```python
  return response.text("Hello World")
  ```

#### `json()`
```python
.json(
    data: Union[str, List[Any], Dict[str, Any]],
    status_code: int = 200,
    headers: Dict[str, Any] = {},
    indent: Optional[int] = None,
    ensure_ascii: bool = True
) -> Response
```
- Sets JSON response
- Example:
  ```python
  return response.json({"key": "value"}, indent=2)
  ```

#### `html()`
```python
.html(content: str, status_code: int = 200, headers: Dict[str, Any] = {}) -> Response
```
- Sets HTML response
- Example:
  ```python
  return response.html("<h1>Hello</h1>")
  ```

#### `file()`
```python
.file(
    path: Union[str, Path],
    filename: Optional[str] = None,
    content_disposition_type: str = "inline"
) -> Response
```
- Sends file response
- Example:
  ```python
  return response.file("/path/to/file.pdf")
  ```

#### `download()`
```python
.download(path: Union[str, Path], filename: Optional[str] = None) -> Response
```
- Forces file download
- Example:
  ```python
  return response.download("/path/to/file.zip")
  ```

#### `stream()`
```python
.stream(
    iterator: Generator[Union[str, bytes], Any, Any],
    content_type: str = "text/plain",
    status_code: Optional[int] = None
) -> Response
```
- Streams response
- Example:
  ```python
  def gen():
      yield "streaming"
      yield "content"
  return response.stream(gen())
  ```

#### `redirect()`
```python
.redirect(url: str, status_code: int = 302) -> Response
```
- Redirects to URL
- Example:
  ```python
  return response.redirect("/new-location")
  ```

#### `empty()`
```python
.empty(status_code: int = 200, headers: Dict[str, Any] = {}) -> Response
```
- Empty response body
- Example:
  ```python
  return response.empty(status_code=204)
  ```

### 2. Headers & Cookies

#### `set_header()`
```python
.set_header(key: str, value: str, overide: bool = False) -> Response
```
- Sets response header
- Example:
  ```python
  return response.set_header("X-Custom", "value")
  ```

#### `set_headers()`
```python
.set_headers(headers: Dict[str, str], overide_all: bool = False) -> Response
```
- Sets multiple headers
- Example:
  ```python
  return response.set_headers({"X-One": "1", "X-Two": "2"})
  ```

#### `remove_header()`
```python
.remove_header(key: str) -> Response
```
- Removes header
- Example:
  ```python
  return response.remove_header("X-Remove-Me")
  ```

#### `set_cookie()`
```python
.set_cookie(
    key: str,
    value: str,
    max_age: Optional[int] = None,
    expires: Optional[Union[str, datetime, int]] = None,
    path: str = "/",
    domain: Optional[str] = None,
    secure: bool = True,
    httponly: bool = False,
    samesite: Optional[Literal["lax", "strict", "none"]] = "lax"
) -> Response
```
- Sets cookie
- Example:
  ```python
  return response.set_cookie("session", "abc123", httponly=True)
  ```

#### `set_permanent_cookie()`
```python
.set_permanent_cookie(key: str, value: str, **kwargs: Dict[str, Any]) -> Response
```
- Sets cookie with 10-year expiration
- Example:
  ```python
  return response.set_permanent_cookie("user_id", "1234")
  ```

#### `delete_cookie()`
```python
.delete_cookie(
    key: str,
    path: str = "/",
    domain: Optional[str] = None
) -> Response
```
- Deletes cookie
- Example:
  ```python
  return response.delete_cookie("old_cookie")
  ```

### 3. Response Configuration

#### `status()`
```python
.status(status_code: int) -> Response
```
- Sets HTTP status code
- Example:
  ```python
  return response.status(404)
  ```

#### `cache()`
```python
.cache(max_age: int = 3600, private: bool = True) -> Response
```
- Enables caching
- Example:
  ```python
  return response.cache(max_age=86400)
  ```

#### `no_cache()`
```python
.no_cache() -> Response
```
- Disables caching
- Example:
  ```python
  return response.no_cache()
  ```

## Properties

```python
.headers: MutableHeaders  # All current headers
.cookies: List[Dict[str, Any]]  # All cookies
.body: Union[bytes, memoryview]  # Response body
.content_type: Optional[str]  # Content-Type header
.content_length: str  # Content-Length
```

## Advanced Usage

### `make_response()`
```python
.make_response(response_class: BaseResponse) -> Response
```
- Uses custom response class while preserving headers/cookies
- Example:
  ```python
  custom_resp = CustomResponse()
  return response.make_response(custom_resp)
  ```

### `resp()`
```python
.resp(
    body: Union[JSONType, Any] = "",
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None,
    content_type: str = "text/plain"
) -> Response
```
- Low-level response configuration
- Example:
  ```python
  return response.resp(b"raw", content_type="application/octet-stream")
  ```

---



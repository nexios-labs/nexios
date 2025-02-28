## Nexios Request Object

In Nexios, the `req` object represents an incoming HTTP request and provides access to various request details such as the query parameters, URL parameters, request body, headers, and more. Similarly, the `res` object is used to handle the HTTP response, allowing you to send data back to the client. By convention, these objects are typically referred to as `req` and `res`, but their actual names depend on the parameters specified in the route handler function.

For example, a basic route in Nexios might look like this:

```python
@nexios.route("/user/{id}")
async def get_user(req, res):
    id = req.path_params.id
    res.text(f"User {id}")
```

However, you could use different parameter names if preferred:

```python
@nexios.route("/user/{id}")
async def get_user(request, response):
    id = req.path_params.id
    response.text(f"User {id}")
```

In both cases, `id` is extracted from the URL, demonstrating how Nexios allows flexibility in handling HTTP requests while maintaining readability and structure.

### Properties


**`request.app`**

In Nexios, the request.app property provides a reference to the instance of the Nexios application that is utilizing the middleware.

If you follow a modular approach where a middleware function is defined in a separate module and then imported into your main application file, the middleware can access the Nexios instance through request.app.


```python
app = get_application()
app.mailer = SomeMailingLibrary()
async def custom_middleware(request, response, next):
    app_instance = request.app  # Accessing the Nexios application instance
    app_instance.mailer.mail("..")
    await next()


```

**`request.base_url`**

In Nexios, the `request.base_url` property returns the base URL of the incoming request, excluding any query parameters or additional path segments. This is useful when you need to construct absolute URLs or reference the root endpoint of a request.

For example:

```python

@app.route("/user/{id}")
async def get_user(request, response):
    base_url = request.base_url  # Get the base URL of the request
    response.text(f"Base URL: {base_url}")

```


**` request.json`**

The `request.json` property retrieves the parsed JSON body from an incoming request. This is useful when handling API requests where the client sends JSON data.

```python
@app.route("/api/data", methods=["POST"])
async def handle_json(request, response):
    data = await request.json  # Parse the JSON body
    response.tetxt(f"Received JSON: {data}")

```

**`request.form_data`**
The request.form_data property retrieves data from application/x-www-form-urlencoded form submissions. This is commonly used for HTML forms.

```python

@app.route("/submit", methods=["POST"])
async def handle_form(request, response):
    form_data = await request.form_data  # Parse form data
    name = form_data.get("name")
    email = form_data.get("email")
    response.text(f"Received Form Data: Name={name}, Email={email}")

```

**`request.files`**

The `request.files` property allows you to handle file uploads, extracting files sent through `multipart/form-data`.


```python

@app.route("/upload", methods=["POST"])
async def handle_file_upload(request, response):
    files = await request.files  # Get uploaded files
    uploaded_file = files.get("file")  # Access a specific file
    
    if uploaded_file:
        file_name = uploaded_file.filename
        file_size = uploaded_file.size
        response.text(f"Received File: {file_name} ({file_size} bytes)")
    else:
        response.text("No file uploaded")

```


**`request.text`**


The` request.text` property retrieves the raw text body from an incoming request. This is useful when handling plain text payloads, logs, or custom data formats that are not JSON or form-encoded.

```py
@app.route("/text", methods=["POST"])
async def handle_text(request, response):
    text_data = await request.text  # Read raw text body
    response.text(f"Received Text: {text_data}")



```

**`request.method`**

The `request.method` property returns the HTTP method used in the request (e.g., "GET", "POST", "PUT", "DELETE").

```py

@app.route("/action", methods=["GET", "POST"])
async def handle_request(request, response):
    method = request.method  # Get the request method
    response.text(f"Request Method: {method}")

```


**`request.stream()`**

The `request.stream()` method allows reading the request body as a stream, useful for large payloads like file uploads or big JSON objects.

```py

@app.route("/stream", methods=["POST"])
async def handle_stream(request, response):
    async for chunk in request.stream():  # Read request body in chunks
        print(f"Received Chunk: {chunk}")  # Process each chunk

    response.text("Streaming completed")
```


**`request.build_absolute_uri`**

The `request.build_absolute_uri()` method constructs an absolute URL based on the current request. This is useful when generating links for redirects, API responses, or email templates.


```py
@app.route("/full-url")
async def get_full_url(request, response):
    absolute_url = request.build_absolute_uri("/image/img")  # Get full request URL
    response.text(f"Absolute URL: {absolute_url}")

```

**`request.state`**

The `request.state` property allows passing data between middlewares and route handlers, similar to request attributes in Express.js.

```py
@app.middleware
async def add_state(request, response, next):
    request.state.user_id = "12345"  # Store state data
    await next()  # Continue to the next middleware/handler

@app.route("/get-user")
async def get_user(request, response):
    user_id = request.state.user_id  # Retrieve stored state
    response.text(f"User ID from state: {user_id}")

```



**`request.client`**

The `request.client` property returns a tuple (host, port), representing the client’s IP address and port.

```py

@app.route("/client-info")
async def get_client_info(request, response):
    client_host, client_port = request.client  # Extract host and port
    response.text(f"Client Host: {client_host}, Client Port: {client_port}")


```


**`request.headers`**

The `request.headers` property is a dictionary-like object that contains all incoming HTTP headers.

```py

@app.route("/headers")
async def get_headers(request, response):
    user_agent = request.headers.get("User-Agent", "Unknown")  # Get User-Agent
    auth_token = request.headers.get("Authorization", "No token provided")  # Get Authorization token

    response.json({
        "User-Agent": user_agent,
        "Authorization": auth_token
    })

```



**`request.cookies`**


The request.cookies property allows retrieving cookies sent by the client.

```py

@nexios.route("/get-cookie")
async def get_cookie(request, response):
    session_id = request.cookies.get("session_id", "No session found")  # Read cookie
    response.text(f"Session ID: {session_id}")


```

## Nexios Response Object


The Nexios Response object provides a fluent interface for building HTTP responses , similar to Express.js. It supports various response types, headers, cookies, caching, and redirections. All methods return the instance itself, enabling method chaining.

---

#### Methods

**`text(content, status_code=200, headers={})`**
Sends a plain text response.

**Parameters:**
- `content`: Text content to send (string or JSONType).
- `status_code`: HTTP status code (default: 200).
- `headers`: Custom headers (optional).

**Example:**
```python
response.text("Hello World", 200, {"X-Custom-Header": "Value"})
```

---

**`json(data, status_code=200, headers={}, indent=None, ensure_ascii=True)`**
Sends a JSON response.

**Parameters:**
- `data`: Data to serialize as JSON.
- `status_code`: HTTP status code (default: 200).
- `headers`: Custom headers (optional).
- `indent`: JSON indentation (optional).
- `ensure_ascii`: Escape non-ASCII characters (default: True).

**Example:**
```python
response.json({"message": "Success"}, 200, indent=2)
```

---

**`html(content, status_code=200, headers={})`**
Sends an HTML response.

**Parameters:**
- `content`: HTML content to send.
- `status_code`: HTTP status code (default: 200).
- `headers`: Custom headers (optional).

**Example:**
```python
response.html("<h1>Welcome</h1>", 200)
```

---

**`file(path, filename=None, content_disposition_type="inline")`**
Sends a file as the response.

**Parameters:**
- `path`: Path to the file (string or `Path`).
- `filename`: Custom filename (optional).
- `content_disposition_type`: `"inline"` (display in browser) or `"attachment"` (download).

**Example:**
```python
response.file("/data/report.pdf", filename="Q4-Report.pdf", content_disposition_type="attachment")
```

---

**`stream(iterator, content_type="text/plain")`**
Streams content from an asynchronous iterator.

**Parameters:**
- `iterator`: Asynchronous generator yielding chunks.
- `content_type`: MIME type of the stream (default: `text/plain`).

**Example:**
```python
async def data_streamer():
    yield "Chunk 1"
    yield "Chunk 2"

response.stream(data_streamer(), "text/event-stream")
```

---

**`redirect(url, status_code=302)`**
Redirects to a URL.

**Parameters:**
- `url`: Target URL.
- `status_code`: Redirect status code (default: 302).

**Example:**
```python
response.redirect("/new-location", 301)
```

---

**`status(status_code)`**
Sets the HTTP status code.

**Parameters:**
- `status_code`: Status code (e.g., 200, 404).

**Example:**
```python
response.status(404)
```

---

**`header(key, value)`**
Adds a custom header.

**Parameters:**
- `key`: Header name (case-insensitive).
- `value`: Header value.

**Example:**
```python
response.header("X-API-Version", "1.0")
```

---

**`set_cookie(key, value, max_age=None, expires=None, path="/", domain=None, secure=True, httponly=False, samesite="lax")`**
Sets a cookie.

**Parameters:**
- `key`: Cookie name.
- `value`: Cookie value.
- `max_age`: Max age in seconds (optional).
- `expires`: Expiry datetime (optional).
- `path`: Cookie path (default: `/`).
- `domain`: Domain scope (optional).
- `secure`: HTTPS-only (default: True).
- `httponly`: Prevent client-side JS access (default: False).
- `samesite`: `"lax"`, `"strict"`, or `"none"` (default: `"lax"`).

**Example:**
```python
response.set_cookie("session_id", "abc123", max_age=3600, path="/admin")
```

---

**`delete_cookie(key, path="/", domain=None)`**
Deletes a cookie.

**Parameters:**
- `key`: Cookie name.
- `path`: Cookie path (default: `/`).
- `domain`: Domain scope (optional).

**Example:**
```python
response.delete_cookie("session_id")
```

---

**`cache(max_age=3600, private=True)`**
Enables caching with `Cache-Control` headers.

**Parameters:**
- `max_age`: Cache duration in seconds (default: 3600).
- `private`: `private` (user-specific) or `public` caching (default: True).

**Example:**
```python
response.cache(max_age=86400, private=False)  # Public cache for 24h
```

---

**`no_cache()`**
Disables caching.

**Example:**
```python
response.no_cache()
```

---

**`resp(body="", status_code=200, headers=None, content_type="text/plain")**
Directly configures the underlying `Response` object.

**Parameters:**
- `body`: Raw response body.
- `status_code`: HTTP status code.
- `headers`: Custom headers (optional).
- `content_type`: MIME type (default: `text/plain`).

**Example:**
```python
response.resp(b"Raw Data", 200, content_type="application/octet-stream")
```

---

**funny example**

```py

@app.get("user-data")
async def create_user(request :Request, response :Response) -> None:
   
    user_data = {
            "id": "user_id",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "created_at": datetime.now().isoformat(),
        }
    (response.status(200)  # Set status code
    .json(user_data, indent=4)  # Send JSON response with pretty-printing
    .header("X-User-ID", str("user_id"))  # Add a custom header
    .set_cookie(
        key="last_profile_view",
        value=datetime.now().isoformat(),
        max_age=3600,  # Expires in 1 hour
        path=f"/users/{"user_id"}",  # Cookie only valid for this path
        secure=True,  # HTTPS-only
        httponly=True,  # Prevent client-side JS access
        samesite="strict"  # Strict SameSite policy
    )
    .cache(max_age=300, private=True) )
```

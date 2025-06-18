# Request API Reference

The Request object is a fundamental component in Nexios that provides access to all incoming HTTP request data and utilities. It encapsulates the HTTP request information and provides methods to interact with various aspects of the request.

## Basic Properties

### `method`
```python
request.method  # Returns the HTTP method (GET, POST, etc.)
```
The `method` property returns the HTTP method of the request as a string. This is useful for determining the type of request and implementing method-specific logic.

Example:
```python
@app.route("/users", methods=["GET", "POST"])
async def handle_users(request, response):
    if request.method == "GET":
        return response.json({"users": get_users()})
    elif request.method == "POST":
        return response.json({"message": "User created"})
```

### `url`
```python
request.url  # Returns a URL object containing the full request URL
```
The `url` property returns a URL object that provides access to various components of the request URL. This object is useful for parsing and manipulating URLs.

Example:
```python
@app.get("/redirect")
async def redirect(request, response):
    # Get the full URL
    full_url = str(request.url)
    
    # Get specific URL components
    scheme = request.url.scheme  # http or https
    host = request.url.netloc    # example.com:8080
    path = request.url.path      # /users/42
    query = request.url.query    # Raw query string
```

### `path`
```python
request.path  # Returns the request path as a string
```
The `path` property returns the path portion of the request URL. This is useful for route matching and path-based logic.

Example:
```python
@app.middleware
async def logging_middleware(request, response, next):
    print(f"Request path: {request.path}")
    return await next(request, response)
```

### `headers`
```python
request.headers  # Returns a case-insensitive dictionary of request headers
```
The `headers` property returns a case-insensitive dictionary containing all request headers. This is useful for accessing header information and implementing header-based logic.

Example:
```python
@app.get("/api")
async def api_endpoint(request, response):
    # Check for API key
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return response.json({"error": "API key required"}, 401)
    
    # Check content type
    content_type = request.headers.get("Content-Type")
    if content_type != "application/json":
        return response.json({"error": "Invalid content type"}, 400)
```

### `query_params`
```python
request.query_params  # Returns a dictionary of URL query parameters
```
The `query_params` property returns a dictionary containing all URL query parameters. This is useful for accessing and processing query string data.

Example:
```python
@app.get("/search")
async def search(request, response):
    # Get query parameters with defaults
    query = request.query_params.get("q", "")
    page = int(request.query_params.get("page", "1"))
    limit = int(request.query_params.get("limit", "10"))
    
    # Process search
    results = await search_database(query, page, limit)
    return response.json({"results": results})
```

### `cookies`
```python
request.cookies  # Returns a dictionary of request cookies
```
The `cookies` property returns a dictionary containing all request cookies. This is useful for accessing cookie data and implementing cookie-based features.

Example:
```python
@app.get("/profile")
async def profile(request, response):
    # Get session cookie
    session_id = request.cookies.get("session_id")
    if not session_id:
        return response.json({"error": "Not authenticated"}, 401)
    
    # Get user preferences
    theme = request.cookies.get("theme", "light")
    language = request.cookies.get("language", "en")
```

### `client`
```python
request.client  # Returns a tuple of (host, port) for the client
```
The `client` property returns a tuple containing the client's host and port. This is useful for client identification and logging.

Example:
```python
@app.middleware
async def client_logging_middleware(request, response, next):
    host, port = request.client
    print(f"Request from {host}:{port}")
    return await next(request, response)
```

## Body Content Methods

### `body()`
```python
body = await request.body()  # Returns the raw request body as bytes
```
The `body()` method returns the raw request body as bytes. This is useful when you need to access the raw request data.

Example:
```python
@app.post("/upload")
async def upload(request, response):
    # Get raw body
    body = await request.body()
    
    # Process raw data
    with open("upload.bin", "wb") as f:
        f.write(body)
    
    return response.json({"message": "Upload successful"})
```

### `text()`
```python
text = await request.text()  # Returns the request body as text
```
The `text()` method returns the request body as a string. This is useful for text-based content.

Example:
```python
@app.post("/text")
async def handle_text(request, response):
    # Get text content
    text = await request.text()
    
    # Process text
    word_count = len(text.split())
    return response.json({"word_count": word_count})
```

### `json()`
```python
data = await request.json()  # Returns the parsed JSON request body
```
The `json()` method parses the request body as JSON and returns the resulting Python object. This is useful for handling JSON API requests.

Example:
```python
@app.post("/users")
async def create_user(request, response):
    try:
        # Parse JSON data
        data = await request.json()
        
        # Validate required fields
        if "username" not in data or "email" not in data:
            return response.json({"error": "Missing required fields"}, 400)
        
        # Create user
        user = await create_user_in_db(data)
        return response.json({"user": user})
    except json.JSONDecodeError:
        return response.json({"error": "Invalid JSON"}, 400)
```

## Form Data Methods

### `form()`
```python
form = await request.form()  # Returns a FormData object
```
The `form()` method returns a FormData object containing all form fields. This is useful for handling form submissions.

Example:
```python
@app.post("/register")
async def register(request, response):
    # Get form data
    form = await request.form()
    
    # Get form fields
    username = form.get("username")
    email = form.get("email")
    password = form.get("password")
    
    # Validate form data
    if not all([username, email, password]):
        return response.json({"error": "Missing required fields"}, 400)
    
    # Process registration
    user = await register_user(username, email, password)
    return response.json({"user": user})
```

### `files()`
```python
files = await request.files()  # Returns a dictionary of uploaded files
```
The `files()` method returns a dictionary containing all uploaded files. This is useful for handling file uploads.

Example:
```python
@app.post("/upload")
async def upload_files(request, response):
    # Get uploaded files
    files = await request.files()
    
    # Process each file
    uploaded_files = []
    for field_name, file in files.items():
        # Get file info
        filename = file.filename
        content_type = file.content_type
        content = await file.read()
        
        # Save file
        file_path = f"uploads/{filename}"
        with open(file_path, "wb") as f:
            f.write(content)
        
        uploaded_files.append({
            "field": field_name,
            "filename": filename,
            "content_type": content_type,
            "size": len(content)
        })
    
    return response.json({"files": uploaded_files})
```

## Path Parameters

### `path_params`
```python
params = request.path_params  # Returns a dictionary of path parameters
```
The `path_params` property returns a dictionary containing all path parameters. This is useful for accessing route parameters.

Example:
```python
@app.get("/users/{id}")
async def get_user(request, response):
    # Get path parameter
    user_id = request.path_params["id"]
    
    # Get user
    user = await get_user_by_id(user_id)
    if not user:
        return response.json({"error": "User not found"}, 404)
    
    return response.json({"user": user})
```

## State and Session

### `state`
```python
request.state  # Returns a dictionary for storing request state
```
The `state` property returns a dictionary that can be used to store request-specific state. This is useful for passing data between middleware and handlers.

Example:
```python
@app.middleware
async def auth_middleware(request, response, next):
    # Authenticate user
    user = await authenticate_user(request)
    if user:
        request.state["user"] = user
    return await next(request, response)

@app.get("/profile")
async def profile(request, response):
    # Access state
    user = request.state.get("user")
    if not user:
        return response.json({"error": "Not authenticated"}, 401)
    
    return response.json({"user": user})
```

### `session`
```python
session = request.session  # Returns the session object
```
The `session` property returns the session object. This is useful for managing user sessions.

Example:
```python
@app.post("/login")
async def login(request, response):
    # Get login data
    data = await request.json()
    
    # Authenticate user
    user = await authenticate_user(data)
    if not user:
        return response.json({"error": "Invalid credentials"}, 401)
    
    # Set session data
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    
    return response.json({"message": "Logged in successfully"})
```

## Utility Methods

### `build_absolute_uri()`
```python
url = request.build_absolute_uri("/path")  # Returns an absolute URL
```
The `build_absolute_uri()` method builds an absolute URL from a path. This is useful for generating full URLs.

Example:
```python
@app.get("/redirect")
async def redirect(request, response):
    # Build absolute URL
    url = request.build_absolute_uri("/new-path")
    
    # Redirect
    return response.redirect(url)
```

### `is_disconnected()`
```python
if await request.is_disconnected():  # Returns True if client disconnected
    raise TimeoutError()
```
The `is_disconnected()` method checks if the client has disconnected. This is useful for handling client disconnections.

Example:
```python
@app.get("/stream")
async def stream_data(request, response):
    async def generate():
        for i in range(10):
            if await request.is_disconnected():
                break
            yield f"data: {i}\n\n"
            await asyncio.sleep(1)
    
    return response.stream(generate())
```

### `send_push_promise()`
```python
await request.send_push_promise("/style.css")  # Sends an HTTP/2 push promise
```
The `send_push_promise()` method sends an HTTP/2 push promise. This is useful for optimizing HTTP/2 connections.

Example:
```python
@app.get("/page")
async def page(request, response):
    # Send push promises for resources
    await request.send_push_promise("/style.css")
    await request.send_push_promise("/script.js")
    
    # Return page
    return response.html("<h1>Hello</h1>")
```

## Advanced Features

### Request Validation
```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

@app.post("/users")
async def create_user(request, response):
    try:
        # Parse and validate request data
        data = await request.json()
        user_data = UserCreate(**data)
        
        # Create user
        user = await create_user_in_db(user_data.dict())
        return response.json({"user": user})
    except ValidationError as e:
        return response.json({"error": e.errors()}, 400)
```

### File Upload Handling
```python
@app.post("/upload")
async def upload_file(request, response):
    # Get uploaded files
    files = await request.files()
    
    # Check for file
    if "file" not in files:
        return response.json({"error": "No file uploaded"}, 400)
    
    # Get file
    file = files["file"]
    
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png"]:
        return response.json({"error": "Invalid file type"}, 400)
    
    # Process file
    content = await file.read()
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    return response.json({
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content)
    })
```

### Query Parameter Handling
```python
@app.get("/search")
async def search(request, response):
    # Get query parameters
    query = request.query_params.get("q", "")
    page = int(request.query_params.get("page", "1"))
    limit = int(request.query_params.get("limit", "10"))
    sort = request.query_params.get("sort", "name")
    order = request.query_params.get("order", "asc")
    
    # Validate parameters
    if page < 1:
        return response.json({"error": "Invalid page number"}, 400)
    if limit < 1 or limit > 100:
        return response.json({"error": "Invalid limit"}, 400)
    if sort not in ["name", "date", "popularity"]:
        return response.json({"error": "Invalid sort field"}, 400)
    if order not in ["asc", "desc"]:
        return response.json({"error": "Invalid order"}, 400)
    
    # Perform search
    results = await search_database(
        query=query,
        page=page,
        limit=limit,
        sort=sort,
        order=order
    )
    
    return response.json({
        "results": results,
        "page": page,
        "limit": limit,
        "total": len(results)
    })
```

## Key Notes

1. **Async Access**: Body/form methods are `await`able
2. **Type Safety**: Path/query params convert types (e.g., `{id:int}` → `int`)
3. **File Handling**: Stream large files without memory overload
4. **Extensions**: `state` and `user` require middleware setup
5. **Validation**: Use Pydantic models for request validation
6. **Security**: Always validate and sanitize user input
7. **Performance**: Use streaming for large file uploads
8. **Error Handling**: Implement proper error handling for all operations

### **Common Patterns**

## **JSON API**
```python
@app.post("/data")
async def handle_data(request, response):
    data = await request.json
    return {"received": data}
```

## **Form Submission**
```python
@app.post("/register")
async def register(request, response):
    form = await request.form
    username = form["username"]
    avatar = (await request.files)["avatar"]
    # Process registration...
```

## **Protected Route**
```python
@app.get("/profile")
async def profile(request, response):
    if not request.user:
        raise HTTPException(401)
    return {"user": request.user}
```

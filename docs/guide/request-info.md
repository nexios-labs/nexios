# Request Information in Nexios 

Nexios provides a comprehensive `Request` object that gives you access to all the information about the incoming HTTP request. This object is automatically passed to your route handlers and contains methods and properties to access request data.

## Basic Request Properties

```python
@app.get("/example")
async def example_handler(req: Request, res):
    # Basic request information
    method = req.method        # HTTP method (GET, POST, etc.)
    url = req.url              # Full URL object
    path = req.path            # Request path (/example)
    headers = req.headers      # Headers dictionary
    client_ip = req.client     # Client address (IP, port)
```

## Query Parameters

Access URL query parameters (after the `?` in the URL):

```python
@app.get("/search")
async def search_handler(req: Request, res):
    # For URL: /search?q=nexios&page=2
    query = req.query_params.get("q")       # "nexios"
    page = req.query_params.get("page")     # "2"
    all_params = dict(req.query_params)    # {'q': 'nexios', 'page': '2'}
```

## Path Parameters

Access named parameters from the route path:

```python
@app.get("/users/{user_id}")
async def user_handler(req: Request, res):
    # For URL: /users/123
    user_id = req.path_params["user_id"]  # "123"
    # Or directly as function parameter (shown above)
```

##  Request Body

### JSON Data

```python
@app.post("/data")
async def data_handler(req: Request, res):
    json_data = await req.json  # Parses JSON body
```

### Form Data

```python
@app.post("/submit")
async def submit_handler(req: Request, res):
    form_data = await req.form  # Parses both URL-encoded and multipart forms
    username = form_data.get("username")
```

### File Uploads

```python
@app.post("/upload")
async def upload_handler(req: Request, res):
    files = await req.files      # Dictionary of uploaded files
    file = files.get("document") # Access specific file
    if file:
        filename = file.filename
        content = await file.read()
```

### Raw Body

```python
@app.post("/raw")
async def raw_handler(req: Request, res):
    body_bytes = await req.body  # Raw bytes
    body_text = await req.text  # Decoded text
```

## Cookies

```python
@app.get("/profile")
async def profile_handler(req: Request, res):
    session_id = req.cookies.get("session_id")
```

## Client Information

```python
@app.get("/client-info")
async def client_info_handler(req: Request, res):
    user_agent = req.user_agent
    client_ip = req.client.host if req.client else None
    origin = req.origin
```

## State and Middleware Data

```python
@app.get("/auth")
async def auth_handler(req: Request, res):
    # Access data added by middleware
    user = req.user
    session = req.session  # Requires session middleware
    custom_data = req.state.get("custom_data")
```

## URL Construction

```python
@app.get("/links")
async def links_handler(req: Request, res):
    absolute_url = req.build_absolute_uri("/api/resource")
    # Returns full URL like "https://example.com/api/resource"
```

## Request Validation

```python
@app.post("/validate")
async def validate_handler(req: Request, res):
    if not req.valid():
        return res.status(400).text("Invalid request")
```

## Advanced Features

### Streaming Requests

For handling large uploads:

```python
@app.post("/stream")
async def stream_handler(req: Request, res):
    async for chunk in req.stream():
        # Process each chunk of the request body
        process_chunk(chunk)
```

### Server Push

```python
@app.get("/push")
async def push_handler(req: Request, res):
    await req.send_push_promise("/static/style.css")
```

The Nexios `Request` object provides a rich interface for working with incoming HTTP requests, with support for all common web standards and convenient access to request data. 
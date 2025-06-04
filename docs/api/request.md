

### **Request API Reference**

## **Basic Properties**
```python
# Access request data
request.method          # "GET", "POST", etc
request.url             # Full URL object
request.path            # "/users/42"
request.headers         # Case-insensitive dict
request.query_params    # URL query parameters
request.cookies         # Dict of cookies
request.client          # (host, port) tuple
```

## **Body Content**
```python
# Read body content
body = await request.body      # Raw bytes
text = await request.text      # Decoded text
data = await request.json      # Parsed JSON

# Example: JSON API handler
@app.post("/users")
async def create_user(request, response):
    user_data = await request.json
    return {"id": 42, **user_data}
```

## **Form Data**
```python
# Handle forms
form = await request.form      # FormData object
name = form["username"]          # Form field

# File uploads
files = await request.files      # Dict of uploaded files
file = files["avatar"]           # File object
filename = file.filename         # Original filename
content = await file.read()      # File content
```

## **Advanced Features**
```python
# Path parameters (from route /users/{id})
user_id = request.path_params["id"]

# State storage (middleware to handler)
request.state.user = current_user

# Session handling (requires middleware)
session = request.session
session["user_id"] = 42

# User authentication (requires middleware)
user = request.user  # None or authenticated user
```

## **Utility Methods**
```python
# Build absolute URLs
url = request.build_absolute_uri("/profile")

# Check connection status
if await request.is_disconnected():
    raise TimeoutError()

# HTTP/2 Server Push
await request.send_push_promise("/style.css")
```

---

## **Key Notes**
1. **Async Access**: Body/form methods are `await`able
2. **Type Safety**: Path/query params convert types (e.g., `{id:int}` → `int`)
3. **File Handling**: Stream large files without memory overload
4. **Extensions**: `state` and `user` require middleware setup

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

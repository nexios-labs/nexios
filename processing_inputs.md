# Processing Inputs in Nexios

In Nexios, processing inputs from HTTP requests is a fundamental aspect of building web applications. This document provides an overview of how to handle and process various types of inputs, such as JSON data, form data, files, and streaming request data.

## Handling JSON Data

To handle JSON data in a request, you can use the `json` property of the `Request` object. This property asynchronously parses the request body as JSON and returns it as a dictionary.

**Example**

```python
from nexios import get_application

app = get_application()

@app.post("/submit")
async def submit_data(req, res):
    data = await req.json
    return res.json({"received": data})
```

Explanation

- **Request Parsing**: The `req.json` property is used to parse the incoming request body as JSON.
- **Response**: The parsed data is then returned in the response as a JSON object.

## Handling Form Data

Nexios provides built-in support for parsing form data, including `multipart/form-data` and `application/x-www-form-urlencoded`. You can access the parsed form data using the `form_data` property of the `Request` object.

**Example**

```python
@app.post("/submit-form")
async def submit_form(req, res):
    form_data = await req.form_data
    return res.json({"received": form_data})
```

Explanation

- **Form Data Parsing**: The `req.form_data` property is used to parse the form data from the request.
- **Response**: The parsed form data is returned in the response as a JSON object.

## Handling File Uploads

When handling file uploads, the `form_data` property also provides access to the uploaded files. You can iterate over the form data to extract files.

**Example**

```python
@app.post("/upload")
async def upload_file(req, res):
    files = await req.files
    for name, file in files.items():
        # Process the uploaded file
        pass
    return res.json({"status": "files received"})
```

- **File Parsing**: The `req.files` property is used to access the uploaded files.
- **File Processing**: Iterate over the files and process them as needed.
- **Response**: A status message is returned indicating the files were received.

## Handling Streaming Request Data

For large payloads or real-time data, you might need to handle streaming request data. Nexios supports streaming data using the `req.stream` property.

**Example**

```python
@app.post("/stream")
async def stream_data(req, res):
    data = b""
    async for chunk in req.stream():
        data += chunk
    print(data.decode())
    return res.json({"status": "stream received"})
```

- **Streaming Data**: The `req.stream` property allows you to process incoming data in chunks.
- **Chunk Processing**: Handle each chunk of data as it arrives and accumulate it.
- **Response**: A status message is returned indicating the stream was received.

## Validating Inputs

Nexios integrates with Pydantic for input validation. You can define Pydantic models to validate and parse request data.

**Example**

```python
from pydantic import BaseModel, EmailStr, ValidationError

class UserSchema(BaseModel):
    name: str
    email: EmailStr

@app.post("/create-user")
async def create_user(req, res):
    try:
        user_data = await req.json
        user = UserSchema(**user_data)
        return res.json({"user": user.dict()})
    except ValidationError as e:
        return res.json({"error": e.errors()}, status_code=422)
```

- **Pydantic Model**: Define a Pydantic model for input validation.
- **Request Parsing**: Parse the request data using the Pydantic model.
- **Error Handling**: Handle validation errors and return appropriate responses.

## Middleware for Input Processing

Middleware can be used to process inputs before they reach the route handler. For example, you can use middleware to log requests or validate authentication tokens.

**Example**

```python
async def log_request(req, res, next):
    print(f"Received request: {req.method} {req.path}")
    await next()

app.add_middleware(log_request)
```

- **Logging Middleware**: A middleware function to log incoming requests.
- **Middleware Registration**: Register the middleware with the application.

## Example Application

Here is a complete example of a Nexios application that processes different types of inputs:

**Example**

```python
from nexios import get_application
from pydantic import BaseModel, EmailStr, ValidationError

app = get_application()

class UserSchema(BaseModel):
    name: str
    email: EmailStr

@app.post("/submit")
async def submit_data(req, res):
    data = await req.json
    return res.json({"received": data})

@app.post("/submit-form")
async def submit_form(req, res):
    form_data = await req.form_data
    return res.json({"received": form_data})

@app.post("/upload")
async def upload_file(req, res):
    files = await req.files
    for name, file in files.items():
        # Process the uploaded file
        pass
    return res.json({"status": "files received"})

@app.post("/create-user")
async def create_user(req, res):
    try:
        user_data = await req.json
        user = UserSchema(**user_data)
        return res.json({"user": user.dict()})
    except ValidationError as e:
        return res.json({"error": e.errors()}, status_code=422)

@app.post("/stream")
async def stream_data(req, res):
    data = b""
    async for chunk in req.stream():
        data += chunk
    print(data.decode())
    return res.json({"status": "stream received"})

async def log_request(req, res, next):
    print(f"Received request: {req.method} {req.path}")
    await next()

app.add_middleware(log_request)
```

- **Application Setup**: Initialize the Nexios application.
- **Route Handlers**: Define route handlers for different types of inputs.
- **Middleware**: Add middleware for logging requests.

## Tips

- **Error Handling**: Always handle potential errors, especially when dealing with external inputs.
- **Security**: Validate and sanitize inputs to prevent security vulnerabilities like SQL injection and XSS.
- **Performance**: For large payloads, consider using streaming to handle data efficiently. Processing Inputs in Nexios


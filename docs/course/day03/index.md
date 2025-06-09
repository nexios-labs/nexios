# Day 3: Request Handling & Responses

Welcome to Day 3! Today we'll dive deep into handling different types of requests and crafting various responses in Nexios.

## Request Handling

### 1. Request Properties

```python
from nexios import NexiosApp
from nexios.http import Request, Response

app = NexiosApp()

@app.get("/request-info")
async def request_info(request: Request, response: Response):
    return response.json({
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "client": {
            "host": request.client.host,
            "port": request.client.port
        }
    })
```

### 2. JSON Data

```python
@app.post("/api/json")
async def handle_json(request: Request, response: Response):
    data = await request.json()
    return response.json({
        "received": data,
        "type": "json"
    })
```

### 3. Form Data

```python
@app.post("/api/form")
async def handle_form(request: Request, response: Response):
    form = await request.form()
    return response.json({
        "form_data": dict(form),
        "type": "form"
    })
```

### 4. File Uploads

```python
import uuid
from pathlib import Path

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/api/upload")
async def handle_upload(request: Request, response: Response):
    files = await request.files()
    if not files:
        return response.json(
            {"error": "No files uploaded"}, 
            status_code=400
        )
    
    results = []
    for file_field, file in files.items():
        # Generate safe filename
        ext = Path(file.filename).suffix
        safe_filename = f"{uuid.uuid4()}{ext}"
        
        # Save file
        file_path = UPLOAD_DIR / safe_filename
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        results.append({
            "original_name": file.filename,
            "saved_as": safe_filename,
            "content_type": file.content_type,
            "size": len(content)
        })
    
    return response.json({
        "message": f"Successfully uploaded {len(results)} files",
        "files": results
    })
```

### 5. Streaming Request Data

```python
@app.post("/api/stream")
async def handle_stream(request: Request, response: Response):
    total_bytes = 0
    async for chunk in request.stream():
        # Process each chunk
        total_bytes += len(chunk)
    
    return response.json({
        "bytes_received": total_bytes,
        "type": "stream"
    })
```

## Response Types

### 1. JSON Response

```python
@app.get("/responses/json")
async def json_response(request: Request, response: Response):
    return response.json({
        "message": "Hello, World!",
        "numbers": [1, 2, 3],
        "nested": {
            "key": "value"
        }
    })
```

### 2. Text Response

```python
@app.get("/responses/text")
async def text_response(request: Request, response: Response):
    return response.text("Hello, World!")
```

### 3. HTML Response

```python
@app.get("/responses/html")
async def html_response(request: Request, response: Response):
    html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Nexios Example</title>
        </head>
        <body>
            <h1>Hello from Nexios!</h1>
            <p>This is a HTML response.</p>
        </body>
    </html>
    """
    return response.html(html)
```

### 4. File Response

```python
@app.get("/responses/file/{filename}")
async def file_response(request: Request, response: Response):
    filename = request.path_params["filename"]
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        return response.json(
            {"error": "File not found"}, 
            status_code=404
        )
    
    return response.file(
        file_path,
        filename=filename,
        content_disposition_type="attachment"
    )
```

### 5. Streaming Response

```python
import asyncio

@app.get("/responses/stream")
async def stream_response(request: Request, response: Response):
    async def number_generator():
        for i in range(10):
            yield f"Number: {i}\n"
            await asyncio.sleep(1)
    
    return response.stream(
        number_generator(),
        content_type="text/plain"
    )
```

## Custom Response Headers

```python
@app.get("/responses/custom-headers")
async def custom_headers(request: Request, response: Response):
    return response.json(
        {"message": "Hello"},
        headers={
            "X-Custom-Header": "Custom Value",
            "X-Response-Time": "1ms"
        }
    )
```

## Status Codes

```python
@app.get("/responses/status")
async def status_codes(request: Request, response: Response):
    status = request.query_params.get("code", "200")
    
    return response.json(
        {"message": f"Status code: {status}"},
        status_code=int(status)
    )
```

## Exercises

1. **File Upload System**:
   Create a complete file upload system with:
   - Multiple file upload support
   - File type validation
   - Size limits
   - Progress tracking
   - File listing and management

2. **Streaming Data Handler**:
   Implement a streaming data handler that:
   - Accepts large data streams
   - Processes data in chunks
   - Provides progress updates
   - Handles errors gracefully

3. **Response Types**:
   Create endpoints that demonstrate:
   - CSV file generation
   - PDF file generation
   - Image manipulation
   - ZIP file creation

## Mini-Project: File Sharing API

Create a simple file sharing API with the following features:

```python
from nexios import NexiosApp
from nexios.http import Request, Response
from pathlib import Path
import uuid
import shutil
import mimetypes

app = NexiosApp()

# Configure storage
STORAGE_DIR = Path("storage")
STORAGE_DIR.mkdir(exist_ok=True)

# Store file metadata
files_db = {}

@app.post("/files/upload")
async def upload_file(request: Request, response: Response):
    files = await request.files
    if not files:
        return response.json(
            {"error": "No file uploaded"}, 
            status_code=400
        )
    
    results = []
    for file_field, file in files.items():
        # Generate unique ID and safe filename
        file_id = str(uuid.uuid4())
        ext = Path(file.filename).suffix
        safe_filename = f"{file_id}{ext}"
        
        # Save file
        file_path = STORAGE_DIR / safe_filename
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Store metadata
        files_db[file_id] = {
            "id": file_id,
            "original_name": file.filename,
            "saved_as": safe_filename,
            "content_type": file.content_type,
            "size": len(content)
        }
        
        results.append(files_db[file_id])
    
    return response.json({
        "message": "Files uploaded successfully",
        "files": results
    })

@app.get("/files")
async def list_files(request: Request, response: Response):
    return response.json({
        "files": list(files_db.values())
    })

@app.get("/files/{file_id}")
async def get_file(request: Request, response: Response):
    file_id = request.path_params["file_id"]
    file_info = files_db.get(file_id)
    
    if not file_info:
        return response.json(
            {"error": "File not found"}, 
            status_code=404
        )
    
    file_path = STORAGE_DIR / file_info["saved_as"]
    return response.file(
        file_path,
        filename=file_info["original_name"],
        content_disposition_type="attachment"
    )

@app.delete("/files/{file_id}")
async def delete_file(request: Request, response: Response):
    file_id = request.path_params["file_id"]
    file_info = files_db.get(file_id)
    
    if not file_info:
        return response.json(
            {"error": "File not found"}, 
            status_code=404
        )
    
    file_path = STORAGE_DIR / file_info["saved_as"]
    file_path.unlink(missing_ok=True)
    del files_db[file_id]
    
    return response.json({
        "message": "File deleted successfully"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000, reload=True)
```

## Key Concepts Learned

- Request properties and methods
- Handling different request types
- File upload handling
- Streaming data
- Various response types
- Custom headers
- Status codes
- File handling and storage

## Additional Resources

- [Request Handling Guide](https://nexios.dev/guide/request)
- [Response Types Documentation](https://nexios.dev/guide/response)
- [File Upload Tutorial](https://nexios.dev/guide/file-upload)
- [Streaming Data Guide](https://nexios.dev/guide/streaming)

## Homework

1. Add features to the File Sharing API:
   - File expiration
   - Access controls
   - File sharing links
   - File preview

2. Create a real-time file upload progress tracker:
   - Upload progress
   - Cancel upload
   - Resume upload
   - Chunk upload

3. Read about:
   - WebSocket responses
   - Server-Sent Events
   - File compression
   - Content negotiation

## Next Steps

Tomorrow, we'll explore path and query parameters in detail in [Day 4: Path & Query Parameters](../day04/index.md). 